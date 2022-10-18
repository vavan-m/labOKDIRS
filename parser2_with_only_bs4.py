import requests
from bs4 import BeautifulSoup

main_url = 'https://pstu.ru/title1/faculties/'
main_site_url = 'https://pstu.ru'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

response = requests.get(main_url, headers=headers)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'lxml')
ul = soup.find('ul', class_='faculties')
faculties = ul.find_all('li')

for fac in faculties:
    print(f'ФАКУЛЬТЕТ: {fac.text}')
    url_for_fac = main_url+'/'.join(fac.a.get('href').split('/')[-2:])
    response = requests.get(url_for_fac, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'lxml')
    div = soup.find('div', class_='chairs')
    chairs = div.find_all('li')
    
    for ch in chairs:
        print(f'КАФЕДРА: {ch.text}')
        url_for_chair = url_for_fac+'/'.join(ch.a.get('href').split('/')[-2:])
        response = requests.get(url_for_chair, headers=headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')
        div = soup.find('div', class_='fac')
        markers = div.find_all('li')
        
        for m in markers:
            if m.text == 'Сотрудники кафедры':
                url_for_employees = main_site_url + m.a.get('href')
                response = requests.get(url_for_employees, headers=headers)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')
                div = soup.find('div', class_='fac')
                employees = div.find_all('li')

                for e in employees:
                    url_for_employee = main_site_url + e.a.get('href')
                    response = requests.get(url_for_employee, headers=headers)
                    response.encoding = 'utf-8'
                    soup = BeautifulSoup(response.text, 'lxml')
                    div = soup.find('div', class_='head_info')
                    fio = div.find('h6')
                    print(fio.text)
        print(' ')
    print(' ')              
