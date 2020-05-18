from flask_restful import Api

from bin.App import app
from bin.common.Const import APP_API_PREFIX
from bin.metadata.Example import ExampleRouter

api = Api(app, prefix=f"/{APP_API_PREFIX}")


# region Ping

@app.route(f"/{APP_API_PREFIX}/ping")
def ping():
    return "{'status', 'ok'}"


# endregion


ExampleRouter().add_resources(api)
