from itertools import count
import os
import requests
from dotenv import load_dotenv
from create_table import create_vacancies_table

IT_LANGUAGES = [
    'Python',
    'JavaScript',
    'C++',
    'PHP',
    'C#',
    'Java'
]


class GetVacanciesError(Exception):
    def __init__(self, response, message='Error getting vacancies'):
        self.response = response
        self.message = message
        super().__init__(self.message)


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 1.8
    return None


def fetch_hh_vacancies(language):
    max_per_page = 100
    hh_url = "https://api.hh.ru/vacancies/"
    params = {
        "text": f"Программист {language}",
        "per_page": max_per_page,
        "currency": "RUR",
        "city": "Москва"
    }
    all_vacancies = []
    max_page = 20
    vacancies_found = 0
    for page in range(max_page):
        params["page"] = page
        response = requests.get(hh_url, params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if response.status_code == 400:
                print(f"Bad request occurred. Exiting pagination loop.")
                break
            else:
                raise ex
        response = response.json()
        vacancies = response.get("items", [])
        if not vacancies:
            break
        all_vacancies.extend(vacancies)
        vacancies_found = response.get("found", 0)
    return all_vacancies, vacancies_found


def calculate_average_salary_hh(vacancies):
    total_salary = 0
    vacancies_count = 0
    for vacancy in vacancies:
        salary = vacancy.get("salary")
        if not salary:
            continue
        salary_from = salary.get("from")
        salary_to = salary.get("to")
        salary = predict_rub_salary(salary_from, salary_to)
        if salary:
            total_salary += salary
            vacancies_count += 1
    average_salary = total_salary / vacancies_count
    return vacancies_count, average_salary


def fetch_superjob_vacancies(language):
    sj_url = "https://api.superjob.ru/2.0/vacancies/"
    secret_key = os.environ["SECRET_KEY"]
    params = {
        "keyword": f"Программист {language}",
        "town": "Москва"
    }
    headers = {
        "X-Api-App-Id": secret_key,
    }
    all_vacancies = []
    vacancies_found = 0
    for page in count(0):
        params['page'] = page
        response = requests.get(sj_url, headers=headers, params=params)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as ex:
            if response.status_code == 400:
                print(f"Bad request occurred. Exiting pagination loop.")
                break
            else:
                raise ex
        response = response.json()
        for item in response.get('objects'):
            all_vacancies.append(item)
        if not response.get('more'):
            break
    vacancies_found = response.get('total')
    return all_vacancies, vacancies_found


def calculate_average_salary_sj(vacancies):
    total_salary = 0
    vacancies_count = 0
    for vacancy in vacancies:
        salary_from = vacancy.get("payment_from")
        salary_to = vacancy.get("payment_to")
        predict_salary = predict_rub_salary(salary_from, salary_to)
        if predict_salary:
            total_salary += predict_salary
            vacancies_count += 1
    average_salary = total_salary / vacancies_count
    return vacancies_count, average_salary


if __name__ == "__main__":
    load_dotenv()

    hh_it_vacancies = []
    sj_it_vacancies = []

    for language in IT_LANGUAGES:
        try:
            hh_vacancies, vacancies_found = fetch_hh_vacancies(language)
            vacancies_count, average_salary = calculate_average_salary_hh(
                hh_vacancies)
            hh_it_vacancies.append(
                {
                    "language": language,
                    "vacancies_found": vacancies_found,
                    "vacancies_processed": vacancies_count,
                    "average_salary": round(average_salary),

                })

            sj_vacancies, vacancies_found = fetch_superjob_vacancies(language)
            vacancies_count, average_salary = calculate_average_salary_sj(
                sj_vacancies)
            sj_it_vacancies.append(
                {
                    "language": language,
                    "vacancies_found": vacancies_found,
                    "vacancies_processed": vacancies_count,
                    "average_salary": round(average_salary),

                })

        except requests.exceptions.HTTPError as ex:
            print(f"HTTP error occurred during  API request: {ex}")
        except GetVacanciesError as ex:
            print(ex)
            continue

    try:
        print(create_vacancies_table(hh_it_vacancies, "HeadHunter Moscow"))
        print(create_vacancies_table(sj_it_vacancies, "SuperJob Moscow"))
    except BaseException as error:  # KeyError, TypeError
        print(
            f"Ошибка анализа информации с сайта: {error}")
