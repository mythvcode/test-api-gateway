#!env/bin/python
# -*- coding: utf-8 -*-
"""
Neutron network management module
"""
from neutronclient.v2_0 import client

__all__ = ["get_networks"]


def _get_subnets(idlist, neutron):
    """
    Function to form a list of available subnets

    :param idlist:  list of subnets to search
    :param neutron: neutron client
    :return: list list of dicts describing available subnets
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
    The function generates a list of available neutron networks
    If the netid parameter is passed, then the network is searched by id
    :param sess: Keystone session
    :param netid: str network id
    :return: list  of dicts describing networks
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
