import requests
from bs4 import BeautifulSoup

main_url = 'https://vestnik.pstu.ru/elinf/archives/'
response = requests.get(main_url)
soup = BeautifulSoup(response.text, 'lxml')
heads = soup.find_all('div', class_='head')

for head in heads:
    url_for_year = main_url+head.a.get('href')
    response = requests.get(url_for_year)
    soup = BeautifulSoup(response.text, 'lxml')
    heads1 = soup.find_all('div', class_='head')
    
    for head1 in heads1:
        url_for_part = ''.join(url_for_year.split('?')[:-1])+head1.a.get('href')
        response = requests.get(url_for_part)
        response.encoding = 'cp1251'
        new_text = response.text.replace("</strong><br>", "</strong><div class='my_class'>").replace("<br>", "</div>")
        soup = BeautifulSoup(new_text, 'lxml')
        file_links = soup.find_all('div', class_='file_link')
        
        for file_link in file_links:
            science_field = file_link.strong
            if science_field is not None:
                science_field = science_field.text
                authors = file_link.find("div", class_='my_class')
                if authors is not None:
                    authors = list(map(str.strip, authors.text.split(',')))
                    print(f'{science_field}: {authors}')
                    print(' ')
