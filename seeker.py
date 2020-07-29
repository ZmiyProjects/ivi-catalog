import requests
from bs4 import BeautifulSoup
import re
from typing import List, NamedTuple, Set, Dict
import argparse
import sys


class Genre(NamedTuple):
    """
    movies - перечень фильмов
    genre - жанр всех фильмов из множества movies
    """
    movies: Set[str]
    genre: str


def take_movies(url: str, max_page: int) -> Genre:
    """
    Считывает в именованный кортеж Genre сведения о фильмах определённого жанра
    :param url: адрес страницы с фильмами определённого жанра
    :param max_page: максимальное количество страниц в рамках жанра, для которых будет получен перечень фильмов
    например, если указано 2 -- будут считаны сведения первых двух страниц
    :return: Возвращает именованный кортеж Genre
    """
    if max_page <= 0:
        raise ValueError
    page_movies = set()
    page_num = 1
    while True:
        r = requests.get(url + f"/page{page_num}")
        catalog = BeautifulSoup(r.text, 'lxml')
        page = catalog.find_all("img", class_="nbl-poster__image")
        if not page:
            break
        else:
            for p in page:
                page_movies.add(p.get("alt"))
            page_num += 1
            if page_num > max_page:
                break
    ru_genre = catalog.find('meta', attrs={'name': 'keywords'}).get("content").split(', ')[1]
    return Genre(page_movies, ru_genre)


def take_genres(url: str) -> List[str]:
    """
    Считывает перечень адресов имеющихся жанров с главной страницы ivi.ru
    :param url: адрес главной страницы ivi.ru
    :return: список с перечнем адресов страниц
    """
    genres_list = []
    r = requests.get(url)
    for item in BeautifulSoup(r.text, 'lxml').find_all("div", class_="gallery__item"):
        value = item.a
        if value is not None:
            current = value.get("href")
            if re.match(r"/movies/[a-z_]{3,}$", current) is not None:
                genres_list.append(current)
    return genres_list


def ivi_to_cvs(data: Dict[str, List[str]], path: str, header: List[str]) -> None:
    """
    Записывает данные из словаря в .csv файл
    :param data: словарь с данными для записи
    :param path: путь к файлу для записи
    :param header: заголовки файла в формате массива
    """
    with open(path, 'w', encoding='utf-8') as writer:
        if header is not None:
            writer.write(';'.join(header))
        writer.writelines(f"\n{key};{','.join(values)}" for key, values in data.items())


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pages', type=int, default=1)
    parser.add_argument('-r', '--result_file', type=str, default="ivi.csv")
    parsed_args = parser.parse_args(sys.argv[1:])

    root = "https://www.ivi.ru"
    all_movies = {}
    genres = take_genres(root + '/movies')
    for i in genres:
        movies = take_movies(root + i, parsed_args.pages)
        for new_key in movies.movies:
            if new_key in all_movies:
                all_movies[new_key].append(movies.genre)
            else:
                all_movies[new_key] = [movies.genre]

    ivi_to_cvs(all_movies, parsed_args.result_file, ['Фильм', 'Ветви каталога'])
