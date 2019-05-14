#

import os
import json
import shutil
import logging
from attrdict import AttrDict

_PATH = os.path.split(__file__)[0]
def _relative_path(*path):
    return os.path.realpath(os.path.join(_PATH, *path))

class EnvConfig(AttrDict):
    '''Loads informations given within the environment files'''

    _RELATIVE_ROOT = '..\\config'
    _MAIN_FILE = 'main.json'

    ROOT = _relative_path(_RELATIVE_ROOT)
    MAIN = os.path.realpath(os.path.join(ROOT, _MAIN_FILE))

    def __new__(cls, *args, **kwargs):
        '''Ensures builders can make recursive AttrDict using an EnvConfig'''
        if args or kwargs:
            return AttrDict(*args, **kwargs)
        return super().__new__(cls)

    def __init__(self):
        with open(os.path.join(self.MAIN), 'r') as f:
            super().__init__(json.load(f))

    def _iterate_configs(self, subdir):
        '''Loops over a given folder and load the config files one at a time'''
        for relpath in os.listdir(subdir):
            abspath = os.path.join(subdir, relpath)
            if not os.path.isfile(abspath) or not abspath.endswith('.json'):
                if not abspath.endswith('.json.meta'): # Remove that ultimately
                    _config_log.warning(f'Invalid file "{abspath}"')
                continue
            with open(abspath, 'r') as f:
                yield AttrDict(json.load(f))

    def _list_configs(self, *path):
        '''Returns a list of loaded configurations for a given directory'''
        subdir = os.path.join(self.ROOT, *path)
        if not os.path.isdir(subdir):
            raise FileNotFoundError(subdir)
        configs = list(self._iterate_configs(subdir))
        assert len(configs), f'No valid file found in {subdir}'
        return configs

    def load_generated(self):
        '''Loads part of the configuration that was generated after the start of the program'''
        loaded = AttrDict()
        loaded.events = self._list_configs(self.generated.events)
        loaded.models = self._list_configs(self.generated.models)
        loaded.maps = self._list_configs(self.generated.maps)
        with open(os.path.join(self.ROOT, self.generated.enums), 'r') as f:
            loaded.enums = json.load(f)
        self.loaded = loaded

    def _get_full_path(self, *path):
        full_path = os.path.realpath(os.path.join(self.ROOT, *path))
        if full_path in (self.ROOT, self.MAIN) or not full_path.startswith(self.ROOT):
            raise ValueError(f'{full_path}: does not look like a valid runtime-generated path')
        return full_path

    def dump(self, obj, *path):
        full_path = self._get_full_path(*path)
        os.makedirs(os.path.split(full_path)[0], exist_ok=True)
        with open(full_path, 'w') as f:
            json.dump(obj, f, indent=4)

    def _rm(self, *path):
        full_path = self._get_full_path(*path)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        elif os.path.exists(full_path):
            os.remove(full_path)

    def remove_generated(self):
        for path in self.generated.values():
            self._rm(path)

Configuration = EnvConfig()
_log_file = _relative_path(Configuration.log)
if os.path.exists(_log_file):
    os.remove(_log_file)
logging.basicConfig(level=logging.INFO, handlers=[logging.FileHandler(_log_file), logging.StreamHandler()])
_config_log = logging.getLogger('Configuration')
_config_log.info('Loaded')
