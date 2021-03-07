# encoding: utf-8

from flask import Blueprint
from flask import request
from flask import current_app
import requests
import configparser
from mkad import mkad_km
from shapely.geometry import Polygon, Point, LinearRing
import pyproj
from typing import List

Coordinate = List[float]



config = configparser.ConfigParser()
config.read('config.ini')

distance_bp = Blueprint('distance_bp', __name__)



class Geocoder:
	"""
	Используется для нахождении дистанции с заданного адреса до МКАДа в км
	входные данные: ключ разоаботчика Яндекс http геокодера и сам адрес
	вывод: дистанция в км
	"""
	def __init__(self, apikey: str, geocode: str) -> None:
		self.apikey = apikey
		self.geocode = geocode


	def get_coords(self) -> Coordinate:
		'''
		Возвращает координаты адреса [longitude, latitude]
		'''
		api = 'https://geocode-maps.yandex.ru/1.x/?format=json&apikey=' + self.apikey + '&geocode=' + self.geocode
		try:
			response =  requests.get(api).json()['response']
		except KeyError:
			response
			current_app.logger.info('Неправильный Yandex apikey')
		position = response['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
		coords = position.split(' ')
		coords = [float(coords[0]), float(coords[1])]
		return coords

	def mkad_contains_address(self) -> bool:
		"""
		Проверяет если адрес находится внутри МКАДа
		"""
		coords = self.get_coords()
		point = Point(coords)
		poly = Polygon(mkad_km)

		return poly.contains(point)


	def closest_point_to_mkad(self) -> List[Coordinate]:
		"""
		Показывает ближайшую точку до МКАДа
		"""
		coords = self.get_coords()
		point1 = Point(coords) # Создаём геометрический объект (точку) из полученных координат (yandex geocode)
		poly = Polygon(mkad_km) # Создаём геом. объект (полигон)
		pol_ext = LinearRing(poly.exterior.coords)
		d = pol_ext.project(point1)
		p = pol_ext.interpolate(d)
		closest = list(p.coords)[0]
		kms = ''
		for i, m in enumerate(mkad_km):
			if m == list(closest):
				kms = str(i+1)
				break


		current_app.logger.info('Самая ближайжая точка c кольцевой МКАДа до ' 
								+ self.geocode + ' - МКАД ' + kms + '-й километр.')

		return [coords, closest]

	def get_distance(self) -> str:
		"""
		Возвращает дистанцию с адреса до ближайшей точки МКАДа
		"""
		output: str = 'Дистанция '
		points = self.closest_point_to_mkad()

		point1 = Point(points[0])
		point2 = Point(points[1])

		geod = pyproj.Geod(ellps='WGS84')
		angle1, angle2, distance = geod.inv(point1.x, point1.y, point2.x, point2.y)

		output = output + "{0:8.3f}".format(distance/1000) + ' km'
		current_app.logger.info(output)

		return output




@distance_bp.route('<path:geocode>')
def index(geocode) -> str:
	output: str = 'Адрес находится внутри МКАДа. Введите другой адрес'

	apikey = config['geocode.api.key']['apikey']
	contains = request.args.get('contains')
	g = Geocoder(apikey, geocode)

	if contains == 'false':
		if g.mkad_contains_address():
			current_app.logger.info(output)
		else:
			output = g.get_distance()
	else:
		output = g.get_distance()



	
	return output

@distance_bp.route('/')
def info():
	return 'Введите ваш адрес с городом'


