#!env/bin/python
# -*- coding: utf-8 -*-
"""
Модуль для управления images glance
В далнейшем может быть функционал модет быть расширен
методами создания удаления конфигурации образов
"""
from glanceclient import Client

__all__ = ["get_images"]

def get_images(sess, imageid=None):
    """
    Функция формирует список словарей описывающих доступые образы.
    Если передается параметр imageid, то происходит поиск образа по id
    :param sess: Keystone session
    :param netid: str id искомого образа
    :return: list список словарей описывающих сети
    """

    result = []
    glance = Client('2', session=sess)
    if imageid:
        glanceimages = glance.images.list(id=imageid)
    else:
        glanceimages = glance.images.list()
    for image in glanceimages:
        result.append({"id": image["id"],
            'status': image["status"],
            'disk_format': image["disk_format"],
            'container_format':image["container_format"]
            })

    return result
