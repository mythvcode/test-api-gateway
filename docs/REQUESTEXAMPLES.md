#  Примеры запросов к api

В Openstack дожен быть создан пользователь от мимени которого api   
будет делать запросы.
Создан пользователь wsgi пароль находится в **/root/PASSWORDS**  

Структура ответа
```
{
  "data": [данные],
  "msg": "Сообщение либо все ок, либо что-то пошло не так"
  
}
```
Во всех запросах на получение flavor iamge server network можно указывать id по которому искать объект.  

## Запрос на получение списка сетей
```
curl -iu wsgi:***  http://77.223.100.94:8035/networks

HTTP/1.1 200 OK
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:29:38 GMT
Connection: close
Content-Type: application/json
Content-Length: 1219

{
  "data": [
    {
      "id": "31a9e6de-a6ec-47fb-91d2-08e3c767f4c0",
      "name": "private",
      "status": "ACTIVE",
      "subnets": [
        {
          "cidr": "10.0.0.0/26",
          "id": "98b2042d-7dfa-4794-bd3b-0698edbb4927",
          "name": "private-subnet"
        },
        {
          "cidr": "fd::/64",
          "id": "994248dd-3b3e-4e9c-99d5-c8e720d5f660",
          "name": "ipv6-private-subnet"
        }
      ]
    },

...
# запрос по id

curl -iu wsgi:***  http://77.223.100.94:8035/networks?id=77d2d954-9dcb-44a8-bc84-5e37aedd1fe9
HTTP/1.1 200 OK
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:32:52 GMT
Connection: close
Content-Type: application/json
Content-Length: 330

{
  "data": [
    {
      "id": "77d2d954-9dcb-44a8-bc84-5e37aedd1fe9",
      "name": "shared",
      "status": "ACTIVE",
      "subnets": [
        {
          "cidr": "192.168.233.0/24",
          "id": "95280ed8-629f-4bab-ad24-91ffcccb531d",
          "name": "shared-subnet"
        }
      ]
    }
  ],
  "msg": "OK"
}

```

## Запрос на получение списка серверов
```
 curl -iu wsgi:***  http://77.223.100.94:8035/servers
HTTP/1.1 200 OK
...
    {
      "addresses": {
        "private": [
          {
            "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b3:f6:ff",
            "OS-EXT-IPS:type": "fixed",
            "addr": "10.0.0.29",
            "version": 4
          },
          {
            "OS-EXT-IPS-MAC:mac_addr": "fa:16:3e:b3:f6:ff",
            "OS-EXT-IPS:type": "fixed",
            "addr": "fd::f816:3eff:feb3:f6ff",
            "version": 6
          }
        ]
      },
      "flavor": {
        "id": "1"
      },
      "id": "bbcb825c-59d0-4109-b136-bea9094456a6",
      "image": {
        "id": "b3de6eac-2f6c-4f7f-be94-ddd7876d1ddf"
      },
      "name": "test_script3",
      "status": "ACTIVE"
    }

curl -iu wsgi:***  http://77.223.100.94:8035/servers?id=bbcb825c-59d0-4109-b136-bea9094456a6
HTTP/1.1 200 OK
....
```
## Список flavors
```
curl -iu wsgi:***  http://77.223.100.94:8035/flavors
HTTP/1.1 200 OK
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:37:25 GMT
Connection: close
Content-Type: application/json
Content-Length: 1400

{
  "data": [
    {
      "disk": 1,
      "id": "1",
      "name": "m1.tiny",
      "ram": 512,
      "vcpus": 1
    },
...

 curl -iu wsgi:***  http://77.223.100.94:8035/flavors?id=1
HTTP/1.1 200 OK
...
```

## Список images

```
 curl -iu wsgi:***  http://77.223.100.94:8035/images
HTTP/1.1 200 OK
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:38:42 GMT
Connection: close
Content-Type: application/json
Content-Length: 192

{
  "data": [
    {
      "container_format": "bare",
      "disk_format": "qcow2",
      "id": "b3de6eac-2f6c-4f7f-be94-ddd7876d1ddf",
      "status": "active"
    }
  ],
  "msg": "OK"
}

curl -iu wsgi:***  http://77.223.100.94:8035/images?id=b3de6eac-2f6c-4f7f-be94-ddd7876d1ddf
HTTP/1.1 200 OK
```

## Создание сервера.  
В ответ посылается  id созданного сервера
В network_ids должен быть список хотя бы с одной сетью.
```
curl -iu wsgi:***  -H "Content-Type: application/json" \
-X POST -d '{"server_name": "super_server1",
"image_id": "b3de6eac-2f6c-4f7f-be94-ddd7876d1ddf",
"flavor_id": "1", "network_ids":["77d2d954-9dcb-44a8-bc84-5e37aedd1fe9"]}'\
 http://77.223.100.94:8035/create_server

HTTP/1.1 201 CREATED
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:43:12 GMT
Connection: close
Content-Type: application/json
Content-Length: 85

{
  "data": {
    "id": "5c210e96-7d5f-45cd-81e7-52c81087e4f5"
  },
  "msg": "OK"
}
```

Выколючение включение сервера

```
# Выключить
 curl -iu wsgi:***  -H "Content-Type: application/json" \
 -X POST -d '{"id": "5c210e96-7d5f-45cd-81e7-52c81087e4f5", "action": "stop"}'\
  http:/77.223.100.94:8035/manage_server
HTTP/1.1 202 ACCEPTED
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:46:25 GMT
Connection: close
Content-Type: application/json
Content-Length: 18

{
  "msg": "OK"
}

# Включить
curl -iu wsgi:***  -H "Content-Type: application/json" \
-X POST -d '{"id": "5c210e96-7d5f-45cd-81e7-52c81087e4f5", "action": "start"}'\
 http:/77.223.100.94:8035/manage_server
HTTP/1.1 202 ACCEPTED
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:48:10 GMT
Connection: close
Content-Type: application/json
Content-Length: 18

{
  "msg": "OK"
}

```

## Удалить сервер
```
curl -iu wsgi:***  -H "Content-Type: application/json" \
 -X POST -d '{"id": "5c210e96-7d5f-45cd-81e7-52c81087e4f5", "action": "delete"}'\
  http:/77.223.100.94:8035/manage_server
HTTP/1.1 202 ACCEPTED
Server: gunicorn/20.0.4
Date: Mon, 04 Jan 2021 18:52:15 GMT
Connection: close
Content-Type: application/json
Content-Length: 18

{
  "msg": "OK"
}
```

