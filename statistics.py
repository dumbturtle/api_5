import os
from itertools import count
from typing import Optional, List, Dict

import requests
from dotenv import load_dotenv
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from terminaltables import AsciiTable


def get_response_from_link(
    link: str, params: Dict, headers: Dict = {}
) -> requests.models.Response:
    link_response = requests.get(
        link, params=params, verify=False, allow_redirects=False, headers=headers
    )
    link_response.raise_for_status()
    return link_response


def predict_salary(
    salary_from: Optional[int], salary_to: Optional[int]
) -> Optional[float]:
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    if salary_from and not salary_to:
        return salary_from * 1.2
    if not salary_from and salary_to:
        return salary_to * 0.8
    return None


def predict_rub_salary_for_hh(vacancy: Dict) -> Optional[float]:
    salary_description = vacancy.get("salary")
    if not salary_description:
        return None
    salary_from = salary_description.get("from")
    salary_to = salary_description.get("to")
    return predict_salary(salary_from, salary_to)
    

def predict_rub_salary_for_superjob(vacancy: Dict) -> Optional[float]:
    salary_from = vacancy.get("payment_from")
    salary_to = vacancy.get("payment_to")
    return predict_salary(salary_from, salary_to)


def predict_average_salary_for_hh(api_link: str, request_params: Dict) -> Dict:
    range_average_salaries = []
    items_limit = 2000 - request_params.get("per_page", 0)
    for page in count():
        request_params["page"] = page
        page_response = get_response_from_link(api_link, params=request_params)
        page_content = page_response.json()
        items = page * page_content.get("per_page")
        if page >= page_content.get("pages") or items >= items_limit:
            break
        range_average_salaries += [
            predict_rub_salary_for_hh(vacancy) for vacancy in page_content.get("items")
        ]
    average_salaries = calculate_average_salary_for_all_vacancies(
        range_average_salaries
    )
    average_salaries["vacancies_found"] = page_content.get("found")
    return average_salaries


def predict_average_salary_for_superjob(
    api_link: str, request_params: Dict, request_headers: Dict
) -> Dict:
    page_response = get_response_from_link(
        api_link, params=request_params, headers=request_headers
    )
    page_content = page_response.json()
    range_average_salaries = [
        predict_rub_salary_for_superjob(vacancy)
        for vacancy in page_content.get("objects")
    ]
    average_salaries = calculate_average_salary_for_all_vacancies(
        range_average_salaries
    )
    average_salaries["vacancies_found"] = page_content.get("total")
    return average_salaries


def calculate_average_salary_for_all_vacancies(salary_range: List) -> Dict:
    average_salary = 0
    filtered_range_salaries: List[float] = list(filter(None, salary_range))
    summation_result_salary = sum(filtered_range_salaries)
    vacancies_processed = len(filtered_range_salaries)
    if not (salary_sum or vacancies_processed) == 0:
        average_salary = int(summation_result_salary / vacancies_processed)
    return {
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    load_dotenv()
    hh_language_salary = {}
    superjob_language_salary = {}
    hh_table_content = []
    superjob_table_content = []
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
    hh_title = "HeadHunter Moscow"
    superjob_title = "SuperJob Moscow"
    table_structure = [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата",
    ]
    hh_table_content.append(table_structure)
    superjob_table_content.append(table_structure)
    try:
        for programming_language in programming_language_range:
            hh_params["text"] = programming_language_range.get(programming_language)
            superjob_params["keyword"] = programming_language_range.get(
                programming_language
            )

            superjob_language_salary = predict_average_salary_for_superjob(
                superjob_api_link, superjob_params, superjob_headers
            )
            superjob_table_content.append(
                [
                    programming_language,
                    superjob_language_salary.get("vacancies_found"),
                    superjob_language_salary.get("vacancies_processed"),
                    superjob_language_salary.get("average_salary"),
                ]
            )

            hh_language_salary = predict_average_salary_for_hh(hh_api_link, hh_params)
            hh_table_content.append(
                [
                    programming_language,
                    hh_language_salary.get("vacancies_found"),
                    hh_language_salary.get("vacancies_processed"),
                    hh_language_salary.get("average_salary"),
                ]
            )
        print(AsciiTable(hh_table_content, hh_title).table)
        print(AsciiTable(superjob_table_content, superjob_title).table)
    except (requests.ConnectionError, requests.HTTPError):
        print("Что-то пошло не так. Проверьте соединение с интернетом.")


if __name__ == "__main__":
    main()
