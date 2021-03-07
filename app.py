# encoding: utf-8

from flask import Flask
import logging
from get_distance import distance_bp

app = Flask(__name__)

logging.basicConfig(filename='distances.log', level=logging.INFO,
					format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')

app.register_blueprint(distance_bp, url_prefix='/address')


