import argparse
import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathlib import Path


def on_reload(json_file_path):
    os.makedirs('./pages', exist_ok=True)
    path = 'pages'

    with open(json_file_path, encoding='utf-8') as my_file:
        books_description = json.load(my_file)

    env = Environment(
        loader=FileSystemLoader('./'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    cards_on_pages = 20
    columns = 2
    chuncked_books = list(chunked(books_description, cards_on_pages))
    for num, cards_on_pages in enumerate(chuncked_books, 1):
        grouped_books = list(chunked(cards_on_pages, columns))
        template = env.get_template('template.html')
        rendered_page = template.render(
            number_of_page=num,
            grouped_books=grouped_books,
            pages_count=len(chuncked_books)
        )
        with open(
                os.path.join(path, f'index{num}.html'), 'w', encoding='utf8'
        ) as file:
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
