from flask_restful import Api

from bin.App import app

api = Api(app, prefix="/v1")


# region Ping

@app.route('/ping', methods=['GET'])
def ping():
    return "{'status', 'ok'}"

# endregion

