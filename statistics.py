import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from typing import Union


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


def main():
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
    number_vacancies = {}
    hh_api_link = "https://api.hh.ru/vacancies"
    hh_params = {
        "area": 1,
        "period": 30,
    }
    programming_language_range = {
        # "JavaScript": "программист JavaScript",
        # "Java": "программист Java",
        "Python": "программист Python",
        # "Ruby": "программист Ruby",
        # "PHP": "программист PHP",
        # "C++": "программист C++",
        # "Swift": "программист Swift",
        # "C#": "программист C#",
        # "Scala": "программист Scala",
        # "Go": "программист Go",
    }
    for programming_language in programming_language_range:
        hh_params["text"] = programming_language_range.get(programming_language)
        hh_link_response = get_response_from_link(hh_api_link, hh_params)
        number_vacancies[programming_language] = hh_link_response.json().get("found")
        for vacancy_item in hh_link_response.json().get("items"):
            print(vacancy_item.get("salary"))
            print(predict_rub_salary(vacancy_item))
    print(number_vacancies)


if __name__ == "__main__":
    main()
