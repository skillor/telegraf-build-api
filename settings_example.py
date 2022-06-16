import os

current_dir = os.path.dirname(os.path.realpath(__file__))

GLOBAL_SETTINGS = {
    'WEBSERVER_DEBUG': False,
    'TELEGRAF_GIT_URL': 'https://github.com/influxdata/telegraf.git',
    'TELEGRAF_GIT_BRANCH': 'v1.23.0',
    'TELEGRAF_DIR': os.path.join(current_dir, 'telegraf-src'),
    'TELEGRAF_BUILD_DIR': os.path.join(current_dir, 'tmp', 'src'),
    'TELEGRAF_BINARY_DIR': os.path.join(current_dir, 'tmp', 'bin'),
    'CORS_ORIGINS': [
        '*'
    ],
    'API_KEYS': [
        # '123qwe',
    ],
}
