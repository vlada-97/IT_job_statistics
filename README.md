# Статистика вакансий программистов в городе Москва

Данная статистика собирается с двух сайтов по поиску работы:

- [HeadHanter](https://hh.ru/)
- [SuperJob](https://superjob.ru/)

В статистике учавствуют языки программирования:

- Python,
- JavaScript,
- C++,
- PHP,
- C#,
- Java

*Языки программирования можно изменить самостоятельно.*

## Пример результатов

![](https://github.com/vlada-97/IT_job_statistics/blob/main/gif/it_statistics.gif)

## Как установить

Python должен быть уже установлен. Затем используйте pip для установки зависимостей:

```cmd
pip install -r requirements.txt
```

## Переменные окружения

- [secret_key] - необходимый api ключ с сайта superJob, получить по [ссылке](https://api.superjob.ru/info/)

## Запуск скриптов

Производится без параметров.

Для того, чтобы получить статистику с сайтов:

```cmd
>> python IT_job_statistics.py
```
