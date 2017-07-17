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
import logging
import uuid


#pylint: disable=R0921
class PluginBase(object):
    """Base class for all plugin implementations."""

    def __init__(self, config=None):
        """Initialize a plugin instance.
        """
        self._config = copy.deepcopy(config or {})
        self._name = None
        if isinstance(self._config, dict) and 'pluginName' in self._config:
            self._name = self._config['pluginName']

        if self._name is None:
            self._name = 'generated-%s' % uuid.uuid4()

        self.logger = logging.getLogger(__name__)
        self.logger.debug('BasePlugin initializer called')
        self.logger.debug('BasePlugin name = %s', self._name)
        self.logger.debug('BasePlugin config = %r', self._config)


    def name(self):
        """Returns the name of the plugin.
        """
        return self._name


    def info(self):
        """Returns the plugin config information.
        """
        if isinstance(self._config, dict) and 'config' in self._config:
            return self._config['config']
        return {}


    def invoke(self, operation, doc, manager):
        """Invoke a plugin operator on a document.
        """
        raise NotImplementedError


    def bulk_invoke(self, operation, docs, manager):
        """Bulk invoke a plugin for a set of documents.

        This method may be overridden to invoke many documents at once.
        """
        for doc in docs:
            self.invoke(operation, doc, manager)


    def commit(self):
        """Commit any outstanding operations.
        """
        raise NotImplementedError


    def stop(self):
        """Stop threads if any are started by a plugin.
        """
        raise NotImplementedError
