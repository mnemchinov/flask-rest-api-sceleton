from flask_restful import reqparse, Api

from bin.App import app
from bin.common.Const import APP_API_PREFIX

api = Api(app, prefix="/" + APP_API_PREFIX)

# region The Api parameters for requests
api_parameters = reqparse.RequestParser()

api_parameters.add_argument(name="limit",
                            dest="limit",
                            type=int,
                            default=None,
                            help="Number of elements per page",
                            store_missing=True,
                            location='args')

api_parameters.add_argument(name="page",
                            dest="page",
                            type=int,
                            default=1,
                            help="Page number",
                            store_missing=True,
                            location='args')

api_parameters.add_argument(name="q",
                            dest="query_string",
                            type=str,
                            help="String for search filters",
                            store_missing=False,
                            location='args')

# endregion
