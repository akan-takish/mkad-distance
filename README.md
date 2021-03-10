## Flask Blueprint приложения для нахождении расстоянии с заданного адреса до МКАД 



По http запросу передаётся адрес и находится дистанция до МКАД в км. Ответы логируются в distances.log файле




### Шаги к выполнению:

1) Нахождение координат адреса с помощью геокодирования (Яндекс API Геокодера):
https://yandex.ru/dev/maps/geocoder/doc/desc/concepts/about.html
2) Найти ближайшую точку от МКАД до заданного адреса
3) Рассчитать дистанцию от первой точки(заданного адреса) до ближайшей точки МКАД


### Основные технологии

- Flask - python фреймворк
- shapely, pyproj - python библиотека для геометрических задач с координатой адреса (yandex api geocoder)
- pytest - python библиотека для Unit тестов


### Установка

Используется версия python 3.7.10

git clone repository

```sh
git clone https://akantakish@bitbucket.org/akantakish/mkad-distance.git
```

Установка библиотек для python

```sh
cd mkad-distance
pip install -r requirements.txt
```
Для работы приложении необходим apikey. Нужно создать config.ini файл внутри папки для ключа Яндекс API Геокодера, внутри прописать:
```sh
[geocode.api.key]
apikey = ваш ключ Яндекс API Геокодера
```
_Ключ разработчика можно получить бесплатно при регистрации_ : https://developer.tech.yandex.ru/services/

### Запуск теста
```sh
pytest -vv
```

### Запуск приложения

```sh
flask run
```
Приложения запустится на 127.0.0.1:5000. Добавьте префикс _/address_ чтобы ввести адрес. Например: 127.0.0.1:5000/address/Караганда, степной 3. Ответ должен быть - Расстояния до МКАД с Караганда степной 3 - 2436.974 km. 

### Полезные ссылки
https://automating-gis-processes.github.io/site/


Akan Takish

