#!env/bin/python
# -*- coding: utf-8 -*-
"""
Neutron network management module
"""
from neutronclient.v2_0 import client

__all__ = ["OpenSNet"]

# pylint: disable=R0903
class OpenSNet:
    """
    Class for managing openstack networks
    """
    def __init__(self, sess):
        self.neutron = client.Client(session=sess)


    def _get_subnets(self, idlist):
        """
        Method to form a list of available subnets

        :param idlist:  list of subnets to search
        :return: list list of dicts describing available subnets
        """
        result = []
        for netid in idlist:
            tmp = self.neutron.list_subnets(id=netid)["subnets"]
            if tmp:
                tmp = tmp[0]
            else:
                tmp = {"name": "", "cidr": ""}
            result.append({"id": netid,
                           "name": tmp["name"],
                           'cidr': tmp["cidr"]})
        return result


    def get_networks(self, netid=None):
        """
        The Method generates a list of available neutron networks
        If the netid parameter is passed, then the network is searched by id
        :param netid: str network id
        :return: list  of dicts describing networks
        """
        result = []
        if netid:
            networks = self.neutron.list_networks(id=netid)["networks"]
        else:
            networks = self.neutron.list_networks()["networks"]
        for net in networks:
            result.append({"id": net["id"],
                           'name': net["name"],
                           'status': net["status"],
                           'subnets': self._get_subnets(net["subnets"])})
        return result
