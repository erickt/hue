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

import json
import os
import shutil
import tempfile

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal, assert_true, assert_false

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from desktop.lib.django_test_util import make_logged_in_client
from desktop.lib.test_utils import add_to_group, grant_access
from hadoop.pseudo_hdfs4 import is_live_cluster, get_db_prefix
from libzookeeper.conf import ENSEMBLE

from indexer.conf import CONFIG_TEMPLATE_PATH
from indexer.controller import get_solr_ensemble, CollectionManagerController


def test_get_ensemble():

  clear = ENSEMBLE.set_for_testing('zoo:2181')
  try:
    assert_equal('zoo:2181/solr', get_solr_ensemble())
  finally:
    clear()


  clear = ENSEMBLE.set_for_testing('zoo:2181,zoo2:2181')
  try:
    assert_equal('zoo:2181,zoo2:2181/solr', get_solr_ensemble())
  finally:
    clear()



class TestIndexerWithSolr:

  @classmethod
  def setup_class(cls):

    if not is_live_cluster():
      raise SkipTest()

    cls.client = make_logged_in_client(username='test', is_superuser=False)
    cls.user = User.objects.get(username='test')
    add_to_group('test')
    grant_access("test", "test", "indexer")

    resp = cls.client.post(reverse('indexer:install_examples'))
    content = json.loads(resp.content)

    assert_equal(content.get('status'), 0)

  @classmethod
  def teardown_class(cls):
    pass

  def test_is_solr_cloud_mode(self):
    assert_true(CollectionManagerController(self.user).is_solr_cloud_mode())

  def test_collection_exists(self):
    db = CollectionManagerController(self.user)
    assert_false(db.collection_exists('does_not_exist'))

  def test_get_collections(self):
    db = CollectionManagerController(self.user)
    db.get_collections()

  def test_create_collection(self):
    db = CollectionManagerController(self.user)

    test_schema = os.path.join(os.path.dirname(__file__), 'test_data', 'schema.xml')

    dirname = tempfile.mkdtemp()
    try:
      solrconfigs = os.path.join(dirname, 'solrconfigs')

      shutil.copytree(CONFIG_TEMPLATE_PATH.config.default, solrconfigs)
      shutil.copyfile(test_schema, os.path.join(solrconfigs, 'solrcloud', 'conf', 'schema.xml'))
      shutil.copyfile(test_schema, os.path.join(solrconfigs, 'nonsolrcloud', 'conf', 'schema.xml'))

      name = get_db_prefix(name='solr') + 'test_create_collection'
      fields = [{'name': 'my_test', 'type': 'text'}]

      resets = [
          CONFIG_TEMPLATE_PATH.set_for_testing(solrconfigs)
      ]

      try:
        db.create_collection(name, fields, unique_key_field='id', df='text')
        db.delete_collection(name, core=False)
      finally:
        for reset in resets:
          reset()
    finally:
      shutil.rmtree(dirname)


  def test_collections_fields(self):
    db = CollectionManagerController(self.user)

    db.get_fields('log_analytics_demo')
    resp = self.client.post(reverse('indexer:install_examples'))
    content = json.loads(resp.content)

    assert_equal(content.get('status'), 0)
