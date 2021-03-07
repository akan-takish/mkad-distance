# encoding: utf-8
# Third party modules

import pytest

# First party modules
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_geocode(client):
    rv = client.get("/address/Москва, Тверская 6")
    assert b"15.472" == rv.data


def test_address(client):

	rv = client.get('/address/')

	assert rv.status_code == 200
	# assert b"Введите ваш адрес с городом" in rv.data

def test_fake_address(client):
	res = client.get('/address/-122')

	assert res.status_code == 200

def test_main_page(client):
	res = client.get('/')