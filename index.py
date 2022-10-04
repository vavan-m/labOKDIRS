from cgitb import text
from bs4 import BeautifulSoup
import requests
import re
import json
base_url = 'https://study.urfu.ru'
url_author = base_url + '/Rubricator/Author/'

alphabet = ["А","Б","В","Г","Д","Е","Ё","Ж","З","И","Й","К","Л","М","Н",
            "О","П","Р","С","Т","У","Ф","Х","Ц","Ч","Ш","Щ","Ы","Э","Ю","Я"]
filteredAuthors = []
for letter in alphabet:
    page = requests.get(url_author + letter)
    soup = BeautifulSoup(page.text, "html.parser")
    allAuthors = soup.findAll('a', {'href': re.compile(r'Search/Author/\d+')})
    for data in allAuthors:
        filteredAuthor = {}
        filteredAuthor["name"] = data.text 
        filteredAuthor["href"] = data.attrs['href']
        filteredAuthor["resources"] = []
        pageResources = requests.get(base_url + data.attrs['href'])
        soupResources = BeautifulSoup(pageResources.text, "html.parser")
        allResources = soupResources.findAll('a', {'href': re.compile(r'Aid/ViewMeta/\d+')})
        for dataResources in allResources:
            filteredResources = {}
            filteredResources["name"] = dataResources.text 
            filteredResources["href"] = dataResources.attrs['href']
            pageАnnotation = requests.get(base_url + dataResources.attrs['href'])
            soupАnnotation = BeautifulSoup(pageАnnotation.text, "html.parser")
            keyWords = soupАnnotation.find('span', text='Ключевые слова:')
            if keyWords != None:
                keyWords = keyWords.next_sibling
            annotation = soupАnnotation.find('h3', text='Аннотация')
            annotation = annotation.next_sibling
            filteredResources["annotation"] = annotation
            filteredResources["keyWords"] = keyWords
            filteredAuthor["resources"].append(filteredResources)
        filteredAuthors.append(filteredAuthor)

with open('data.json', 'w') as outfile:
    json.dump(filteredAuthors, outfile, ensure_ascii=False)