import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning


def get_response_from_link(link: str, params: dict) -> requests.models.Response:
    link_response = requests.get(
        link, params=params, verify=False, allow_redirects=False
    )
    link_response.raise_for_status()
    return link_response


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
        for vacancie_item in hh_link_response.json().get("items"):
            print(vacancie_item.get("salary"))
    print(number_vacancies)


if __name__ == "__main__":
    main()
