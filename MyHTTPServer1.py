from __future__ import unicode_literals, absolute_import, print_function
import os
import logging
import asyncio
from httpserver import HttpProtocol

def _start_server(bindaddr, port, hostname, folder):
    """Starts an asyncio server"""
    loop = asyncio.get_event_loop()
    coroutine = loop.create_server(lambda: HttpProtocol(hostname, folder),
                                   bindaddr,
                                   port)
    print("type of coroutine = ", coroutine)
    server = loop.run_until_complete(coroutine)
    print('Starting server on {}'.format(server.sockets[0].getsockname()))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass

SERVER_HOST = '127.0.0.1'
SERVER_PORT = 8000
_start_server(SERVER_HOST, SERVER_PORT, 'localhost', os.getcwd())