#!env/bin/python
# -*- coding: utf-8 -*-
"""
Module for managing images glance
"""
from glanceclient import Client

__all__ = ["OpenSImage"]

# pylint: disable=R0903
class OpenSImage:
    """
    Class for managing openstack images
    """
    def __init__(self, sess):

        self.glance = Client('2', session=sess)


    def get_images(self, imageid=None):
        """
        The method generates a list of dicts describing the available images.
        If the imageid parameter is passed, then the image is searched by id
        :param imageid: str id searched image
        :return: list of dicts describes images
        """

        result = []
        if imageid:
            glanceimages = self.glance.images.list(id=imageid)
        else:
            glanceimages = self.glance.images.list()
        for image in glanceimages:
            result.append({"id": image["id"],
                           'status': image["status"],
                           'disk_format': image["disk_format"],
                           'container_format': image["container_format"]
                           })

        return result
