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

import logging
import threading
import time

from mongo_connector.plugins.plugin_base import PluginBase
from mongo_connector.util import resolve_xpath


INDEX = 'index'

QUERY = 'query'
QUERY_KEY_XPATH = '/%s/key' % QUERY
QUERY_XMAP_XPATH = '/%s/xmap' % QUERY

UPDATE = 'update'
UPDATE_FIELD_XPATH = '/%s/field' % UPDATE
UPDATE_KEY_XPATH = '/%s/key' % UPDATE
UPDATE_XMAP_XPATH = '/%s/xmap' % UPDATE

VALUE = 'value'
UPDATE_VALUE_XPATH = '/%s/%s' % (UPDATE, VALUE)
UPDATE_VALUE_TYPE_XPATH = '%s/type' % UPDATE_VALUE_XPATH
UPDATE_VALUE_KEYS_XPATH = '%s/keys' % UPDATE_VALUE_XPATH

OPTIONS = 'options'
OPTIONS_ALLOW_DELETES_XPATH = '/%s/allowDeletes' % OPTIONS

SUPPORTED_VALUE_TYPES = ['dict']

LOG = logging.getLogger(__name__)


# TODO(ramr): All this code eventually should be in a separate plugin repo.

def _resolve_xmap(doc, xmap):
    """Build and return the resolved xmap dictionary.
    """
    xmap_dict = {}
    if isinstance(xmap, dict):
        for k in xmap:
            xmap_dict[k] = resolve_xpath(doc, xmap[k])

    return xmap_dict


def _build_query_key(doc, fields, xmap):
    """Build and return the query key.
    """
    if fields is None or not isinstance(fields, list):
        return None

    if xmap is None or not isinstance(xmap, dict):
        return None

    xmap_dict = _resolve_xmap(doc, xmap)

    query_key = ""
    for k in fields:
        if k in xmap_dict and xmap_dict[k] is not None:
            query_key += xmap_dict[k]

    if len(query_key) > 0:
        return query_key

    return None


def _get_query_criteria(config, doc):
    """Build and return the query criteria.
    """
    if not isinstance(config, dict) or QUERY not in config:
        return None

    key_fields = resolve_xpath(config, QUERY_KEY_XPATH)
    if not isinstance(key_fields, list):
        key_fields = [key_fields]

    xmap = resolve_xpath(config, QUERY_XMAP_XPATH)
    return _build_query_key(doc, key_fields, xmap)


def _build_update_key(config, doc):
    """Build the update key.
    """
    if not isinstance(config, dict) or UPDATE not in config:
        return None

    field_name = resolve_xpath(config, UPDATE_FIELD_XPATH)
    xmap = resolve_xpath(config, UPDATE_XMAP_XPATH)
    key_fields = resolve_xpath(config, UPDATE_KEY_XPATH)

    if not isinstance(key_fields, list):
        key_fields = [key_fields]

    if field_name is None:
        return None

    if xmap is None or not isinstance(xmap, dict):
        return None

    xmap_dict = _resolve_xmap(doc, xmap)

    update_key = "%s." % field_name
    start_len = len(update_key)
    for k in key_fields:
        if k in xmap_dict and xmap_dict[k] is not None:
            update_key += xmap_dict[k]

    if len(update_key) == start_len:
        return None

    return update_key


def _build_update_value_dict(config, doc):
    """Build the update value dictionary.
    """
    if not isinstance(config, dict) or UPDATE not in config:
        return None

    xmap = resolve_xpath(config, UPDATE_XMAP_XPATH)
    if xmap is None or not isinstance(xmap, dict):
        return None

    xmap_dict = _resolve_xmap(doc, xmap)

    value_type = resolve_xpath(config, UPDATE_VALUE_TYPE_XPATH)
    if value_type not in SUPPORTED_VALUE_TYPES:
        return None

    value_keys = resolve_xpath(config, UPDATE_VALUE_KEYS_XPATH)
    if value_keys is None or not isinstance(value_keys, list):
        return None

    value_dict = {}
    for k in value_keys:
        if k in xmap_dict and xmap_dict[k] is not None:
            value_dict[k] = xmap_dict[k]

    if len(value_dict) > 0:
        return value_dict

    return None


def _get_document_update_spec(operation, config, doc):
    """Return the document update spec.
    """
    update_key = _build_update_key(config, doc)
    allow_deletes = resolve_xpath(config, OPTIONS_ALLOW_DELETES_XPATH)

    if operation == 'd':
        if allow_deletes is True and update_key is not None:
            return {"$unset": {update_key: True}}
        return None

    update_value_dict = _build_update_value_dict(config, doc)

    if update_key is None or update_value_dict is None:
        return None

    return {"$set": {update_key: update_value_dict}}


class UpdateElasticsearchIndex(PluginBase):
    """Update Elasticsearch index plugin.
    """

    def __init__(self, config=None):
        """Initialize update Elasticsearch index plugin instance.
        """
        self._pending_ops = []
        self._lock = threading.Lock()
        super(self.__class__, self).__init__(config)


    def _add_pending_op(self, manager):
        """Adds a pending operation.
        """
        self._lock.acquire()
        self._pending_ops.append(manager)
        self._lock.release()


    def _reset_pending_ops(self):
        """Resets any pending operations.
        """
        pending_ops = []

        self._lock.acquire()
        pending_ops = self._pending_ops or []
        self._pending_ops = None
        self._lock.release()

        return pending_ops


    def invoke(self, operation, doc, manager):
        """Update an existing Elasticsearch index in the document manager
           using the specified document.
        """
        self.logger.debug('UpdateElasticsearchIndex.invoke(%s, %s, %s)',
            operation, doc, manager)

        config = self.info()

        index_name = None
        if INDEX in config:
            index_name = config[INDEX]

        if index_name is None:
            LOG.error('UpdateElasticsearchIndex.invoke: no index name')
            return None

        criteria = _get_query_criteria(config, doc)
        update_spec = _get_document_update_spec(operation, config, doc)
        timestamp = time.time()

        if criteria is None or update_spec is None:
            LOG.info('UpdateElasticsearchIndex.invoke: no criteria '
                      'or update spec for %s operation', operation)
            return None

        LOG.debug('UpdateElasticsearchIndex.invoke: criteria = %s, '
            'update_spec = %r, index_name = %s',
            criteria, update_spec, index_name)

        self._add_pending_op(manager)
        return manager.update(criteria, update_spec, index_name, timestamp)


    def commit(self):
        """Commit any outstanding operations.
        """
        pending_doc_managers = self._reset_pending_ops()
        for pdm in pending_doc_managers:
            pdm.commit()


    def stop(self):
        """Stop threads if any are started by a plugin.
        """
        pass
