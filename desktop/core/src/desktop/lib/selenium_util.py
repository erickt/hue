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

import errno
import os
import socket
import threading

from django.conf import settings
from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.core.handlers.wsgi import WSGIHandler
from django.db import connection, connections
from django.test import testcases
from django.utils.module_loading import import_by_path
from django.utils.translation import ugettext as _

from nose.plugins.skip import SkipTest

from desktop.lib import cherrypy


__all__ = (
    'CherryPyServerTestCase',
    'HueLiveServerTestCase',
)


class CherryPyServerTestCase(testcases.TransactionTestCase):
    """
    Does basically the same as TransactionTestCase but also launches a live
    http server in a separate thread so that the tests may use another testing
    framework, such as Selenium for example, instead of the built-in dummy
    client.
    Note that it inherits from TransactionTestCase instead of TestCase because
    the threads do not share the same transactions (unless if using in-memory
    sqlite) and each thread needs to commit all their transactions so that the
    other thread can see the changes.
    """

    static_handler = StaticFilesHandler

    @property
    def live_server_url(self):
        return 'http://%s:%s' % (
            self.server_thread.host, self.server_thread.port)

    @classmethod
    def setUpClass(cls):
        super(CherryPyServerTestCase, cls).setUpClass()
        connections_override = {}
        for conn in connections.all():
            # If using in-memory sqlite databases, pass the connections to
            # the server thread.
            if (conn.settings_dict['ENGINE'].rsplit('.', 1)[-1] in ('sqlite3', 'spatialite')
                and conn.settings_dict['NAME'] == ':memory:'):
                # Explicitly enable thread-shareability for this connection
                conn.allow_thread_sharing = True
                connections_override[conn.alias] = conn

        # Launch the live server's thread
        specified_address = os.environ.get(
            'DJANGO_LIVE_TEST_SERVER_ADDRESS', 'localhost:8081')

        # The specified ports may be of the form '8000-8010,8080,9200-9300'
        # i.e. a comma-separated list of ports or ranges of ports, so we break
        # it down into a detailed list of all possible ports.
        possible_ports = []
        try:
            host, port_ranges = specified_address.split(':')
            for port_range in port_ranges.split(','):
                # A port range can be of either form: '8000' or '8000-8010'.
                extremes = list(map(int, port_range.split('-')))
                assert len(extremes) in [1, 2]
                if len(extremes) == 1:
                    # Port range of the form '8000'
                    possible_ports.append(extremes[0])
                else:
                    # Port range of the form '8000-8010'
                    for port in range(extremes[0], extremes[1] + 1):
                        possible_ports.append(port)
        except Exception:
            msg = 'Invalid address ("%s") for live server.' % specified_address
            six.reraise(ImproperlyConfigured, ImproperlyConfigured(msg), sys.exc_info()[2])
        cls.server_thread = cherrypy.ServerThread(host, possible_ports,
                                                  cls.static_handler,
                                                  connections_override=connections_override)
        cls.server_thread.daemon = True
        cls.server_thread.start()

        # Wait for the live server to be ready
        cls.server_thread.is_ready.wait()
        if cls.server_thread.error:
            # Clean up behind ourselves, since tearDownClass won't get called in
            # case of errors.
            cls._tearDownClassInternal()
            raise cls.server_thread.error

    @classmethod
    def _tearDownClassInternal(cls):
        # There may not be a 'server_thread' attribute if setUpClass() for some
        # reasons has raised an exception.
        if hasattr(cls, 'server_thread'):
            # Terminate the live server's thread
            cls.server_thread.terminate()
            cls.server_thread.join()

        # Restore sqlite in-memory database connections' non-shareability
        for conn in connections.all():
            if (conn.settings_dict['ENGINE'].rsplit('.', 1)[-1] in ('sqlite3', 'spatialite')
                and conn.settings_dict['NAME'] == ':memory:'):
                conn.allow_thread_sharing = False

    @classmethod
    def tearDownClass(cls):
        cls._tearDownClassInternal()
        super(CherryPyServerTestCase, cls).tearDownClass()




class HueLiveServerTestCase(CherryPyServerTestCase):

  webdriver_class = 'selenium.webdriver.firefox.webdriver.WebDriver'

  @classmethod
  def setUpClass(cls):
    if not os.environ.get('HUE_SELENIUM_TESTS', False):
      raise SkipTest('Selenium tests are not enabled')

    try:
      cls.selenium = import_by_path(cls.webdriver_class)()
    except Exception, e:
      raise SkipTest(
          'Selenium webdriver "%s" not installed or not operational' %
          (cls.webdriver_class, str(e)))

    super(HueLiveServerTestCase, cls).setUpClass()

  @classmethod
  def tearDownClass(cls):
    if hasattr(cls, 'selenium'):
      cls.selenium.quit()

    super(HueLiveServerTestCase, cls).tearDownClass()

  def wait_until(self, callback, timeout=10):
    from selenium.webdriver.support.wait import WebDriverWait
    WebDriverWait(self.selenium, timeout).until(callback)

  def wait_for(self, css_selector, timeout=10):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions
    self.wait_until(
      expected_conditions.presence_of_element_located((By.CSS_SELECTOR, css_selector)),
      timeout)

  def wait_page_loaded(self):
    from selenium.common.exceptions import TimeoutException
    try:
      self.wait_for('body')
    except TimeoutException:
      pass

  def logged_in_client(self, user='test', passwd='test'):
    self.selenium.get(self.live_server_url)

    #if self.execute_script("!!$('hue-login')")["output"]:
    #  self.wait_for('#id_username')
    username_input = self.selenium.find_element_by_id('id_username')
    username_input.send_keys(user)
    #  self.wait_for('#id_password')

    password_input = self.selenium.find_element_by_id('id_password')
    password_input.send_keys(passwd)

    login_text = _('Create account')
    self.selenium.find_element_by_xpath('//input[@value="%s"]' % login_text).click()

    self.wait_page_loaded()

  def logout(self):
    self.selenium.find_element_by_xpath('//a[@href="/accounts/logout/"]').click()
