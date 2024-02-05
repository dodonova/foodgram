#  Проект Foodgram

## Описание проекта

Проект Foodgram - это сервис для размещения и обмена рецептами.

Сервис размещен по адресу: https://try-foodgram.ddns.net

## Как развернуть проект на своем сервере
1. Установить веб-сервер nginx
2. На сервере создать папку `foodgram`
3. В папку скопировать файл [docker-compose.production.yml](https://github.com/dodonova/kittygram_final/blob/main/docker-compose.production.yml)
4. В этой же папке создать файл `.env` в котором разместить информацию о переменных окружения. Пример в файле [.env.example](https://github.com/dodonova/kittygram_final/blob/main/.env.example)
5. Отредактировать конфигурацию `nginx sudo nano /etc/nginx/sites-enabled/default` :
```
server { 
  server_name IP-адрес-сервера ваше-доменное-имя; 
  location / { 
    proxy_pass http://127.0.0.1:8000; 
  }
}
```
6. Проверить конфигурацию nginx: 
```
sudo nginx -t
```
7. Запустить Docker Compose на сервере в папке c проектом: 
```
sudo docker compose -f docker-compose.production.yml up -d
```
8. Выполнить миграции: 
```
sudo docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```
9. Собрать статику: 
 ```
 sudo docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic 
 ```
10. Перезапустить nginx: 
```
sudo systemctl restart nginx
``` 