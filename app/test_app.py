import os
import pytest
from app import app, db
from app.models import Client
import io


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<div class="button-container">' in response.data





def test_login(client):
    # Создание тестового клиента
    test_client = Client(
        login='testuser',
        email='testuser@example.com',
        name='Test',
        surname='User',
        work_age=5
    )
    test_client.set_password('testpass')
    with app.app_context():
        db.session.add(test_client)
        db.session.commit()

    # 1. Успешный вход
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'testpass',
        'remember_me': True
    })
    assert response.status_code == 302  # проверяем перенаправление после успешного входа
    assert response.location.endswith('/home')

    # 2. Неверный логин
    response = client.post('/login', data={
        'login': 'testuser',
        'password': 'wrongpassword',
        'remember_me': True
    })
    assert response.status_code == 302  # проверяем перенаправление

    # неверный логин (пользователь не существует)
    response = client.post('/login', data={
        'login': 'nonexistentuser',
        'password': 'somepassword',
        'remember_me': True
    })
    assert response.status_code == 302  # Проверяем перенаправление


