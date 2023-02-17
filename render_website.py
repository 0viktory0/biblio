import argparse
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from math import ceil


def on_reload(json_file_path):
    path = 'pages'
    os.makedirs(path, exist_ok=True)

    with open(json_file_path, encoding='utf8') as file:
        books_description = json.load(file)

    env = Environment(
        loader=('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    cards_on_pages = 20
    rows_on_page = 10
    number_of_pages = ceil(len(books_description) / cards_on_pages)
    chuncked_books = list(chunked(books_description, cards_on_pages))
    last_page = len(chuncked_books) - 1
    for num, book_cards in enumerate(chuncked_books, 1):
        grouped_cards = list(chunked(book_cards, rows_on_page))
        template = env.get_template('template.html')
        page_path = os.path.join(
            path,
            f'index{num}.html')

        rendered_page = template.render(
            chuncked_books=grouped_cards,
            number_of_pages=number_of_pages,
            current_page_number=num,
            last_page=last_page
        )
        with open(page_path, 'w', encoding='utf8') as file:
            file.write(rendered_page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--json_path', type=str, default='books_description.json',
                        help='Путь к *.json файлу с результатами')
    args = parser.parse_args()
    json_file_path = args.json_path

    on_reload(json_file_path)

    server = Server()
    server.watch('./template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')
