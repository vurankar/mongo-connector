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


CLASS_NAME = 'className'
CONFIG = 'config'
MODULE_NAME = 'moduleName'
OPTIONS = 'options'
PLUGIN_NAME = 'pluginName'
INDEX_DOCS = 'indexDocs'

LOG = logging.getLogger(__name__)


def _config_as_list(config):
    """Returns the plugin config as a list.
    """
    if not config:
        return []

    if isinstance(config, list):
        return config

    return [config]


def _resolve_plugin_config(config):
    """Resolves plugin using the configuration.
    """
    LOG.debug('resolving plugin config %r', config)
    if PLUGIN_NAME not in config:
        return None

    class_name = config[PLUGIN_NAME]
    module_name = 'mongo_connector.plugins.%s_plugin' % class_name
    if MODULE_NAME in config:
        module_name = config[MODULE_NAME]

    if CLASS_NAME in config:
        class_name = config[CLASS_NAME]

    #  Create a new plugin instance.
    try:
        # Resolve the plugin module.
        # importlib doesn't exist in 2.6, but __import__ is everywhere

        # import importlib
        # module = importlib.import_module(module_name)
        module = __import__(module_name, fromlist=(module_name,))
        clz = getattr(module, class_name)

        # Create a new plugin instance.
        return clz(config)
    except Exception as exc:
        fqn = '%s.%s' % (module_name, class_name)
        LOG.error('creating new plugin %s instance: %s', fqn, exc)

    return None


def get_plugin_configs(namespace):
    """Returns the plugin configurations for a namespace.
    """
    LOG.debug('Getting plugin configs for %r', namespace)
    if namespace and isinstance(namespace.plugins, list):
        configs = []
        for plugin_config in namespace.plugins:
            if CONFIG in plugin_config:
                configs.append(plugin_config)
        return configs

    return []


def docs_index_needed(config):
    """Returns whether or not any plugin config options say that docs need
       to be indexed as well.
    """
    LOG.debug('checking if docs index needed for config %r', config)
    for cfg in _config_as_list(config):
        if cfg and CONFIG in cfg and OPTIONS in cfg[CONFIG]:
            options = cfg[CONFIG][OPTIONS]
            if INDEX_DOCS in options and options[INDEX_DOCS]:
                LOG.debug('docs index needed returning true')
                return True
    return False


def resolve(config):
    """Resolves the plugins using the specified configuration.
    """
    LOG.debug('Resolving plugin config %r', config)
    plugin_list = []
    for cfg in _config_as_list(config):
        plugin = _resolve_plugin_config(cfg)

        # Even though plugin config was valid at check time, ensure that
        # we only use "resolved" plugins.
        if plugin is not None:
            plugin_list.append(plugin)

    return plugin_list
