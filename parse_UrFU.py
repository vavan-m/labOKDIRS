from bs4 import BeautifulSoup
import requests
import re
import os
from pymongo import MongoClient
from pick import pick

client = MongoClient('localhost', 27017)

db = client['quasiDB']
series_collection = db['URFU']

base_url = 'https://study.urfu.ru'
url_authors = base_url + '/Rubricator/Author/'

dictionary = {}

def get_all_keywords(collection):
    for document in collection.find():
        dict_add(document["resources"][0]["keyWords"])

def dict_add(keyWords):
    if(keyWords):
        for word in keyWords:
            if dictionary.get(word, False):
                dictionary[word] += 1
            else: 
                dictionary[word] =  1

def insert_document(collection, data):
    filter = { 'name' : data['name'] }
    if collection.find_one(filter):
        newValue = {"$set" : { 'resources': data['resources'] }}
        return collection.update_one(filter, newValue)
    return collection.insert_one(data).inserted_id

def parse():
    for letter in range(ord('А'), ord('Я')):   
        page = requests.get(url_authors + chr(letter))
        soup = BeautifulSoup(page.text, "html.parser")
        allAuthors = soup.findAll('a', {'href': re.compile(r'Search/Author/\d+')})
        for data in allAuthors:
            filteredAuthor = {}
            filteredAuthor["name"] = data.text 
            filteredAuthor["resources"] = []
            pageResources = requests.get(base_url + data.attrs['href'])
            soupResources = BeautifulSoup(pageResources.text, "html.parser")
            allResources = soupResources.findAll('a', {'href': re.compile(r'Aid/ViewMeta/\d+')})
            numResource = 0
            for dataResources in allResources:
                filteredResources = {}
                filteredResources["name"] = dataResources.text 
                pageАnnotation = requests.get(base_url + dataResources.attrs['href'])
                soupАnnotation = BeautifulSoup(pageАnnotation.text, "html.parser")
                numResource += 1
                filename = f'cache/{chr(letter)}/{data.text}/{numResource}.html'
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                html = soupАnnotation.prettify("utf-8")
                with open(filename, "wb") as file:
                    file.write(html)
                keyWords = soupАnnotation.find('span', text='Ключевые слова:')
                if keyWords != None:
                    keyWords = keyWords.next_sibling
                    keyWords = keyWords.lower()
                    keyWords = ' '.join(keyWords.split())
                    keyWords = keyWords.split(", ")
                    keyWords[-1] = keyWords[-1].replace(".", "")
                annotation = soupАnnotation.find('h3', text='Аннотация')
                annotation = annotation.next_sibling
                annotation = annotation.replace("\r\n", "")
                annotation = ' '.join(annotation.split())
                if (annotation == '\n') or (annotation == ''):
                    filteredResources["annotation"] = None 
                else: 
                    filteredResources["annotation"] = annotation
                filteredResources["keyWords"] = keyWords
                filteredAuthor["resources"].append(filteredResources)
            insert_document(series_collection, filteredAuthor)

def parseFromCache():
    for letter in range(ord('А'), ord('Я')):
        content = os.listdir(f'cache/{chr(letter)}/')   
        for nameAuthor in content:
            filteredAuthor = {}
            filteredAuthor["name"] = nameAuthor.text 
            filteredAuthor["resources"] = []
            for dataResources in os.listdir(f'cache/{chr(letter)}/{nameAuthor}'):
                filteredResources = {}
                HTMLFile = open(f'cache/{chr(letter)}/{nameAuthor}/{dataResources}', "r", encoding="utf8")
                pageАnnotation = HTMLFile.read()
                soupАnnotation = BeautifulSoup(pageАnnotation, "html.parser")
                keyWords = soupАnnotation.text.find('span', text='Ключевые слова:')
                if keyWords != None:
                    keyWords = keyWords.next_sibling
                    keyWords = keyWords.lower()
                    keyWords = ' '.join(keyWords.split())
                    keyWords = keyWords.split(", ")
                    keyWords[-1] = keyWords[-1].replace(".", "")
                annotation = soupАnnotation.find('h3', text='Аннотация')
                annotation = annotation.next_sibling
                annotation = annotation.replace("\r\n", "")
                annotation = ' '.join(annotation.split())
                if (annotation == '\n') or (annotation == ''):
                    filteredResources["annotation"] = None 
                else: 
                    filteredResources["annotation"] = annotation
                filteredResources["keyWords"] = keyWords
                filteredAuthor["resources"].append(filteredResources)
            insert_document(series_collection, filteredAuthor)


if __name__ == "__main__":   
    title = 'Выберете предпочитаемый метод: '
    options = ['Парсинг сайта УрФУ', 'Парсинг сохраненной ранне копии сайта', 'Получить ключевые слова']
    option, index = pick(options, title)

    if index == 0:
        parse()
    elif index == 1:
        parseFromCache()
    else:
        get_all_keywords(series_collection)
        for key, value in sorted(dictionary.items()):
            print("{0}: {1}".format(key,value))

