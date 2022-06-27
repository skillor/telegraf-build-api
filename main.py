from server import create_server

import os
try:
    from settings import GLOBAL_SETTINGS
except ModuleNotFoundError or ImportError:
    GLOBAL_SETTINGS = None
try:
    from settings_example import GLOBAL_SETTINGS as EXAMPLE_GLOBAL_SETTINGS
except ModuleNotFoundError or ImportError:
    EXAMPLE_GLOBAL_SETTINGS = None

server = create_server(os.environ, GLOBAL_SETTINGS, EXAMPLE_GLOBAL_SETTINGS)
app = server.app

if __name__ == '__main__':
    server.run()
