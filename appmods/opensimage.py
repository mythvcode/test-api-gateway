#!env/bin/python
# -*- coding: utf-8 -*-
"""
Module for managing images glance
"""
from glanceclient import Client

__all__ = ["get_images"]


def get_images(sess, imageid=None):
    """
    The function generates a list of dicts describing the available images.
    If the imageid parameter is passed, then the image is searched by id
    :param sess: Keystone session
    :param imageid: str id searched image
    :return: list of dicts describes images
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
                       'container_format': image["container_format"]
                       })

    return result
