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


def predict_rub_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to) / 2
    elif salary_from:
        return salary_from * 1.2
    elif salary_to:
        return salary_to * 1.8
    return None


def fetch_hh_vacancies(language):
    hh_url = "https://api.hh.ru/vacancies/"
    params = {
        "text": f"Программист {language}",
        "per_page": 100,
        "currency": "RUR",
        "city": "Москва"
    }
    all_vacancies = []
    page = 0
    vacancies_found = 0
    for page in range(20):  # maximum 20 pages
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
        result = response.json()
        vacancies = result.get("items", [])
        if not vacancies:
            break
        all_vacancies.extend(vacancies)
        vacancies_found = result.get("found", 0)
    return all_vacancies, vacancies_found


def calculate_average_salary_hh(vacancies):
    total_salary = 0
    vacancies_count = 0
    for vacancy in vacancies:
        salary = vacancy.get("salary")
        if salary:
            salary_from = salary.get("from")
            salary_to = salary.get("to")
            salary_avg = predict_rub_salary(salary_from, salary_to)
            if salary_avg is not None:
                total_salary += salary_avg
                vacancies_count += 1
    average_salary = total_salary / vacancies_count if vacancies_count > 0 else 0
    return vacancies_count, average_salary


def fetch_superjob_vacancies(language):
    sj_url = "https://api.superjob.ru/2.0/vacancies/"
    secret_key = os.environ["SECRET_KEY"]
    params = {
        "keyword": f"Программист {language}",
        "town": "Москва",
        "page": 5,
        "count": 100,
    }
    headers = {
        "X-Api-App-Id": secret_key,
    }
    response = requests.get(sj_url, headers=headers, params=params)
    response.raise_for_status()
    result = response.json()
    return result


def calculate_average_salary_sj(vacancies):
    total_salary = 0
    vacancies_count = 0
    vacancies_found = 0
    for vacancy in vacancies:
        vacancies_found += 1
        salary_from = vacancy.get("payment_from")
        salary_to = vacancy.get("payment_to")
        salary_avg = predict_rub_salary(salary_from, salary_to)
        if salary_avg is not None:
            total_salary += salary_avg
            vacancies_count += 1
    average_salary = total_salary / vacancies_count if vacancies_count > 0 else 0
    return vacancies_found, vacancies_count, average_salary


def generate_vacancy_statistics(language, vacancies_found, vacancies_count, average_salary):
    vacancies_list = {
        "language": language,
        "vacancies_found": vacancies_found,
        "vacancies_processed": vacancies_count,
        "average_salary": round(average_salary),
    }
    return vacancies_list


if __name__ == "__main__":
    load_dotenv()

    hh_it_vacancies = []
    sj_it_vacancies = []

    for language in IT_LANGUAGES:
        try:
            hh_vacancies, vacancies_found = fetch_hh_vacancies(language)
            vacancies_count, average_salary = calculate_average_salary_hh(
                hh_vacancies)
            hh_it_vacancies.append(generate_vacancy_statistics(
                language, vacancies_found, vacancies_count, average_salary))

            sj_vacancies = fetch_superjob_vacancies(language)
            vacancies = sj_vacancies.get("objects")
            vacancies_found, vacancies_count, average_salary = calculate_average_salary_sj(
                vacancies)
            sj_it_vacancies.append(generate_vacancy_statistics(
                language, vacancies_found, vacancies_count, average_salary))

        except requests.exceptions.HTTPError as ex:
            print(f"HTTP error occurred during  API request: {ex}")

    try:
        create_vacancies_table(hh_it_vacancies, "HeadHunter Moscow")

        create_vacancies_table(sj_it_vacancies, "SuperJob Moscow")
    except (KeyError, TypeError) as error:
        print(
            f"Ошибка анализа информации с сайта: {error}")
