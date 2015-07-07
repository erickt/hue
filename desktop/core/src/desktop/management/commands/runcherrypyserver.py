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
# a thirdparty project

import sys, logging
from django.core.management.base import BaseCommand

from desktop import conf
from desktop.lib.daemon_utils import drop_privileges_if_necessary
from django.utils.translation import ugettext as _


CPSERVER_HELP = r"""
  Run Hue using the CherryPy WSGI server.
"""

class Command(BaseCommand):
    help = _("CherryPy Server for Desktop.")
    args = ""

    def handle(self, *args, **options):
        from django.conf import settings
        from django.utils import translation

        if not conf.ENABLE_SERVER.get():
          logging.info("Hue is configured to not start its own web server.")
          sys.exit(0)

        # Activate the current language, because it won't get activated later.
        try:
            translation.activate(settings.LANGUAGE_CODE)
        except AttributeError:
            pass
        runcpserver(args)

    def usage(self, subcommand):
        return CPSERVER_HELP


def start_server(options):
    """
    Start CherryPy server
    """
    from desktop.lib.cherrypy import create_server

    server = create_server(**options)

    try:
        server.bind_server()
        drop_privileges_if_necessary(options)
        server.listen_and_loop()
    except KeyboardInterrupt:
        server.stop()


def runcpserver(argset=[], **kwargs):
    # Get the options
    options = {}
    options.update(kwargs)
    for x in argset:
        if "=" in x:
            k, v = x.split('=', 1)
        else:
            k, v = x, True
        options[k.lower()] = v

    if "help" in options:
        print CPSERVER_HELP
        return

    # Start the webserver
    print _('starting server with options %(options)s') % {'options': options}
    start_server(options)


if __name__ == '__main__':
    runcpserver(sys.argv[1:])
