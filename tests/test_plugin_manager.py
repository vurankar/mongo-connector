# Copyright 2013-2014 MongoDB, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests methods in plugin_manager.py
"""
import sys

sys.path[0:0] = [""]

from mongo_connector.plugin_manager import (get_plugin_configs,
                                            docs_index_needed,
                                            resolve)
from tests import unittest
from tests.plugins.helpers import (get_test_namespace,
                                   get_test_supported_modules)


class TestPluginManager(unittest.TestCase):
    """ Tests the plugin manager.
    """

    def setUp(self):
        """Initialize test instance.
        """
        self.namespace = get_test_namespace()


    def test_get_plugin_configs(self):
        """Test get_plugin_configs."""
        configs = get_plugin_configs(self.namespace)
        self.assertEqual(len(configs), 4)
        self.assertTrue(len(self.namespace.plugins) > len(configs))

        for cfg in configs:
            self.assertTrue(cfg['pluginName'] != u'BadConfigPlugin')


    def test_docs_index_needed(self):
        """Test docs_index_needed."""
        configs = get_plugin_configs(self.namespace)
        self.assertTrue(docs_index_needed(configs))
        for cfg in configs:
            expectation = False
            if 'config' in cfg and 'options' in cfg['config']:
                options = cfg['config']['options']
                if 'indexDocs' in options:
                   expectation = options['indexDocs']

            docs_index = docs_index_needed(cfg)
            self.assertEqual(docs_index, expectation)
            docs_index = docs_index_needed([cfg])
            self.assertEqual(docs_index, expectation)


    def test_resolve(self):
        """Test resolve."""
        configs = get_plugin_configs(self.namespace)

        plugins = resolve(configs)
        self.assertEqual(len(plugins), 2)
        self.assertTrue(len(self.namespace.plugins) > len(plugins))

        plugins = resolve(configs[0:2])
        self.assertEqual(len(plugins), 2)

        supported = get_test_supported_modules()

        for cfg in configs:
            expectation = 0
            if 'moduleName' in cfg and cfg['moduleName'] in supported:
                expectation = 1

            cfg_plugins = resolve(cfg)
            self.assertEqual(len(cfg_plugins), expectation)
            cfg_plugins = resolve([cfg])
            self.assertEqual(len(cfg_plugins), expectation)


if __name__ == '__main__':

    unittest.main()
