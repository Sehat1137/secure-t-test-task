# secure-t-test-task

### env file
```shell
POSTGRES_DB=postcommentdb
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_USER=postcommentdb
POSTGRES_PASSWORD=qwerty123
```

### Run app
```shell
docker-compose up
```
When we run this command, our app is available 127.0.0.1:8080

### Docs
```
http://127.0.0.1:8080/redoc
http://127.0.0.1:8080/docs
http://127.0.0.1:8080/openapi.json
```

### Run tests
```shell
docker exec -it secure-t-test-task pytest tests/ --disable-warnings
```

### Task description
```
# Тестовое задание Python

Необходимо разработать API с системой древовидных комментариев (как на reddit.com).

## Функциональность

- Регистрация/авторизация пользователей
- CRUD постов
- CRUD комментариев (комментарии привязываются либо к посту, либо к другому комментарию)
- Список полей в моделях на ваше усмотрение
- Приветствуется реализация дополнительного функционала

Можно выбрать любой фрейворк, но будет плюсом использование FastAPI.
В качестве БД желательно использовать PostgreSQL.
```