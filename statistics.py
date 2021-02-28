import pprint
from itertools import count
from typing import Union

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_response_from_link(link: str, params: dict) -> requests.models.Response:
    link_response = requests.get(
        link, params=params, verify=False, allow_redirects=False
    )
    link_response.raise_for_status()
    return link_response


def predict_rub_salary(vacancy: dict) -> Union[int, None]:
    salary_description = vacancy.get("salary")
    if salary_description:
        salary_from = salary_description.get("from")
        salary_to = salary_description.get("to")
        if salary_from and salary_to:
            return (salary_from + salary_to) / 2
        if salary_from and not salary_to:
            return salary_from * 1.2
        if not salary_from and salary_to:
            return salary_to * 0.8
    return None


def predict_average_salary(api_link: str, request_params: dict) -> dict:
    print(request_params.get("text"))
    average_salary = 0
    vacancy_salary_average_sum = 0
    vacancies_processed = 0
    items_limit = 2000 - request_params.get("per_page", 0)
    for page in count():
        request_params["page"] = page
        page_response = get_response_from_link(api_link, request_params)
        page_response.raise_for_status()
        page_content = page_response.json()
        items = page * page_content.get("per_page")
        if page >= page_content.get("pages") or items >= items_limit:
            break
        for vacancy in page_content.get("items"):
            salary_vacancy_average = predict_rub_salary(vacancy)
            if salary_vacancy_average:
                vacancy_salary_average_sum += salary_vacancy_average
                vacancies_processed += 1
        print("page", page, end="\r")
    average_salary = int(vacancy_salary_average_sum / vacancies_processed)
    return {
        "vacancies_found": page_content.get("found"),
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    salary_languages = {}
    hh_api_link = "https://api.hh.ru/vacancies"
    hh_params = {
        "area": 1,
        "period": 30,
        "per_page": 20,
    }
    programming_language_range = {
        "JavaScript": "программист JavaScript",
        "Java": "программист Java",
        "Python": "программист Python",
        "Ruby": "программист Ruby",
        "PHP": "программист PHP",
        "C++": "программист C++",
        "Swift": "программист Swift",
        "C#": "программист C#",
        "Scala": "программист Scala",
        "Go": "программист Go",
    }
    for programming_language in programming_language_range:
        hh_params["text"] = programming_language_range.get(programming_language)
        salary_languages[programming_language] = predict_average_salary(
            hh_api_link, hh_params
        )
    pprint.pprint(salary_languages)


if __name__ == "__main__":
    main()
