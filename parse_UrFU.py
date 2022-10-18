from cgitb import text
from bs4 import BeautifulSoup
import requests
import re
from pymongo import MongoClient

client = MongoClient('localhost', 27017)

db = client['quasiDB']
series_collection = db['URFU']

base_url = 'https://study.urfu.ru'
url_authors = base_url + '/Rubricator/Author/'

dictionary = {}

def dict_add(keyWords):
    for word in keyWords:
        if dictionary.get(word, False):
            dictionary[word] += 1
        else: 
            dictionary[word] =  1

def insert_document(collection, data):
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
            for dataResources in allResources:
                filteredResources = {}
                filteredResources["name"] = dataResources.text 
                pageАnnotation = requests.get(base_url + dataResources.attrs['href'])
                soupАnnotation = BeautifulSoup(pageАnnotation.text, "html.parser")
                keyWords = soupАnnotation.find('span', text='Ключевые слова:')
                if keyWords != None:
                    keyWords = keyWords.next_sibling
                    keyWords = keyWords.lower()
                    keyWords = ' '.join(keyWords.split())
                    keyWords = keyWords.split(", ")
                    keyWords[-1] = keyWords[-1].replace(".", "")
                    dict_add(keyWords)
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
    parse()
    for key, value in sorted(dictionary.items(), key=lambda item: item[1]):
        print("{0}: {1}".format(key,value))
