from Config import APP_SERVER_HOST, APP_SERVER_PORT, DEBUG
from bin.App import app

if __name__ == '__main__':

    app.run(host=APP_SERVER_HOST, port=APP_SERVER_PORT, debug=DEBUG)
