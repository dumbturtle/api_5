import os
from itertools import count
from typing import Dict, List, Optional

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
    page_content = {"pages": 100}
    for page in count():
        if page >= page_content["pages"]:
            break
        request_params["page"] = page
        page_response = get_response_from_link(api_link, params=request_params)
        page_content = page_response.json()
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
    if not vacancies_processed == 0:
        average_salary = int(summation_result_salary / vacancies_processed)
    return {
        "vacancies_processed": vacancies_processed,
        "average_salary": average_salary,
    }


def collect_hh_all_statistic(programming_language_range: Dict, api_link: str) -> List:
    hh_statistic = []
    hh_params = {
        "area": 1,
        "period": 30,
        "per_page": 20,
    }
    for programming_language in programming_language_range:
        hh_params["text"] = programming_language_range.get(programming_language)
        hh_language_salary = predict_average_salary_for_hh(api_link, hh_params)
        hh_statistic.append(
            [
                programming_language,
                hh_language_salary.get("vacancies_found"),
                hh_language_salary.get("vacancies_processed"),
                hh_language_salary.get("average_salary"),
            ]
        )
    return hh_statistic


def collect_superjob_all_statistic(
    programming_language_range: Dict, api_link: str
) -> List:
    superjob_statistic = []
    superjob_headers = {
        "X-Api-App-Id": os.environ["SUPERJOB_API_KEY"],
    }
    superjob_params = {
        "town": 4,
    }
    for programming_language in programming_language_range:
        superjob_params["keyword"] = programming_language_range.get(
            programming_language
        )
        superjob_language_salary = predict_average_salary_for_superjob(
            api_link, superjob_params, superjob_headers
        )
        superjob_statistic.append(
            [
                programming_language,
                superjob_language_salary.get("vacancies_found"),
                superjob_language_salary.get("vacancies_processed"),
                superjob_language_salary.get("average_salary"),
            ]
        )
    return superjob_statistic


def create_table(content: List, title: str) -> AsciiTable.table:
    table_structure = [
        "Язык программирования",
        "Вакансий найдено",
        "Вакансий обработано",
        "Средняя зарплата",
    ]
    table_content = [table_structure] + content
    return AsciiTable(table_content, title).table


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    load_dotenv()
    hh_api_link = os.environ["HH_API_LINK"]
    superjob_api_link = os.environ["SUPERJOB_API_LINK"]
    hh_title = "HeadHunter Moscow"
    superjob_title = "SuperJob Moscow"
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
    try:
        hh_all_statistic = collect_hh_all_statistic(
            programming_language_range, hh_api_link
        )
        superjob_all_statistic = collect_superjob_all_statistic(
            programming_language_range, superjob_api_link
        )
        hh_termial_table = create_table(hh_all_statistic, hh_title)
        superjob_terminal_table = create_table(superjob_all_statistic, superjob_title)
        print(hh_termial_table)
        print()
        print(superjob_terminal_table)
    except (requests.ConnectionError, requests.HTTPError):
        print("Что-то пошло не так. Проверьте соединение с интернетом.")


if __name__ == "__main__":
    main()
