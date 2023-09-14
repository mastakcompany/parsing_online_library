from pathlib import Path
import requests

from pathvalidate import sanitize_filename
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.is_redirect:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    book_name = sanitize_filename(filename)
    Path(Path.cwd() / folder).mkdir(exist_ok=True)
    response = requests.get(url)
    response.raise_for_status()

    with open(f'{Path().cwd()/folder}/{filename}.txt', 'wb') as file:
        file.write(response.content)
    
    return f'{Path(folder) / book_name}.txt'


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
