import requests
import bs4
import json
from fake_headers import Headers
from pprint import pprint
from tqdm import tqdm

def get_fake_headers():
    return Headers(browser="opera", os="win").generate()

response = requests.get("https://spb.hh.ru/search/vacancy?text=python&area=1&area=2",
                         headers=get_fake_headers())
main_page_data = bs4.BeautifulSoup(response.text, features="lxml")

main_vacancy_content = main_page_data.find("main", class_="vacancy-serp-content")
div_tags = main_vacancy_content.findAll("div", class_="vacancy-serp-item-body")


def find_job(tag):
    final_list = []

    for div_tag in tqdm(tag):
        link = div_tag.find("a", class_="bloko-link")["href"]
        
        if link:
            response = requests.get(link, headers=get_fake_headers())
            vacancy = bs4.BeautifulSoup(response.text, features="lxml")
            vacancy_desc = vacancy.find("div", class_="vacancy-description")
            vacancy_desc_text = " ".join(vacancy_desc.text.split()).lower()
            
            if ("django" or "flask") in vacancy_desc_text:
                name_vac = div_tag.find("span", class_="serp-item__title-link serp-item__title").text
                salary = div_tag.find("span", class_="bloko-header-section-2")
                name_company = div_tag.find("div", class_="bloko-text").text
                city = div_tag.find("div", {"data-qa":"vacancy-serp__vacancy-address"}).text
               
                if salary == None:
                    salary = "зарплата не указана"
                else:
                    salary = salary.text
                
                vacancy_data = {
                "вакансия": name_vac,
                "ссылка": link,
                "зп": salary,
                "название компании": name_company,
                "город": city
            }
                final_list.append(vacancy_data)
    return final_list

def record_json(some_list):
    with open("job.json", "w", encoding="utf-8") as f:
        json.dump(some_list, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    final_list = find_job(div_tags)
    record_json(final_list)