from pathlib import Path
from urllib.parse import urljoin, urlsplit

import requests

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


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

for i in range(1, 11):
    try:
        response = requests.get(book_url.format(i), allow_redirects=False)
        response.raise_for_status()
        check_for_redirect(response)
    except requests.HTTPError:
        print(f'Обнаружен редирект, книга c id: {i} не скачана!')
    else:
        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.find('h1').text.split('::')[0].strip()
        url = download_book_url.format(i)
        download_txt(url, title)
        
        book_cover = soup.find('div', class_='bookimage').find('img').get('src')
        book_cover_url = urljoin(base_url, book_cover)
        print(title, book_cover_url, sep='\n', end='\n\n')
        download_image(book_cover_url)
