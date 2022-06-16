def main():
    from fastapi.openapi.utils import get_openapi
    from server import Server
    import json
    import os

    app = Server().app

    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'docs', 'openapi.json')
    with open(file_path, 'w') as f:
        json.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ), f)


if __name__ == '__main__':
    main()
