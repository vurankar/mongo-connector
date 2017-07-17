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

import copy

from mongo_connector.plugins.plugin_base import PluginBase

INDEX = 'index'
QUERY = 'query'
UPDATE = 'update'
OPTIONS = 'options'
OPTIONS_ALLOW_DELETES_XPATH = '/%s/allowDeletes' % OPTIONS


class PluginSimulator(PluginBase):
    """Simulator plugin.
    """

    def __init__(self, config=None):
        """Initialize the plugin instance.
        """
        self.ops = {}
        self.stop_called = False
        self.commit_called = False
        super(self.__class__, self).__init__(config)


    def find_ops(self, key):
        """Returns all the ops for a specific key.
        """
        if key in self.ops:
            return copy.deepcopy(self.ops[key])

        return []


    def is_stopped(self):
        return self.stop_called


    def is_committed(self):
        return self.commit_called


    def invoke(self, operation, doc, manager):
        """Update an existing Elasticsearch index in the document manager
           using the specified document.
        """
        if not isinstance(doc, dict) or '_id' not in doc:
            return None

        key = doc['_id']
        if key not in self.ops:
            self.ops[key] = []

        self.ops[key].append({'op': operation, 'doc': doc})
        return doc


    def commit(self):
        """Commit any outstanding operations.
        """
        self.commit_called = True


    def stop(self):
        """Stop threads if any are started by a plugin.
        """
        self.stop_called = True
