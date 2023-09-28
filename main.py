import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit
import requests
import argparse
import sys
from requests.exceptions import HTTPError, ConnectionError

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def get_parser():
    parser = argparse.ArgumentParser(description='The program downloads a range of books, by their id')
    parser.add_argument('start_id', help='Initial book id, default=1', default=1, type=int, nargs='?')
    parser.add_argument('end_id', help='Final id of the book, not including it, default=10', default=10, type=int,
                        nargs='?')
    return parser


def check_for_redirect(response):
    if response.is_redirect:
        raise requests.HTTPError


def download_txt(url, book_id, filename, folder='books/'):
    payload = {'id': book_id}
    book_name = sanitize_filename(filename)
    Path(Path.cwd() / folder).mkdir(exist_ok=True)
    response = requests.get(url, params=payload)
    response.raise_for_status()
    path_to_save_book = Path(f'{folder}/{book_name}.txt')
    
    with open(path_to_save_book, 'wb') as file:
        file.write(response.content)
    
    return path_to_save_book


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    Path(Path.cwd() / folder).mkdir(exist_ok=True)
    book_name = urlsplit(url).path.split('/')[-1]
    
    with open(f'{Path().cwd() / folder}/{book_name}', 'wb') as file:
        file.write(response.content)


def parse_book_page(html, book_url):
    soup = BeautifulSoup(html.text, 'lxml')
    title, author = map(str.strip, soup.find('h1').text.split('::'))
    book_cover = soup.find('div', class_='bookimage').find('img').get('src')
    book_cover_url = urljoin(book_url, book_cover)
    book_genres = [genres.text for genres in soup.find('span', class_='d_book').find_all('a')]
    description = soup.find(id='content').find_all('table')[2].text
    comments = [comment.find('span', class_='black').text for comment in soup.find_all('div', class_='texts')]
    
    return {
        'title'         : title,
        'author'        : author,
        'book_cover'    : book_cover,
        'book_cover_url': book_cover_url,
        'book_genres'   : book_genres,
        'description'   : description,
        'comments'      : comments
    }


def get_book_info(book_id, download_book_url, book_url, base_url):
    try:
        response = requests.get(book_url.format(book_id), allow_redirects=False)
        response.raise_for_status()
        check_for_redirect(response)
    except requests.HTTPError:
        print(f'Обнаружен редирект, книга c id: {book_id} не скачана!\n')
    
    else:
        book_content = parse_book_page(response, base_url)
        title, author, book_cover_url = book_content['title'], book_content['author'], book_content['book_cover_url']
        download_txt(download_book_url, book_id, title)
        download_image(book_cover_url)
        print(f'Название: {title}\nАвтор: {author}', end='\n\n')


def main():
    parser = get_parser()
    args = parser.parse_args()
    
    base_url = 'https://tululu.org/'
    download_book_url = 'https://tululu.org/txt.php'
    book_url = 'https://tululu.org/b{}/'
    
    for book_id in range(args.start_id, args.end_id + 1):
        is_first_attempt = True
        while True:
            try:
                get_book_info(book_id, download_book_url, book_url, base_url)
            except ConnectionError as e:
                eprint(f'Исключение: {e}!\nБудет предпринята повторная попытка для id {book_id}.')
                if is_first_attempt:
                    is_first_attempt = False
                    time.sleep(1)
                else:
                    time.sleep(5)
                continue
            except HTTPError as e:
                eprint(f'Исключение: {e}!\nКнига с id {book_id} не скачана.')
                break
            else:
                break


if __name__ == '__main__':
    main()
