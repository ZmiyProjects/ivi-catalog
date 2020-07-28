import requests
from bs4 import BeautifulSoup
import re
from typing import List, NamedTuple, Set, Dict


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
        page = BeautifulSoup(r.text, 'lxml').find_all("img", class_="nbl-poster__image")
        if not page:
            break
        else:
            for p in page:
                page_movies.add(p.get("alt"))
            page_num += 1
            if page_num > max_page:
                break
    return Genre(page_movies, url.replace('https://www.ivi.ru/movies/', ''))


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
    with open(path, 'w') as writer:
        if header is not None:
            writer.write(';'.join(header))
        writer.writelines(f"\n{key};{','.join(values)}" for key, values in data.items())


if __name__ == "__main__":
    root = "https://www.ivi.ru"
    all_movies = {}
    ivi: List[Genre] = []
    genres = take_genres(root + '/movies')
    for i in genres:
        movies = take_movies(root + i, 2)
        for new_key in movies.movies:
            all_movies[new_key] = []
        ivi.append(movies)

    for cur_key in all_movies.keys():
        for movies_set in ivi:
            if cur_key in movies_set.movies:
                all_movies[cur_key].append(movies_set.genre)

    ivi_to_cvs(all_movies, 'ivi.csv', ['Фильм', 'Ветви каталога'])
