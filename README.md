# Тестовое задание API gateway  к openstack
Api написан на python3 в качестве WSGI HTTP сервера используется gunicorn.  
Потдерживает опреации:  
  1. Получить список (image,network,flavor,server).  
  2. Создать удалить остановить запустить сервер.  
  
Примеры запросов и ответов в docs.  
На тестовом сервере приложение расположено в директории /opt/test-api-gateway. 
Пароль от root и от панели управления не менял

**Пароли к wsgi и horizon находятся в /root/PASSWORDS**  
  
Создана virtualenv с установленными в нее зависимостиями.  
Для запуска приложения можно использовать скрипт <app_dir>/scripts/api-gateway.sh  
Пример  
```
./scripts/api-gateway.sh start
Starting api-gateway
Done
ps -axu | grep gunicorn
root     1548364  0.0  0.0  27276 19680 ?        S    17:26   0:00 /opt/test-api-gateway/env/bin/python /opt/test-api-gateway/env/bin/gunicorn --daemon --bind=0.0.0.0:8035 --pid=/var/run/api-gateway.pid --workers=3 --log-file=/var/log/api-gateway/api-gateway.log --access-logfile /var/log/api-gateway/access.log wsgi:app
root     1548366  0.9  0.1  50428 39956 ?        S    17:26   0:00 /opt/test-api-gateway/env/bin/python /opt/test-api-gateway/env/bin/gunicorn --daemon --bind=0.0.0.0:8035 --pid=/var/run/api-gateway.pid --workers=3 --log-file=/var/log/api-gateway/api-gateway.log --access-logfile /var/log/api-gateway/access.log wsgi:app
root     1548367  0.9  0.1  50428 39968 ?        S    17:26   0:00 /opt/test-api-gateway/env/bin/python /opt/test-api-gateway/env/bin/gunicorn --daemon --bind=0.0.0.0:8035 --pid=/var/run/api-gateway.pid --workers=3 --log-file=/var/log/api-gateway/api-gateway.log --access-logfile /var/log/api-gateway/access.log wsgi:app
root     1548368  0.9  0.1  50428 39960 ?        S    17:26   0:00 /opt/test-api-gateway/env/bin/python /opt/test-api-gateway/env/bin/gunicorn --daemon --bind=0.0.0.0:8035 --pid=/var/run/api-gateway.pid --workers=3 --log-file=/var/log/api-gateway/api-gateway.log --access-logfile /var/log/api-gateway/access.log wsgi:app

```
Либо можно запусить docker контейнер.  
Image собран и опубликован [https://hub.docker.com/r/testapigateway1/api](https://hub.docker.com/r/testapigateway1/api).  
Приложение слушает tcp порт 8035, пожно переопределить в api-gateway.sh.  
В контейнере параметры gunicorn можно переопрелить с кпмощью переменной окружения GUNICORN_CMD_ARGS.  

По умолчанию приложение пытается пройти аутентификаци на localhost.  
Переопредеить данное поведение можно изменив переменную окружения KEYSTONEHOST.  
Так же в директории с проектом создан docker-compose.yaml для более удобного запуска  

Примеры запуска контейнера  
```
docker run -e KEYSTONEHOST=192.168.0.2 -d  -p 8035:8035 testapigateway1/api
# В директории с проэктом
docker-compose up -d
```

У приложения должен быть доступ к сконфигурированным в openstack endpoints сервисов (neutron,nova,glance,keystone)  

```
openstack endpoint list
+----------------------------------+-----------+--------------+----------------+---------+-----------+----------------------------------------------+
| ID                               | Region    | Service Name | Service Type   | Enabled | Interface | URL                                          |
+----------------------------------+-----------+--------------+----------------+---------+-----------+----------------------------------------------+
| 04413fa8d10f41759c2a286f6eb2202a | RegionOne | glance       | image          | True    | public    | http://192.168.0.2/image                     |
| 1f40ab5ba7754a0e8c2442b655150572 | RegionOne | keystone     | identity       | True    | admin     | http://192.168.0.2/identity                  |
| cda84afd49214363b6fac415a2418878 | RegionOne | nova         | compute        | True    | public    | http://192.168.0.2/compute/v2.1              |
| e24dea6758a746f9940c834b049e863c | RegionOne | neutron      | network        | True    | public    | http://192.168.0.2:9696/                     |
| ffb26af3ef094c5dbd297985f6df049d | RegionOne | keystone     | identity       | True    | public    | http://192.168.0.2/identity                  |
+----------------------------------+-----------+--------------+----------------+---------+-----------+----------------------------------------------+
```

