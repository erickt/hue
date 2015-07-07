#!/usr/bin/env python
# Licensed to Cloudera, Inc. under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  Cloudera, Inc. licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket
import threading

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.handlers.wsgi import WSGIHandler
from django.test import testcases

from desktop import conf
from desktop.lib import wsgiserver

__all__ = (
    'create_server',
    'CherryPyServerThread',
)

def create_server(**kwargs):
  """
  Create a CherryPy WSGI server, which uses the Hue configuration options by
  default.
  """

  try:
    handler = kwargs['handler']
  except KeyError:
    handler = WSGIHandler()

  options = {
    'host': conf.HTTP_HOST.get(),
    'port': conf.HTTP_PORT.get(),
    'server_name': 'localhost',
    'threads': conf.CHERRYPY_SERVER_THREADS.get(),
    'daemonize': False, # supervisor does this for us
    'workdir': None,
    'pidfile': None,
    'server_user': conf.SERVER_USER.get(),
    'server_group': conf.SERVER_GROUP.get(),
    'ssl_certificate': conf.SSL_CERTIFICATE.get(),
    'ssl_private_key': conf.SSL_PRIVATE_KEY.get(),
    'ssl_cipher_list': conf.SSL_CIPHER_LIST.get()
  }

  options.update(kwargs)

  try:
    handler = options.pop('handler')
  except KeyError:
    handler = WSGIHandler()

  # Translogger wraps a WSGI app with Apache-style combined logging.
  server = wsgiserver.CherryPyWSGIServer(
      (options['host'], int(options['port'])),
      handler,
      int(options['threads']),
      options['server_name']
  )

  if options['ssl_certificate'] and options['ssl_private_key']:
      server.ssl_certificate = options['ssl_certificate']
      server.ssl_private_key = options['ssl_private_key']
      server.ssl_cipher_list = options['ssl_cipher_list']

      ssl_password = conf.get_ssl_password()
      if ssl_password:
          server.ssl_password_cb = lambda *unused: ssl_password

  return server


# Backported from Django 1.7.
class _MediaFilesHandler(StaticFilesHandler):
  """
  Handler for serving the media files. A private class that is meant to be
  used solely as a convenience by LiveServerThread.
  """

  def get_base_dir(self):
      return settings.MEDIA_ROOT

  def get_base_url(self):
      return settings.MEDIA_URL


# Backported from Django 1.7 and modified to work with CherryPy.
class CherryPyServerThread(threading.Thread):
  """
  Thread for running a live CherryPy http server while the tests are running.
  """

  def __init__(self, host, possible_ports, static_handler, connections_override=None):
    self.host = host
    self.port = None
    self.possible_ports = possible_ports
    self.is_ready = threading.Event()
    self.error = None
    self.static_handler = static_handler
    self.connections_override = connections_override
    super(CherryPyServerThread, self).__init__()


  def run(self):
    """
    Sets up the live server and databases, and then loops over handling http
    requests.
    """
    if self.connections_override:
      # Override this thread's database connections with the ones
      # provided by the main thread.
      for alias, conn in self.connections_override.items():
        connections[alias] = conn

    try:
      # Create the handler for serving static and media files
      handler = self.static_handler(_MediaFilesHandler(WSGIHandler()))

      # Go through the list of possible ports, hoping that we can find one that
      # is free to use for the WSGI server.
      for index, port in enumerate(self.possible_ports):
        try:
          httpd = create_server(
              host=self.host,
              port=port,
              handler=testcases.QuietWSGIRequestHandler
          )
          httpd.bind_server()
        except socket.error, e:
          if (index + 1 < len(self.possible_ports) and
              e.errno == errno.EADDRINUSE):
            # This port is already in use, so we gon on and try with the next
            # one in the list.
            continue
          else:
            # Either none of the given ports are free or the error is something
            # else than "Address already in use". So we let that error bubble
            # up to the main thread.
            raise
        else:
          # A free port was found.
          self.httpd = httpd
          self.port = port
          break

      self.httpd.wsgi_app = handler
      self.is_ready.set()
      self.httpd.listen_and_loop()
    except Exception, e:
      self.error = e
      self.is_ready.set()

  def terminate(self):
    if hasattr(self, 'httpd'):
      # Stop the WSGI server
      self.httpd.stop()
