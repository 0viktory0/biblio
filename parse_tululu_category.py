import argparse
import json
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from parse_tululu import check_for_redirect, download_txt, download_image, parse_book_page


def parse_books_urls(response):
    soup = BeautifulSoup(response.text, 'lxml')
    #books_select = '#content .bookimage a'
    #books = soup.select(books_select)
    books = soup.find('div', id='content').find_all('table')
    one_page_books_urls = list()
    for book in books:
        book_id = book.find('a')['href']
        book_url = urljoin(response.url, book_id)
        one_page_books_urls.append(book_url)
    return one_page_books_urls


if __name__ == '__main__':
    books_url = 'https://tululu.org'

    book_folder = 'books'
    img_folder = 'images'

    parser = argparse.ArgumentParser()
    parser.add_argument('--first_page', type=int, default=1,
                        help='Первая страница для скачивания')
    parser.add_argument('--last_page', type=int, default=5,
                        help='Последняя страница для скачивания')
    parser.add_argument('--books_category', type=int, default=55,
                        help='Категория подборки книг')
    parser.add_argument('--dest_folder', type=str, default="",
                        help='Путь к каталогу с результатами парсинга')
    parser.add_argument('--skip_img', action='store_true',
                        help='Не скачивать картинки')
    parser.add_argument('--skip_txt', action='store_true',
                        help='Не скачивать книги')
    parser.add_argument('--json_path', type=str, default='books.json',
                        help='Путь к *.json файлу с результатами')
    args = parser.parse_args()

    first_page = args.first_page
    last_page = args.last_page + 1
    books_category = args.books_category
    skip_txt = args.skip_txt
    skip_img = args.skip_img
    dest_folder = args.dest_folder
    json_file_path = args.json_path

    books_urls = list()
    for page_number in range(first_page, last_page + 1):
        new_page_url = urljoin(books_url, f'/l{books_category}/{page_number}')
        try:
            response = requests.get(new_page_url)
            response.raise_for_status()
            check_for_redirect(response)
            on_page_books_urls = parse_books_urls(response)

            books_urls.extend(on_page_books_urls)

        except (requests.HTTPError) as e:
            print(f'Страница {page_number} не найдена ')
            continue
        except (requests.ConnectionError) as e:
            print('Ошибка подключения. Повторное соединение...')
            time.sleep(10)
            continue

    comments = []
    for book_url in books_urls:
        book_id = urlparse(book_url).path.replace('/', '').replace('b', '')
        book_txt_url = urljoin(books_url, 'txt.php')
        book_url = f'{books_url}/b{book_id}/'
        try:
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            book = parse_book_page(response)
            book_path = download_txt(book_txt_url, book_id, book['book_name'], book_folder)
            img_path = download_image(book['book_img'], img_folder)

        except (requests.HTTPError) as e:
            print('Книга с id = {}, не найдена '.format(book_id))
            continue

        except (requests.ConnectionError) as e:
            print('Ошибка подключения. Повторное соединение...')
            time.sleep(10)
            continue

        comments.append({
            'title': book['book_name'],
            'author': book['author'],
            'img_src': img_path,
            'book_path': book_path,
            'comments': book['comments'],
            'genres': book['genres'],
        })


    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(
            comments,
            file,
            ensure_ascii=False,
            indent=4,
            sort_keys=False
        )