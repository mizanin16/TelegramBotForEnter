Telegram бот для постановки задач в Flowlu


В переменных окружения надо проставить API токен бота.

`TELEGRAM_API_TOKEN` — API токен бота

Использование с Docker показано ниже. Предварительно заполните ENV переменные, указанные выше, в Dockerfile, а также в команде запуска укажите локальную директорию с проектом вместо `local_project_path`.

```
docker build -t tgfinance ./
docker run -d --name tg -v /local_project_path/db:/home/db tgfinance
```

Чтобы войти в работающий контейнер:

```
docker exec -ti tg bash
```

Войти в контейнере в SQL шелл:

```
docker exec -ti tg bash
sqlite3 /home/db/user.db
```


