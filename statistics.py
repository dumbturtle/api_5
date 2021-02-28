import pprint
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


def predict_average_salary(vacancies: list) -> dict:
    average_salary = 0
    vacancies_processed = 0
    for vacancy in vacancies:
        salary_vacancy_average = predict_rub_salary(vacancy)
        if salary_vacancy_average:
            average_salary += salary_vacancy_average
            vacancies_processed += 1
    average_salary = average_salary / vacancies_processed
    return {
        "vacancies_processed": vacancies_processed,
        "average_salary": int(average_salary),
    }


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    salary_languages = {}
    hh_api_link = "https://api.hh.ru/vacancies"
    hh_params = {
        "area": 1,
        "period": 30,
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
        hh_link_response = get_response_from_link(hh_api_link, hh_params)
        vacancy_items = hh_link_response.json().get("items")
        salary_languages[programming_language] = predict_average_salary(vacancy_items)
        salary_languages[programming_language][
            "vacancies_found"
        ] = hh_link_response.json().get("found")
    pprint.pprint(salary_languages)


if __name__ == "__main__":
    main()
