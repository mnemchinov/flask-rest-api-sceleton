from flask_restful import Api

from bin.App import app
from bin.metadata.Example import ExampleRouter

api = Api(app, prefix="/v1")


# region Ping

@app.route('/ping', methods=['GET'])
def ping():
    return "{'status', 'ok'}"


# endregion


ExampleRouter.add_resources(api)
