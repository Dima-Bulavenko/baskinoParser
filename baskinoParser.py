import json
import re
import os
import requests
from bs4 import BeautifulSoup

url = 'http://baskino.me'
number_pages = 2615
headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36",
}


def get_video_page_links(url, number_pages, headers):
    film_links = []
    for page in range(1, number_pages + 1):
        print(f'page number: {page}')
        new_url = url + f'/page/{page}/'
        req = requests.get(new_url, headers=headers)
        src = req.text

        soup = BeautifulSoup(src, 'lxml')
        try:
            films = soup.find(id="dle-content").find_all(class_=re.compile("posttitle"))
        except AttributeError:
            continue

        for film in films:
            try:
                film_links.append(film.find('a').get('href'))
            except AttributeError:
                continue
    return film_links


def get_videos_info(video_page_links):
    films_info = []
    flag = 1
    for film_link in video_page_links:
        print(f'Video number: {flag}')
        flag += 1
        try:
            req = requests.get(film_link, headers=headers)
            src = req.text
            soup = BeautifulSoup(src, 'lxml')
            image = soup.find(class_="mobile_cover").find("img").get("src")
            info_table = soup.find(class_="info").find('table')
            description = soup.find(id=re.compile("news-id")).get_text('<br>')
            name = info_table.find('td', string='Название:').find_next_sibling().text
            original_name = info_table.find('td', string='Оригинальное название:').find_next_sibling().text
            year = int(info_table.find('td', string='Год:').find_next_sibling().text)
            country = info_table.find('td', string='Страна:').find_next_sibling().text
            director = [i.strip() for i in
                        info_table.find('td', string='Режиссер:').find_next_sibling().text.split(",")]
            genre = [i.strip() for i in info_table.find('td', string='Жанр:').find_next_sibling().text.split(",")]
            actors = [i.strip() for i in
                      info_table.find('td', string='В главных ролях:').find_next_sibling().text.split(",")]
            video = soup.find(id='player-holder-1').find('iframe').get("src")
            rating = float(soup.find('b', itemprop="ratingValue").text.replace(',', '.'))
        except AttributeError:
            continue

        films_info.append({
            "name": name,
            'original_name': original_name,
            'year': year,
            'country': country,
            'director': director,
            'genre': genre,
            'actors': actors,
            'video': video,
            'image': image,
            'description': description,
            'rating': rating,
        })
    return films_info


def set_json_file(films_info):
    if os.path.exists('data.json'):
        os.remove("data.json")
    with open('data.json', 'a', encoding='utf-8') as file:
        json.dump(films_info, file, indent=4, ensure_ascii=False)


video_page_links = get_video_page_links(url, number_pages, headers)
videos_info = get_videos_info(video_page_links)
set_json_file(videos_info)
