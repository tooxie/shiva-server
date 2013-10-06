# -*- coding: utf-8 -*-
from shiva import get_version, get_contributors
from shiva.http import Resource, JSONResponse


class ClientResource(Resource):
    """ Resource that lists the known clients for Shiva. """

    def get(self):
        clients = [
            {
                'name': 'Shiva-Client',
                'uri': 'https://github.com/tooxie/shiva-client',
                'authors': [
                    u'Alvaro Mouriño <alvaro@mourino.net>',
                ],
            },
            {
                'name': 'Shiva4J',
                'uri': 'https://github.com/instant-solutions/shiva4j',
                'authors': [
                    u'instant:solutions <office@instant-it.at>'
                ],
            },
            {
                'name': 'Shakti',
                'uri': 'https://github.com/gonz/shakti',
                'authors': [
                    u'Gonzalo Saavedra <gonzalosaavedra@gmail.com>',
                ],
            },
        ]

        return clients


class AboutResource(Resource):
    """ Just some information about Shiva. """

    def get(self):
        info = {
            'name': 'Shiva',
            'version': get_version(),
            'author': u'Alvaro Mouriño <alvaro@mourino.net>',
            'uri': 'https://github.com/tooxie/shiva-server',
            'contributors': get_contributors(),
        }

        return info
