from bs4 import BeautifulSoup
import requests
import re
import os
from pymongo import MongoClient
from pick import pick
# selenium
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import (presence_of_element_located)
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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


# кибер ленинка поиск 
def searchInCyberleninka():
    base_url = "https://cyberleninka.ru/"
    url_search = base_url + "search?q="

    words = input("Введите описание иследования: ")
    words = words.split(" ")
    url_search += '%20'.join(words)
    print(url_search)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url_search)
    time.sleep(10)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    allArticlKeyWords = []
    allArticle = soup.findAll('a', {'href': re.compile(r'/article/')})
    for article in allArticle:
        pageАrticle = requests.get(base_url + article.attrs['href'])
        soupАrticle = BeautifulSoup(pageАrticle.text, "html.parser")
        keyWords = soupАrticle.findAll('span', "hl to-search")
        for word in keyWords:
            allArticlKeyWords.append(word.contents[0].lower())
    authors = []
    for document in series_collection.find({"resources.keyWords": {"$in": allArticlKeyWords }}):
        count = 0 
        for resources in document["resources"]:
            if resources["keyWords"] != None:
                for keyWord in resources["keyWords"]:
                    if keyWord in allArticlKeyWords:
                        count += 1
        if count > 2:
            authors.append(document)             
    for author in authors:
        print(author["name"])
        # for resours in author["resources"]:
        #     print(resours["name"])

if __name__ == "__main__":   
    title = 'Выберете предпочитаемый метод: '
    options = ['Парсинг сайта УрФУ', 'Парсинг сохраненной раннее копии сайта', 'Поиск в киберленинке', 'Получить ключевые слова']
    option, index = pick(options, title)
    searchInCyberleninka()    
    if index == 0:
        parse()
    elif index == 1:
        parseFromCache()
    elif index == 2:
        searchInCyberleninka()    
    else:
        get_all_keywords(series_collection)
        for key, value in sorted(dictionary.items()):
            print("{0}: {1}".format(key,value))


