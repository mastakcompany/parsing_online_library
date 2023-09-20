from pathlib import Path
from urllib.parse import urljoin, urlsplit
import requests
import argparse

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup

parser = argparse.ArgumentParser(description='The program downloads a range of books, by their id')
parser.add_argument('start_id', help='Initial book id', default=1, type=int, nargs='?')
parser.add_argument('end_id', help='Final id of the book, not including it', default=10, type=int, nargs='?')
args = parser.parse_args()


def check_for_redirect(response):
    if response.is_redirect:
        raise requests.HTTPError


def create_dir(folder):
    Path(Path.cwd() / folder).mkdir(exist_ok=True)


def download_txt(url, filename, folder='books/'):
    book_name = sanitize_filename(filename)
    create_dir(folder)
    response = requests.get(url)
    response.raise_for_status()
    
    with open(f'{Path().cwd() / folder}/{filename}.txt', 'wb') as file:
        file.write(response.content)
    
    return f'{Path(folder) / book_name}.txt'


def download_image(url, folder='images/'):
    response = requests.get(url)
    response.raise_for_status()
    create_dir(folder)
    book_name = urlsplit(url).path.split('/')[-1]
    
    with open(f'{Path().cwd() / folder}/{book_name}', 'wb') as file:
        file.write(response.content)


base_url = 'https://tululu.org/'
download_book_url = 'https://tululu.org/txt.php?id={}'
book_url = 'https://tululu.org/b{}/'


def parse_book_page(html):
    soup = BeautifulSoup(html.text, 'lxml')
    title, author = map(str.strip, soup.find('h1').text.split('::'))
    book_cover = soup.find('div', class_='bookimage').find('img').get('src')
    book_genres = [genres.text for genres in soup.find('span', class_='d_book').find_all('a')]
    description = soup.find(id='content').find_all('table')[2].text
    comments = [comment.find('span', class_='black').text for comment in soup.find_all('div', class_='texts')]
    
    return {
        'title'      : title,
        'author'     : author,
        'book_cover' : book_cover,
        'book_genres': book_genres,
        'description': description,
        'comments'   : comments
    }


for i in range(args.start_id, args.end_id+1):
    try:
        response = requests.get(book_url.format(i), allow_redirects=False)
        response.raise_for_status()
        check_for_redirect(response)
    except requests.HTTPError:
        print(f'Обнаружен редирект, книга c id: {i} не скачана!\n')
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        book_cover = soup.find('div', class_='bookimage').find('img').get('src')
        book_cover_url = urljoin(base_url, book_cover)
        url = download_book_url.format(i)
        book_data = parse_book_page(response)

        title, author = book_data['title'], book_data['author']
        download_txt(url, title)
        download_image(book_cover_url)
        print(f'Название: {title}\nАвтор: {author}', end='\n\n')
