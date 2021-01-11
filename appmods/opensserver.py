#!env/bin/python
# -*- coding: utf-8 -*-
"""
Module for managing servers and flavors nova
"""
from novaclient import client

__all__ = ["OpenStackServer"]

class OpenStackServer:
    """
    Class for managing openstack servers and flavor
    """
    def __init__(self, sess):
        self.nova = client.Client(version='2', session=sess)


    def get_flavors(self, flid=None):
        """
        The method generates a list of dicts describing the available flavors.
        If the flid parameter is passed, then the image is searched by id
        :param flid: str id of searched flavor
        :return: list of dicts flavors
        """

        result = []
        if flid:
            tmp = [self.nova.flavors.get(flid)]
        else:
            tmp = self.nova.flavors.list()

        for flavor in tmp:
            flavor = flavor.to_dict()
            result.append({"id": flavor["id"],
                           "name": flavor["name"],
                           "ram": flavor["ram"],
                           "disk": flavor["disk"],
                           "vcpus": flavor["vcpus"]})

        return result


    @staticmethod
    def _del_unused_keys(*args):
        """
        Private method for delete
        unused keys from dict
        :param args: List of dicts for modify
        :return: None
        """
        for item in args:
            if "links" in item:
                del item["links"]


    def get_servers(self, srvid=None):
        """
        The method generates a list of dicts describing the available servers.
        If the srvid parameter is passed, then the servers is searched by id
        :param srvid: str id of searched server
        :return: list of dicts flavors
        """
        result = []
        if srvid:
            tmp = [self.nova.servers.get(srvid)]
        else:
            tmp = self.nova.servers.list()
        for srv in tmp:
            srv = srv.to_dict()

            self._del_unused_keys(srv["flavor"], srv["image"])

            result.append({"id": srv["id"],
                           "name": srv["name"],
                           "status": srv["status"],
                           "image": srv["image"],
                           "flavor": srv["flavor"],
                           "addresses": srv["addresses"]})
        return result


    def create_server(self, server_name, image_id, flavor_id, network_ids):
        """
        The method creates a server by parameters from data
        raises novaclient.exceptions.BadRequest
        :param server_name:
        :param image_id: str glance umage id
        :param flavor_id: str nova flavor id
        :param network_ids: list of str network ids
        :return: dict {id:<created server id>}
        """
        servermanager = self.nova.servers
        networks = [{"net-id": net_id} for net_id in network_ids]
        createdserver = servermanager.create(server_name,
                                             flavor=flavor_id,
                                             image=image_id,
                                             nics=networks)
        if createdserver:
            return {"srvid": createdserver.to_dict()["id"]}

        return dict()


    def manage_server(self, srvid, action):
        """
        The method for manage servers
        support stop, start, delete
        raises NotFound, Conflict
        :param srvid: str nova server id
        :param action: str delete stop start
        :return:
        """
        servermanager = self.nova.servers
        server = servermanager.get(srvid)
        functios = {
            "delete": server.delete,
            "stop": server.stop,
            "start": server.start
            }
        func = functios.get(action)
        if func:
            func()
