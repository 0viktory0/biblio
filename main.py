import requests
import os



def get_books(directory):

    for book_id in range(9):
        response = requests.get(f"https://tululu.org/txt.php?id={book_id}")
        response.raise_for_status()

        path = os.path.join(directory, f'{book_id}.txt')
        with open(path, 'wb') as file:
            file.write(response.content)

if __name__ == '__main__':

    os.makedirs("books", exist_ok=True)

    get_books("books")





