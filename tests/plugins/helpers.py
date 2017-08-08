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

"""Helper methods for plugins
"""
import sys

sys.path[0:0] = [""]

from mongo_connector.namespace_config import Namespace

TEST_MODULES = [u'mongo_connector.plugins.plugin_simulator',
                u'mongo_connector.plugins.update_elasticsearch_index']

TEST_PLUGIN_CONFIGS = [{
    u'pluginName': u'TestPlugin',
    u'moduleName': u'mongo_connector.plugins.plugin_simulator',
    u'className':  u'PluginSimulator',
    u'config': {
        u'index': u'ns1.resources',
        u'query': {
            u'key':  [u'_id'],
            u'xmap': {
                u'_id': u'/resourceId'
            }
        },
        u'update': {
            u'field': u'run_props',
            u'key':   u'propid',
            u'value': {
                u'type': u'dict',
                u'keys': [u'name', u'value']
            },
            u'xmap': {
                u'propid': u'/propertyId',
                u'name':   u'/propertyName',
                u'value':  u'/data/0/value'
            }
        },
        u'options': {
            u'indexDocs':    False,
            u'allowDeletes': True
        }
    }
},
{
    u'pluginName': u'UpdateElasticsearchIndex',
    u'moduleName': u'mongo_connector.plugins.update_elasticsearch_index',
    u'config': {
        u'index': u'ns1.resources',
        u'query': {
            u'key':  [u'_id'],
            u'xmap': {
                u'_id': u'/resourceId'
            }
        },
        u'update': {
            u'field': u'run_props',
            u'key':   u'propid',
            u'value': {
                u'type': u'dict',
                u'keys': [u'name', u'value']
            },
            u'xmap': {
                u'propid': u'/propertyId',
                u'name':   u'/propertyName',
                u'value':  u'/data/0/value'
            }
        },
        u'options': {
            u'indexDocs':    False,
            u'allowDeletes': True
        }
    }
},
{
    u'pluginName': u'BadConfigPlugin',
    u'moduleName': u'mongo_connector.plugins.update_elasticsearch_index'
},
{
    u'pluginName': u'NonExistentPlugin',
    u'moduleName': u'mongo_connector.plugins.does_not_exist',
    u'config': {
        u'index': u'ns1.something',
        u'options': {
            u'indexDocs':    True,
            u'allowDeletes': True
        }
    }
},
{
    u'pluginName': u'NoModuleAndNonExistentPlugin',
    u'config': {
        u'index': u'ns1.something',
        u'options': {
            u'indexDocs':    True,
            u'allowDeletes': True
        }
    }
}
]

BAD_PLUGIN_CONFIGS = [None, [], {}, {'foo': 1}, 1, 2.2, '3.33', 'four']

TEST_DOCS = [{
    '_id': 'one'
},
{
    '_id': 'two',
    'data': { 'value': 'jr' }
},
{
    '_id': 'three.0',
},
{
    '_id': 'four',
    'data': { 'value': { 'arr': [1.1, 2.2, 3.3], 'str': 'quad', 'd': 4.0}}
}]

BAD_DOCS = [None, [], {}, {'no_id': 'five'}, 1, 2.2, '3.33', 'four']

TEST_DOC_OPERATIONS = ['i', 'u', 'd', 'c']

BAD_OPERATIONS = ['x', 'y', 'z']


def get_test_namespace():
    """Returns the Namespace for testing plugins."""
    return Namespace(plugins=TEST_PLUGIN_CONFIGS)


def get_test_supported_modules():
    """Returns the plugin modules supported for testing purposes."""
    return TEST_MODULES
