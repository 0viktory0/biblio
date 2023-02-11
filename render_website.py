import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
import json
from more_itertools import chunked
from pathlib import Path


def on_reload():
    os.makedirs('./pages', exist_ok=True)

 #   with open('books.json', 'r', errors="ignore") as file:
  #      books = json.load(file)

    with open("books.json", encoding="utf-8") as my_file:
        books_json = my_file.read()

    books = json.loads(books_json)

    env = Environment(
        loader=FileSystemLoader('./'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    books_on_pages = 20
    books_pages = list(chunked(books, books_on_pages))

    for num, books_on_page in enumerate(books_pages, 1):
        grouped_books = list(chunked(books_on_page, 2))
        template = env.get_template('template.html')

        rendered_page = template.render(
            number_of_page=num,
            grouped_books=grouped_books,
            pages_count=len(books_pages)
        )
        with open(
                Path.cwd() / 'pages' / f'index{num}.html',
                'w',
                encoding="utf8",
        ) as file:
            file.write(rendered_page)


def main():
    on_reload()

    server = Server()
    server.watch('./template.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()



