# Описание

Консольное приложение для получение актуального каталога фильмов на сайте ivi.ru. Результат забисывается в файл .csv. 

- `seeker.py` -- скрипт для получение актуального каталога фильмов
- `requirements.txt` -- перечень необходимых зависимостей
- `ivi.csv` -- пример вывода скрипта

# Агрументы командной строки

Скрипт `seeker.py` принимает 2 аргумента
- `-p`, `--pages` -- максимальное количество страниц в рамках жанра, для которых будет получен перечень фильмов например, если указано 2 -- будут считаны сведения первых двух страниц, по умолчанию равно 1
- `-r`, `--result_file` -- имя файла, в который будут записаны результаты, по умолчанию равно "ivi.csv"

# Как запустить?

## Linux

Скопировать на локальное устройство и запустить контейнер в корневой директории проекта:

```sh
git clone https://github.com/ZmiyProjects/ivi-catalog
cd ivi-catalog/
python -m venv venv
sourse venv/bin/activate
pip install -r requirements.txt
chmod u+x seeker.py
python3 ./seeker.py
```