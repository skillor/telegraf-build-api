# Telegraf Build Api

### Docs

API-Documentation can be found here: https://skillor.github.io/telegraf-build-api/

## Installation

All settings can be overwritten with environment variables with the same name.

### Run as Docker container

> with port and API KEY

    docker run --rm -d -p 8000:80 --env API_KEYS=123qwe skillor/telegraf-build-api

### Setup in Unix

> Install Go Version accordingly to your Telegraf Version (https://github.com/influxdata/telegraf/#build-from-source)

    sudo apt install golang-go

> Install requirements

    pip3 install -r requirements.txt

> Copy "settings_example.py" to "settings.py"

    cp settings_example.py settings.py

> Edit your settings.py

> Start the server

    python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 --log-level warning
