import os

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
    # '1' for True '0' for False
    'WEBSERVER_DEBUG': '0',
    'TELEGRAF_GIT_URL': 'https://github.com/influxdata/telegraf.git',
    'TELEGRAF_GIT_BRANCH': 'v1.23.0',
    # '1' for True '0' for False
    'UPDATE_TELEGRAF_ON_RESTART': '1',
    'TELEGRAF_DIR': os.path.join(current_dir, 'telegraf-src'),
    'TELEGRAF_BUILD_DIR': os.path.join(current_dir, 'tmp', 'src'),
    'TELEGRAF_BINARY_DIR': os.path.join(current_dir, 'tmp', 'bin'),
    # CORS ORIGINS, separate by comma
    'CORS_ORIGINS': '*',
    # API KEYS, separate by comma
    'API_KEYS': '',
}
