from pathlib import Path

import requests

url = "https://tululu.org/txt.php?id={}"

Path(Path.cwd() / 'books').mkdir(exist_ok=True)

for i in range(1, 11):
    response = requests.get(url.format(i))
    response.raise_for_status()
    
    with open(f'books/id{i}.txt', 'wb') as file:
        file.write(response.content)
