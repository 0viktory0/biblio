import argparse
import os
import requests
import time
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin, urlsplit


def donload_txt(book_txt_url, book_id, file_name, folder):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(
        urljoin(books_url, book_txt_url),
        params={'id': book_id}
    )
    response.raise_for_status()
    check_for_redirect(response)
    sanitized_filename = sanitize_filename(f'{file_name}_{book_id}')
    file_extension = '.txt'
    book_path = os.path.join(folder, f'{sanitized_filename}{file_extension}')
    with open(book_path, 'w') as file:
        file.write(response.text)
    return book_path


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    page_title = soup.head.title.text.split(' - ')
    book_name, string_with_author = page_title
    author = string_with_author.split(',')

    img_select = 'body table .bookimage img'
    book_img = soup.select_one(img_select)['src']
    img_url = urljoin(response.url, book_img)

    comments_select = 'body div.texts span.black'
    comments = soup.select(comments_select)
    comments_text = [comment.text for comment in comments]

    genres_select = 'span.d_book a'
    genre_tags = soup.select(genres_select)
    genres = [tag.text for tag in genre_tags]

    return {
        'book_name': book_name,
        'author': author,
        'book_img': img_url,
        'comments': comments_text,
        'genres': genres
    }


def download_image(url, folder):
    os.makedirs(folder, exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    file_name = os.path.basename(urlsplit(url).path)
    sanitized_filename = sanitize_filename(file_name)
    img_path = os.path.join(folder, sanitized_filename)

    with open(img_path, 'wb') as file:
        file.write(response.content)
    return img_path


if __name__ == '__main__':
    books_url = 'https://tululu.org'

    parser = argparse.ArgumentParser()
    parser.add_argument("--start_id", type=int, default=1, help='Book id to start download')
    parser.add_argument("--end_id", type=int, default=10, help='Book id to end download')
    args = parser.parse_args()

    end_id = args.end_id + 1
    start_id = args.start_id

    book_folder = 'books'
    img_folder = 'images'
    for book_id in range(start_id, end_id):
        book_url = f'{books_url}/b{book_id}/'
        book_txt_url = urljoin(books_url, 'txt.php')
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(response)
            donload_txt(book_txt_url, book_id, book['book_name'], book_folder)
            download_image(book['book_img'], img_folder)
        except (requests.HTTPError) as e:
            print('Книга с id = {}, не найдена '.format(book_id))
            continue

        except (requests.ConnectionError) as e:
            print('Ошибка подключения. Повторное соединение...')
            time.sleep(10)
            continue