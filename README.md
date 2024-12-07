# AssinglyAPI #

## Основные запросы ##

То, что выделено большими буквами - параметры запроса

### Login ###

Запрос: 

`/login/?login=LOGIN&password=PASSWORD` 

Ответ:

```
{
    "id": user_id, - id пользователя 
    "token": auth_token - токен авторизации
}
```


## Зависимости: ##

- FastAPI

    `pip install fastapi`

- SQLAlchemy

    `pip install sqlalchemy`

- Unicorn 

    `pip install unicorn`

    `pip install "uvicorn[standard]"`

- Faker

    `pip install faker`

## Запуск: ##

  `uvicorn main:app --reload`

## Коллекция в Postman ##
https://www.postman.com/research-operator-5471098/workspace/assignlyapi/collection/40122979-dc7cdcb4-5442-41d3-95f4-9f62ad967a27?action=share&creator=40122979