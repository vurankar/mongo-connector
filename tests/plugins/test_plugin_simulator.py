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

"""Tests methods in plugin_base.py
"""
import copy
import sys

sys.path[0:0] = [""]

from mongo_connector.plugins.plugin_simulator import PluginSimulator
from tests import unittest
from tests.plugins.helpers import (BAD_PLUGIN_CONFIGS,
                                   TEST_DOCS,
                                   BAD_DOCS,
                                   TEST_DOC_OPERATIONS,
                                   BAD_OPERATIONS,
                                   get_test_namespace)


class PluginSimulatorTest(unittest.TestCase):
    """ Tests the PluginSimulator.
    """

    def setUp(self):
        """Initialize test instance.
        """
        self.configs = copy.deepcopy(BAD_PLUGIN_CONFIGS)
        for cfg in get_test_namespace().plugins:
            if 'className' in cfg and cfg['className'] == 'PluginSimulator':
                self.configs.append(cfg)


    def test_instantiate(self):
        """Test creation.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            self.assertFalse(plugin.is_committed())
            self.assertFalse(plugin.is_stopped())


    def test_is_stopped(self):
        """Test is_stopped.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            self.assertFalse(plugin.is_stopped())
            plugin.commit()
            self.assertFalse(plugin.is_stopped())
            plugin.stop()
            self.assertTrue(plugin.is_stopped())


    def test_is_committed(self):
        """Test is_committed.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            self.assertFalse(plugin.is_committed())
            plugin.stop()
            self.assertFalse(plugin.is_committed())
            plugin.commit()
            self.assertTrue(plugin.is_committed())


    def test_invoke(self):
        """Test invoke.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            for doc in TEST_DOCS:
                for op in TEST_DOC_OPERATIONS:
                    self.assertIsNotNone(plugin.invoke(op, doc, {}))
                    ops = plugin.find_ops(doc['_id'])
                    lastop = ops.pop()
                    self.assertEqual(lastop['op'], op)
                    self.assertEqual(lastop['doc'], doc)

                for op in BAD_OPERATIONS:
                    self.assertIsNotNone(plugin.invoke(op, doc, {}))

            for doc in BAD_DOCS:
                for op in TEST_DOC_OPERATIONS:
                    self.assertIsNone(plugin.invoke(op, doc, {}))

                for op in BAD_OPERATIONS:
                    self.assertIsNone(plugin.invoke(op, doc, {}))


    def test_commit(self):
        """Test commit.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            self.assertFalse(plugin.is_committed())
            plugin.commit()
            self.assertTrue(plugin.is_committed())


    def test_stop(self):
        """Test stop.
        """
        for cfg in self.configs:
            plugin = PluginSimulator(cfg)
            self.assertIsNotNone(plugin)
            self.assertFalse(plugin.is_stopped())
            plugin.stop()
            self.assertTrue(plugin.is_stopped())


if __name__ == '__main__':

    unittest.main()
