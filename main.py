from server import create_server

from settings import GLOBAL_SETTINGS
from settings_example import GLOBAL_SETTINGS as EXAMPLE_GLOBAL_SETTINGS

server = create_server(GLOBAL_SETTINGS, EXAMPLE_GLOBAL_SETTINGS)
app = server.app

if __name__ == '__main__':
    server.run()
