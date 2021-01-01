#!env/bin/python
# -*- coding: utf-8 -*-
"""
Модуль для управления сетями neutron
"""
from neutronclient.v2_0 import client

__all__ = ["get_networks"]


def _get_subnets(idlist, neutron):
    """
    Функция для формирования списка доступных подсетей
    :param idlist: list список подсетей для поиска
    :param neutron: neutron client
    :return: list список словарей описывающих доступные подсети
    """
    result = []
    for netid in idlist:
        tmp = neutron.list_subnets(id=netid)["subnets"][0]
        result.append({"id": netid,
                       "name": tmp["name"],
                       'cidr': tmp["cidr"]})
    return result


def get_networks(sess, netid=None):
    """
    Функция формирует список доступных сетей neutron
    формирует список словарей описывающих доступые сети
    Если передается параметр netid, то происходит поиск сети по id
    :param sess: Keystone session
    :param netid: str id искомой сети
    :return: list список словарей описывающих сети
    """
    result = []
    neutron = client.Client(session=sess)
    if netid:
        networks = neutron.list_networks(id=netid)["networks"]
    else:
        networks = neutron.list_networks()["networks"]
    for net in networks:
        result.append({"id": net["id"],
                       'name': net["name"],
                       'status': net["status"],
                       'subnets': _get_subnets(net["subnets"], neutron)})
    return result
