
from terminaltables import AsciiTable


def create_vacancies_table(it_vacancies, title):
    vacancies_table = []
    vacancies_table.append(
        [
            "Язык программирования",
            "Вакансий найдено",
            "Вакансий обработанно",
            "Средняя зарплата",
        ]
    )
    for statistic_item in it_vacancies:
        vacancies_table.append(
            [
                statistic_item["language"],
                statistic_item["vacancies_found"],
                statistic_item["vacancies_processed"],
                statistic_item["average_salary"],
            ]
        )
    jobs_table = AsciiTable(vacancies_table, title)
    print(jobs_table.table)
