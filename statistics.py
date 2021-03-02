import os
import pprint
from itertools import count
from typing import Union

import requests
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_response_from_link(
    link: str, params: dict, headers: dict = {}
) -> requests.models.Response:
    link_response = requests.get(
        link, params=params, verify=False, allow_redirects=False, headers=headers
    )
    link_response.raise_for_status()
    return link_response


def predict_salary(
    salary_from: Union[int, None], salary_to: Union[int, None]
) -> Union[int, None]:
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from and not salary_to:
        return salary_from * 1.2
    if not salary_from and salary_to:
        return salary_to * 0.8
    return None


def predict_rub_salary_for_hh(vacancy: dict) -> Union[int, None]:
    salary_description = vacancy.get("salary")
    if salary_description:
        salary_from = salary_description.get("from")
        salary_to = salary_description.get("to")
        return predict_salary(salary_from, salary_to)
    return None


def predict_rub_salary_for_superjob(vacancy: dict) -> Union[int, None]:
    salary_from = vacancy.get("payment_from")
    salary_to = vacancy.get("payment_to")
    return predict_salary(salary_from, salary_to)


def predict_average_salary_for_hh(api_link: str, request_params: dict) -> dict:
    print("HH",request_params.get("text"))
    salary_vacancy_average = []
    items_limit = 2000 - request_params.get("per_page", 0)
    for page in count():
        print(page, end='\r')
        request_params["page"] = page
        page_response = get_response_from_link(api_link, params=request_params)
        page_content = page_response.json()
        items = page * page_content.get("per_page")
        if page >= page_content.get("pages") or items >= items_limit:
            break
        salary_vacancy_average += [
            predict_rub_salary_for_hh(vacancy) for vacancy in page_content.get("items")
        ]
    average_salary = calculation_average_salary_for_all_vacancies(
            salary_vacancy_average
        )
    average_salary["vacancies_found"] = page_content.get("found")
    return average_salary


def predict_average_salary_for_superjob(
    api_link: str, request_params: dict, request_headers: dict
) -> dict:
    print("SJ", request_params.get("keyword"))
    page_response = get_response_from_link(
        api_link, params=request_params, headers=request_headers
    )
    page_content = page_response.json()
    salary_vacancy_average = [
        predict_rub_salary_for_superjob(vacancy)
        for vacancy in page_content.get("objects")
    ]
    average_salary = calculation_average_salary_for_all_vacancies(
        salary_vacancy_average
    )
    average_salary["vacancies_found"] = page_content.get("total")
    return average_salary


def calculation_average_salary_for_all_vacancies(salary_range: list) -> dict:
    average_salary = 0
    salary_range_filtered = list(filter(None, salary_range))
    vacancy_salary_sum = sum(salary_range_filtered)
    vacancies_processed = len(salary_range_filtered)
    if not (vacancy_salary_sum or vacancies_processed) == 0:
        average_salary = int(vacancy_salary_sum / vacancies_processed)
    return {
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    load_dotenv()
    hh_language_salary = {}
    superjob_language_salary = {}
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
    hh_api_link = os.environ["HH_API_LINK"]
    hh_params = {
        "area": 1,
        "period": 30,
        "per_page": 20,
    }
    superjob_api_link = os.environ["SUPERJOB_API_LINK"]
    superjob_headers = {
        "X-Api-App-Id": os.environ["SUPERJOB_API_KEY"],
    }
    superjob_params = {
        "town": 4,
    }
    for programming_language in programming_language_range:
        hh_params["text"] = programming_language_range.get(programming_language)
        superjob_params["keyword"] = programming_language_range.get(
            programming_language
        )
        superjob_language_salary[
            programming_language
        ] = predict_average_salary_for_superjob(
            superjob_api_link, superjob_params, superjob_headers
        )
        hh_language_salary[programming_language] = predict_average_salary_for_hh(
            hh_api_link, hh_params
        )
    pprint.pprint(superjob_language_salary)
    pprint.pprint(hh_language_salary)


if __name__ == "__main__":
    main()
