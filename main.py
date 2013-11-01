# -*- coding: utf-8 -*-
__doc__ = """
Module to host a Django application from within a CherryPy server.

Instead of creating a clone to `runserver` like other similar
packages do, we simply setup and host the Django application
using WSGI and CherryPy's capabilities to serve it.

In order to configure the application, we use the `settings.configure(...)`
function provided by Django.

Since the CherryPy WSGI server doesn't offer a log
facility, we add a straightforward WSGI middleware to do so, based
on the CherryPy built-in logger. Obviously any other log middleware
can be used instead.

For some extra fun we demonstrate how to add WebSocket support
to your Django application. This requires ws4py:

https://github.com/Lawouach/WebSocket-for-Python

Note this application admin site uses the following credentials:
admin/admin

Thanks to Damien Tougas for his help on this recipe.
"""
PORT = 8090
#IP_ADDRESS = "192.168.0.103"
#IP_ADDRESS = "localhost"
IP_ADDRESS = "127.0.0.1"
#IP_ADDRESS = "142.143.160.33"
PROJECT_SETTINGS = "main.settings.production"

if __name__ == '__main__':
    import cherrypy
    cherrypy.config.update({'server.socket_port': PORT,
                            'server.socket_host': IP_ADDRESS,
                            'checker.on': False})

    from djangoplugin import DjangoAppPlugin
    DjangoAppPlugin(cherrypy.engine,
                    settings_module=PROJECT_SETTINGS).subscribe()

    from ws4py.server.cherrypyserver import WebSocketPlugin
    WebSocketPlugin(cherrypy.engine).subscribe()

    cherrypy.quickstart()
