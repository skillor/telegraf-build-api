from typing import *


class Plugins:
    def __init__(self, plugins: Dict[str, List[str]]):
        self.plugins = plugins

        self.plugin_list = sorted([plugin_type + '/' + plugin
                                   for plugin_type, m_plugins in plugins.items()
                                   for plugin in m_plugins])

    def __hash__(self):
        return hash(frozenset(x for x in self.plugin_list))

    def keys(self):
        return self.plugins.keys()

    def to_dict(self) -> Dict[str, List[str]]:
        return self.plugins

    def exclude_plugins_by_type(self, plugin_type: str, diff_plugins: 'Plugins') -> List[str]:
        if plugin_type not in diff_plugins.keys():
            return self.plugins[plugin_type]
        else:
            return list(set(self.plugins[plugin_type]).difference(diff_plugins.to_dict()[plugin_type]))
