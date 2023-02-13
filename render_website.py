import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked
from pathlib import Path


def on_reload():
    os.makedirs('./pages', exist_ok=True)

    with open('books_description.json', encoding='utf-8') as my_file:
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
                Path.cwd() / 'pages' / f'index{num}.html',
                'w',
                encoding='utf8',
        ) as file:
            file.write(rendered_page)


if __name__ == '__main__':
    on_reload()

    server = Server()
    server.watch('./template.html', on_reload)
    server.serve(root='.', default_filename='pages/index1.html')
