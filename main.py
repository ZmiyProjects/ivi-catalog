import requests
from bs4 import BeautifulSoup
import re
from typing import Optional, List, NamedTuple, Set, Dict
import lxml


class Genre(NamedTuple):
    movies: Set[str]
    genre: str


def take_movies(url: str, max_page: int) -> Genre:
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
    genres_list = []
    r = requests.get(url)
    for item in BeautifulSoup(r.text, 'lxml').find_all("div", class_="gallery__item"):
        value = item.a
        if value is not None:
            current = value.get("href")
            if re.match(r"/movies/[a-z_]{3,}$", current) is not None:
                genres_list.append(current)
    return genres_list


def ivi_to_cvs(data: Dict[str, List[str]], path: str, header: List[str]):
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
        take, g = take_movies(root + i, 1)
        for j in take:
            all_movies[j] = []
        ivi.append(Genre(take, g))
    for i in ivi:
        print(i)
    print(all_movies)
    for i in all_movies.keys():
        for j in ivi:
            if i in j.movies:
                all_movies[i].append(j.genre)
    for i, j in all_movies.items():
        print(i, j)
    ivi_to_cvs(all_movies, 'ivi.csv', ['Фильм', 'Ветви каталога'])
