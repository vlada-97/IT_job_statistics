
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
    for statistic_measure in it_vacancies:
        vacancies_table.append(
            [
                statistic_measure["language"],
                statistic_measure["vacancies_found"],
                statistic_measure["vacancies_processed"],
                statistic_measure["average_salary"],
            ]
        )
    jobs_table = AsciiTable(vacancies_table, title)
    return jobs_table.table
