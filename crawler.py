import requests
from bs4 import BeautifulSoup

url = 'https://example.com'

response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    for link in soup.find_all('a'):
        print('텍스트:', link.text)
        print('링크:', link.get('href'))
else:
    print('웹 페이지를 불러오는 데 실패했습니다.', response.status_code)