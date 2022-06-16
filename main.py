from typing import *

import uvicorn
from fastapi import Body, FastAPI
from fastapi.requests import Request
from fastapi.responses import Response, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from telegraf_builder.builder import Builder
from telegraf_builder.plugin_manager import PluginManager
from telegraf_builder.plugins import Plugins


class Server:
    async def authorize(self, api_key: str):
        if self.api_keys is None:
            return
        if api_key is None:
            raise Exception('Api Key not provided')
        if api_key not in self.api_keys:
            raise Exception('Api Key is incorrect')

    def __init__(self,
                 plugin_manager: PluginManager,
                 builder: Builder,
                 debug=False,
                 api_keys=None,
                 cors_origins=None,
                 ):
        super().__init__()

        if api_keys is not None and len(api_keys) == 0:
            api_keys = None
        self.api_keys = api_keys

        self.plugin_manager = plugin_manager
        self.builder = builder

        docs_url = None
        redoc_url = None
        openapi_url = None
        if debug:
            docs_url = '/docs'
            redoc_url = '/redoc'
            openapi_url = '/openapi.json'

        self.app = FastAPI(
            title='Telegraf Build Api',
            debug=debug,
            default_response_class=Response,
            docs_url=docs_url,
            redoc_url=redoc_url,
            openapi_url=openapi_url,
        )

        if cors_origins is None:
            cors_origins = []

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=cors_origins,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @self.app.exception_handler(Exception)
        def handle_exception(request: Request, e: Exception):
            return JSONResponse(content={
                'code': 400,
                'name': type(e).__name__,
                'description': str(e),
            }, status_code=400)

        @self.app.get(path='/plugins', response_class=JSONResponse)
        async def get_plugins(api_key: str):
            await self.authorize(api_key)
            return JSONResponse(content=self.plugin_manager.plugins.to_dict())

        @self.app.post(path='/binary', response_class=FileResponse)
        async def binary(api_key: str,
                         go_os: str = Body(),
                         go_arch: str = Body(),
                         plugins: Dict[str, List[str]] = Body(),
                         ) -> FileResponse:
            await self.authorize(api_key)
            info = await self.builder.get_binary(go_os, go_arch, Plugins(plugins))
            return FileResponse(info.built_binary_path, filename=info.original_name)

        @self.app.post(path='/build', response_class=JSONResponse)
        async def build(api_key: str,
                        go_os: str = Body(),
                        go_arch: str = Body(),
                        plugins: Dict[str, List[str]] = Body(),
                        ) -> JSONResponse(content={'build_id': 'uuid'}):
            await self.authorize(api_key)
            info = await self.builder.get_binary(go_os, go_arch, Plugins(plugins))
            return JSONResponse(content={'build_id': info.uuid})

        @self.app.get(path='/download', response_class=FileResponse)
        async def download(api_key: str,
                           build_id: str,
                           ) -> FileResponse:
            await self.authorize(api_key)
            info = await self.builder.get_binary_by_build_id(build_id)
            return FileResponse(info.built_binary_path, filename=info.original_name)

    def run(self):
        uvicorn.run(self.app)


def create_server():
    from settings import GLOBAL_SETTINGS
    from settings_example import GLOBAL_SETTINGS as EXAMPLE_GLOBAL_SETTINGS

    from telegraf_builder.installer import install
    from telegraf_builder.cleaner import rm_dir

    def get_setting(key):
        if key in GLOBAL_SETTINGS:
            return GLOBAL_SETTINGS[key]
        return EXAMPLE_GLOBAL_SETTINGS[key]

    rm_dir(get_setting('TELEGRAF_BUILD_DIR'))
    rm_dir(get_setting('TELEGRAF_BINARY_DIR'))
    install(get_setting('TELEGRAF_GIT_URL'), get_setting('TELEGRAF_GIT_BRANCH'), get_setting('TELEGRAF_DIR'))

    plugin_manager = PluginManager(get_setting('TELEGRAF_DIR'))

    builder = Builder(plugin_manager,
                      get_setting('TELEGRAF_DIR'),
                      get_setting('TELEGRAF_BUILD_DIR'),
                      get_setting('TELEGRAF_BINARY_DIR'),
                      )

    return Server(
        plugin_manager=plugin_manager,
        builder=builder,
        cors_origins=get_setting('CORS_ORIGINS'),
        api_keys=get_setting('API_KEYS'),
        debug=get_setting('WEBSERVER_DEBUG'),
    )


def main():
    s = create_server()
    s.run()


if __name__ == '__main__':
    main()

else:
    server = create_server()
    app = server.app
