#!env/bin/python
# -*- coding: utf-8 -*-
"""
Module for managing servers and flavors nova
"""
from novaclient import client
from novaclient.exceptions import BadRequest

__all__ = ["get_flavors", "get_servers", "create_server"]


def get_flavors(sess, flid=None):
    """
    The function generates a list of dicts describing the available flavors.
    If the flid parameter is passed, then the image is searched by id
    :param sess: Keystone session
    :param flid: str id of searched flavor
    :return: list of dicts flavors
    """

    result = []
    nova = client.Client(version='2', session=sess)
    if flid:
        tmp = [fl for fl in nova.flavors.list()
               if str(fl.id) == str(flid)]
    else:
        tmp = nova.flavors.list()

    for flavor in tmp:
        flavor = flavor.to_dict()
        result.append({"id": flavor["id"],
                       "name": flavor["name"],
                       "ram": flavor["ram"],
                       "disk": flavor["disk"],
                       "vcpus": flavor["vcpus"]})

    return result


def _del_unused_keys(*args):
    """
    Private function for delete
    unused keys from dict
    :param args: List of dicts for modify
    :return: None
    """
    for item in args:
        if "links" in item:
            item.pop("links")


def get_servers(sess, srvid=None):
    """
    The function generates a list of dicts describing the available servers.
    If the srvid parameter is passed, then the servers is searched by id
    :param sess: Keystone session
    :param srvid: str id of searched server
    :return: list of dicts flavors
    """
    result = []
    nova = client.Client(version='2', session=sess)
    if srvid:
        tmp = [srv for srv in nova.servers.list()
               if str(srv.id) == str(srvid)]
    else:
        tmp = nova.servers.list()
    for srv in tmp:
        srv = srv.to_dict()

        _del_unused_keys(srv["flavor"], srv["image"])

        result.append({"id": srv["id"],
                       "name": srv["name"],
                       "status": srv["status"],
                       "image": srv["image"],
                       "flavor": srv["flavor"],
                       "addresses": srv["addresses"]})
    return result


def create_server(sess, data):
    """
    The function creates a server by parameters from data
    raises novaclient.exceptions.BadRequest
    :param sess: Keystone session
    :param data: dict descibed server
    :return: dict {id:<created server id>}
    """
    reuired_data = ("server_name", "image_id", "flavor_id", "network_ids")
    no_in_data = [req_d for req_d in reuired_data if req_d not in data]
    if no_in_data:
        raise BadRequest(f"Not all required data is given '{no_in_data}'")
    if not data["network_ids"] or not isinstance(data["network_ids"], list):
        raise BadRequest("Network_ids must be not empty list")

    nova = client.Client(version='2', session=sess)
    servermanager = nova.servers
    networks = [{"net-id": net_id} for net_id in data["network_ids"]]
    createdserver = servermanager.create(data["server_name"],
                                         flavor=data["flavor_id"],
                                         image=data["image_id"],
                                         nics=networks)
    if createdserver:
        return {"id": createdserver.to_dict()["id"]}

    return dict()


def manage_server(sess, data):
    """
    The function for manage servers
    support stop start delete
    raises NotFound, BadRequest, Conflict
    :param sess: Keystone session
    :param data: dict descibed server and command
    :return: None
    """
    reuired_data = ("id", "action")
    no_in_data = [req_d for req_d in reuired_data if req_d not in data]
    if no_in_data:
        raise BadRequest(f"Not all required data is given '{no_in_data}'")
    nova = client.Client(version='2', session=sess)
    servermanager = nova.servers
    server = servermanager.get(data["id"])
    functios = {
        "delete": server.delete,
        "stop": server.stop,
        "start": server.start
        }
    try:
        func = functios[data["action"]]
        func()
    except KeyError:
        raise  BadRequest(f"Not allowed action {data['action']}") from KeyError
