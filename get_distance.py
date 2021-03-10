from flask import Blueprint
from flask import request
from flask import current_app
import requests
import configparser
from mkad import mkad_km
from shapely.geometry import Polygon, Point, LinearRing, LineString
from shapely.ops import nearest_points
import pyproj
from typing import List


Coordinate = List[float]


config = configparser.ConfigParser()
config.read('config.ini')


distance_bp = Blueprint('distance_bp', __name__)


class Geocoder:
	"""	
	Используется для нахождении дистанции с заданного адреса до МКАДа в км
	входные данные: 
	1) 	ключ разработчика Яндекс http геокодера(apikey)
	2) 	адрес(geocode), 
	3)	параметр inner, если "false" то адреса внутри МКАДа не учитывает, 
		если 'true' то находит дистанцию (default)
	"""

	def __init__(self, apikey: str, geocode: str, inner: bool) -> None:
		self.apikey = apikey
		self.geocode = geocode
		self.inner = inner


	def get_coords(self) -> Coordinate:
		'''
		Возвращает координаты адреса [longitude, latitude]
		'''
		api = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey=' + self.apikey + '&geocode=' + self.geocode
		response =  requests.get(api).json()['response']
		position = response['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
		
		coords = position.split(' ')
		coords = [float(coords[0]), float(coords[1])]
		return coords


	def closest_point_to_mkad(self) -> List[Coordinate]:
		"""
		Возвращает координату адреса и его ближайшую точку до МКАДа
		"""

		coords = self.get_coords()
		point = Point(coords) # Создаём геометрический объект (точку) из полученных координат (yandex geocoder)
		poly = Polygon(mkad_km) # Создаём геом. объект (полигон)

		# Находит ближайшую точку 
		pol_ext = LinearRing(poly.exterior.coords)
		d = pol_ext.project(point)
		p = pol_ext.interpolate(d) 
		closest = list(p.coords)[0]
		kms = ''
		for i, m in enumerate(mkad_km):
			if m == list(closest):
				kms = str(i+1)
				break


		current_app.logger.info('Самая ближайжая точка c кольцевой МКАД до ' 
								+ self.geocode + ' - МКАД ' + kms + '-й километр.')

		return [coords, closest]

	def get_distance(self) -> str:
		"""
		Возвращает дистанцию с адреса до ближайшей точки МКАДа
		"""

		output: str = 'Расстояния до МКАД с ' + self.geocode + ' - '


		points = self.closest_point_to_mkad()
		point1 = Point(points[0])
		point2 = Point(points[1])
		poly = Polygon(mkad_km)
		line = LineString(mkad_km)


		if self.inner == False and poly.contains(point1):
			output = 'Адрес находится внутри МКАД. Введите другой адрес'
		elif line.contains(point1):
			output = 'Адрес находится вдоль МКАД'	
		else:
			geod = pyproj.Geod(ellps='WGS84')
			angle1, angle2, distance = geod.inv(point1.x, point1.y, point2.x, point2.y) 
			output = output + "{0:8.3f}".format(distance/1000) + ' km'
		
		current_app.logger.info(output)


		return output




@distance_bp.route('<path:geocode>')
def index(geocode) -> str:
	output: str = 'Адрес находится внутри МКАД. Введите другой адрес'

	apikey = config['geocode.api.key']['apikey']
	inner = request.args.get('inner') # Если добавить параметр inner с аргументом false 
	

	if inner == 'false':
		g = Geocoder(apikey, geocode, inner=False)
	else:
		g = Geocoder(apikey, geocode, inner=True)
	
	# out = g.get_distance()
	try:
		output = g.get_distance()
	except IndexError:
		output = 'Неправильный адрес, укажите адрес с городом'
	except KeyError:
		output = 'Неправильный ключ Яндекс API геокодера'


	return output

@distance_bp.route('/')
def info():
	return 'Введите ваш адрес с городом'


