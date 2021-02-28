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
    hh_api_link = "https://api.hh.ru/vacancies"
    hh_params = {
        "text": "программист",
        "area": 1,
        "period": 30,
    }
    hh_link_response = get_response_from_link(hh_api_link, hh_params)
    print(hh_link_response.json().get("found"))


if __name__ == "__main__":
    main()
