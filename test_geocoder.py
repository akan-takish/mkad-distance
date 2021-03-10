# encoding: utf-8

import pytest

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_address(client):
    rv = client.get("/address/Москва, Тверская 6")
    assert b"15.472" == rv.data


def test_main_page(client):
	res = client.get('/address/')
	assert 'Введите ваш адрес с городом'.encode() == res.data


def test_wrong_address(client):
	res = client.get('/address/-122')
	assert 'Неправильный адрес, укажите адрес с городом'.encode() == res.data


def test_inner_false(client):
	res = client.get('/address/Москва, Тверская 6?inner=false')
	assert 'Адрес находится внутри МКАДа. Введите другой адрес'.encode() == res.data
