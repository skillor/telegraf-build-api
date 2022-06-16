import os
import re
from typing import *

from telegraf_builder.plugins import Plugins


class PluginManager:
    @staticmethod
    def get_plugins_path_by_type(working_dir: str, plugin_type: str):
        return os.path.join(working_dir, 'plugins', plugin_type, 'all', 'all.go')

    def __init__(self,
                 telegraf_dir: str,
                 plugin_types: List[str] = None
                 ):
        if plugin_types is None:
            plugin_types = [
                'aggregators',
                'inputs',
                'outputs',
                'parsers',
                'processors',
            ]
        self.plugin_types = plugin_types
        self.telegraf_dir = telegraf_dir
        self.plugins = self.get_plugins()

    def get_plugins(self) -> Plugins:
        return Plugins({plugin_type: self.get_plugins_by_type(plugin_type) for plugin_type in self.plugin_types})

    def get_plugins_by_type(self, plugin_type: str) -> List[str]:
        with open(self.get_plugins_path_by_type(self.telegraf_dir, plugin_type), 'r', encoding='utf-8') as f:
            content = f.read()
        return re.findall(r'\"github.com/influxdata/telegraf/plugins/' + plugin_type + r'/([^\"]+)\"', content)

    def set_plugins(self, working_dir: str, plugins: Plugins):
        for plugin_type in self.plugins.to_dict().keys():
            exclude_plugins = self.plugins.exclude_plugins_by_type(plugin_type, plugins)

            self.set_plugins_by_type(working_dir, plugin_type, exclude_plugins)

    def set_plugins_by_type(self, working_dir: str, plugin_type: str, exclude_plugins: List[str]):
        with open(self.get_plugins_path_by_type(working_dir, plugin_type), 'r', encoding='utf-8') as f:
            content = f.read()
        for plugin in exclude_plugins:
            content = re.sub(r'([^\n\"]+\"github.com/influxdata/telegraf/plugins/' + plugin_type + '/' + plugin + '")',
                             r'// \1',
                             content)

        with open(self.get_plugins_path_by_type(working_dir, plugin_type), 'w', encoding='utf-8') as f:
            f.write(content)
