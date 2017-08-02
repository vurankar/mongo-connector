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

from mongo_connector.plugins.plugin_base import PluginBase
from tests import unittest
from tests.plugins.helpers import (BAD_PLUGIN_CONFIGS, get_test_namespace)


class TestPluginBase(unittest.TestCase):
    """ Tests the utils
    """

    def setUp(self):
        """Initialize test instance.
        """
        self.namespace = get_test_namespace()


    def test_name(self):
        """Test name.
        """
        configs = self.namespace.plugins[0]
        for cfg in configs:
            obj = PluginBase(cfg)
            self.assertEqual(cfg['pluginName'], obj.name())

        for cfg in BAD_PLUGIN_CONFIGS:
            obj = PluginBase(cfg)
            self.assertEqual(obj.name().index('generated'), 0)


    def test_info(self):
        """Test info.
        """
        configs = self.namespace.plugins[0]
        for cfg in configs:
            obj = PluginBase(cfg)
            self.assertEqual(cfg['config'], obj.info())

        for cfg in BAD_PLUGIN_CONFIGS:
            obj = PluginBase(cfg)
            self.assertEqual(obj.info(), {})


    def _test_not_implemented_method_by_name(self, name):
        """Test not implemented method by name.
        """
        configs = copy.deepcopy(self.namespace.plugins)
        configs.extend(BAD_PLUGIN_CONFIGS)
        for cfg in configs:
            obj = PluginBase(cfg)
            try:
                method = getattr(obj, name)
                if not method or not callable(method):
                    raise KeyError

                method()

            except NotImplementedError as exc:
                pass

        return True


    def test_invoke(self):
        """Test invoke.
        """
        flag = self._test_not_implemented_method_by_name('invoke')
        self.assertEqual(flag, True)


    def test_bulk_invoke(self):
        """Test bulk_invoke.
        """
        # Bulk invoke is really implemented but it calls invoke in loop
        # which returns an not implemented exception.
        flag = self._test_not_implemented_method_by_name('bulk_invoke')
        self.assertEqual(flag, True)


    def test_commit(self):
        """Test commit.
        """
        flag = self._test_not_implemented_method_by_name('commit')
        self.assertEqual(flag, True)


    def test_stop(self):
        """Test stop.
        """
        flag = self._test_not_implemented_method_by_name('stop')
        self.assertEqual(flag, True)


if __name__ == '__main__':

    unittest.main()
