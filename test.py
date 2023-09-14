import requests
from bs4 import BeautifulSoup

url = "https://tululu.org/b1/"

response = requests.get(url)
response.raise_for_status()

soup = BeautifulSoup(response.text, 'lxml')
title, author = map(str.strip, soup.find('h1').text.split('::'))
print(title, author, sep='\n')
