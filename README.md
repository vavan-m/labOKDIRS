# labOKDIRS
Парсинг порталов информационно-образовательных ресурсов с целью получить информацию о публикациях авторов  
____
В файле [parse_UrFU.py](https://github.com/vavan-m/labOKDIRS/blob/master/parse_UrFU.py) содержится код для парсинга с [сайта](https://study.urfu.ru).
Информация о публикациях сохраняется в MongoDB.  
HTML страницы, с которых осуществлялся, парсинг сохраняются в директорию cache.  
Порядок работы с программой:
1. Запуск программы в командной строке;
2. Выбрать действие в интерактивном списке выбора.

UPDATE
Добавлен поиск специалистов в СУБД. 
1. Запустить программу, выбрать "Поиск в киберленинке"
2. Ввести описание исследования
3. Получить список специалистов, способных помочь в реализации проекта 
____
Выполнили: Машанов Владимир (commit author: vladimir.mashan, vavan-m) vladimir.mashan@gmail.com,  
Максим Торопицын (commit author: Max-serrro)  
Студенты группы РИС-21-1м   
