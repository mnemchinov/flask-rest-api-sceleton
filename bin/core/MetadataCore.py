import datetime
import traceback

from flask import request
from flask_restful import Resource, abort
from marshmallow_sqlalchemy.fields import fields
from sqlalchemy import or_

import bin.common.ResponseHandler as ResponseHandler
from bin.Api import api_parameters
from bin.App import db, ma
from bin.common.Const import ERR, DATE_ISO_FORMAT, DATETIME_FORMAT_REGEX


class ModelCore(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(150), index=True, unique=True)
    title = db.Column(db.String(250), index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_deleted = db.Column(db.Boolean, default=False)
    search_fields = ["code", "title"]

    def __repr__(self):
        return f"{self.title}"

    def __str__(self):
        return f"{self.title}"

    @staticmethod
    def delete_not_updated_fields(**kwargs):
        data = {key: value for key, value in kwargs.items() if value is not None}
        data.pop("id", None)
        data.pop("created_at", None)
        data.pop("updated_at", None)
        data.pop("is_deleted", None)
        data.pop("_sa_instance_state", None)

        return data


class ControllerCore:

    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.need_commit = kwargs.get("need_commit", True)
        self.throw_exception = kwargs.get("throw_exception", True)

    @staticmethod
    def date_time_parser(dictionary: dict) -> dict:

        result = {key: datetime.datetime.strptime(value, DATE_ISO_FORMAT)
        if isinstance(value, str) and DATETIME_FORMAT_REGEX.match(value)
        else value for key, value in dictionary.items()}

        return result

    def _error(self, message):
        if self.throw_exception:
            raise NotImplementedError(message)

    def create(self, **kwargs):

        data = self.model.delete_not_updated_fields(**kwargs)
        item_code = kwargs.get("code", None)

        if item_code is not None and self.model.code.comparator.unique:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

            if item is not None:
                self._error(f"Item with Code={item_code} already exists!")

                return item

        item = self.model()
        item.__dict__.update(data)
        db.session.add(item)

        if self.need_commit:
            try:
                db.session.commit()

            except Exception as ex:
                db.session.rollback()
                item = None
                self._error(f"{ex}")

        return item

    def read(self, **kwargs):
        item_id = kwargs.get("id")
        item_code = kwargs.get("code")
        item = None

        if item_id is not None:
            item = db.session.query(self.model).get(item_id)

            if item is None:
                self._error(f"Item with ID={item_id} not found!")

        elif item_code is not None:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

            if item is None:
                self._error(f"Item with Code={item_code} not found!")

        return item

    def update(self, **kwargs):

        item_id = kwargs.get("id")

        if item_id is None:
            self._error(f"No id specified!")

        item = db.session.query(self.model).get(item_id)

        if item is None:
            self._error(f"Item not found!")

        data = self.model.delete_not_updated_fields(**kwargs)
        db.session.query(self.model).filter(self.model.id == item_id).update(data)
        item = self.read(**kwargs)

        if self.need_commit:
            try:
                db.session.commit()

            except Exception as ex:
                db.session.rollback()
                item = None
                self._error(f"{ex}")

        return item

    def delete(self, **kwargs):

        item = self.read(**kwargs)

        if not item:
            self._error(f"Item not found!")

        if item.is_deleted:
            db.session.delete(item)

        else:
            self._error(f"Item '{item}' cannot be deleted")

        if self.need_commit:
            try:
                db.session.commit()

            except Exception as ex:
                db.session.rollback()
                item = None
                self._error(f"{ex}")

        return True

    def mark_to_delete(self, **kwargs):

        item_id = kwargs.get("id")
        item_code = kwargs.get("code")
        item = None

        if item_id is not None:
            item = db.session.query(self.model).get(item_id)

        elif item_code is not None:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

        if not item:
            self._error(f"Item not found!")

            return item

        if item.is_deleted:
            self._error(f"Item '{item}' cannot be mark to delete")

        else:
            item.is_deleted = True
            db.session.add(item)

            if self.need_commit:
                try:
                    db.session.commit()

                except Exception as ex:
                    db.session.rollback()
                    item = None
                    self._error(f"{ex}")

        return item

    def mark_to_undelete(self, **kwargs):
        item_id = kwargs.get("id")
        item_code = kwargs.get("code")
        item = None

        if item_id is not None:
            item = db.session.query(self.model).get(item_id)

        elif item_code is not None:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

        if not item:
            self._error(f"Item not found!")

            return item

        if not item.is_deleted:
            self._error(f"Item '{item}' cannot be mark to undelete")

            return item

        else:
            item.is_deleted = False
            db.session.add(item)

        if self.need_commit:
            try:
                db.session.commit()

            except Exception as ex:
                db.session.rollback()
                item = None
                self._error(f"{ex}")

        return item

    def get_list(self, **kwargs):
        limit = kwargs.get("limit")
        page = kwargs.get("page")
        owner_id = kwargs.get("owner_id")
        query_string = kwargs.get("query_string")
        items = self.model.query.order_by(db.desc(self.model.created_at))

        if owner_id:
            items = items.filter(self.model.owner_id == owner_id)

        if query_string:
            query_string = f"%{query_string}%"
            filter_list = [getattr(self.model, field).like(query_string) for field in self.model.search_fields]
            items = items.filter(or_(*filter_list))

        if limit:
            items = items.paginate(page, limit, False)

        else:
            items = items.all()

        return items


class RouterCore:
    endpoint = None
    controller = None
    schema = None

    @classmethod
    def add_resource(cls, api, resource):
        kwargs = {'controller': cls.controller, 'schema': cls.schema}
        api.add_resource(resource, resource.route(cls.endpoint),
                         resource_class_kwargs=kwargs)

    class Item(Resource):
        """Routes by template '/item/<int:item_id>' """

        @staticmethod
        def route(endpoint: str):
            route = f"/{endpoint}/<int:item_id>"

            return route

        def __init__(self, **kwargs):
            self.schema = kwargs.get("schema")
            self.controller = kwargs.get("controller")

        def get(self, item_id: int):
            """Read an item by ID"""

            try:

                controller = self.controller()
                schema = self.schema()
                raw_data = controller.read(id=item_id)
                data = {'item': schema.dump(raw_data)}

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

        def patch(self, item_id):
            """Update an item by ID"""

            try:

                data = request.json

                if data is None:
                    raise NotImplementedError("No data")

                controller = self.controller()
                data["id"] = item_id
                data = controller.date_time_parser(data)
                schema = self.schema(many=False)
                raw_data = controller.update(**data)
                data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

        def delete(self, item_id: int):

            try:

                controller = self.controller()
                is_success = controller.delete(id=item_id)

                if is_success:
                    return ResponseHandler.render_response(message="Successfully delete!")

                raise NotImplemented("Failed to perform the operation")

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

    class Items(Resource):
        """Routes by template '/item/' """

        @staticmethod
        def route(endpoint: str):
            route = f"/{endpoint}"

            return route

        def __init__(self, **kwargs):
            self.schema = kwargs.get("schema")
            self.controller = kwargs.get("controller")

        def get(self):
            """Reads a list of items"""

            try:
                args = api_parameters.parse_args()
                limit = args.get("limit")
                controller = self.controller()
                schema = self.schema(many=True)
                raw_data = controller.get_list(**args)

                if limit:
                    items = raw_data.items
                    items = schema.dump(items)
                    data = ResponseHandler.get_section_paginate(raw_data, items)

                else:
                    data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

        def post(self):
            """Adds a new item"""

            try:

                controller = self.controller()
                kwargs = controller.date_time_parser(request.json)
                schema = self.schema(many=False)
                raw_data = controller.create(**kwargs)
                data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

    class ItemsFromOwner(Resource):
        """Routes by template '/item/from/<int:owner_id>' """

        @staticmethod
        def route(endpoint: str):
            route = f"/{endpoint}/from/<int:owner_id>"

            return route

        def __init__(self, **kwargs):
            self.schema = kwargs.get("schema")
            self.controller = kwargs.get("controller")

        def get(self, owner_id: int):

            try:

                args = api_parameters.parse_args()
                limit = args.get("limit")
                page = args.get("page")
                controller = self.controller()
                schema = self.schema(many=True)
                raw_data = controller.get_list(owner_id=owner_id, limit=limit, page=page)

                if limit:
                    items = raw_data.items
                    items = schema.dump(items)
                    data = ResponseHandler.get_section_paginate(raw_data, items)

                else:
                    data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())

    class ItemsActions(Resource):
        """Routes by template '/item/<int:item_id>/<string:action>' """

        @staticmethod
        def route(endpoint: str):
            route = f"/{endpoint}/<int:item_id>/<string:action>"

            return route

        def __init__(self, **kwargs):
            self.schema = kwargs.get("schema")
            self.controller = kwargs.get("controller")

        def patch(self, item_id: int, action: str):

            try:

                controller = self.controller()
                schema = self.schema(many=False)
                raw_data = None

                if action == 'delete':
                    raw_data = controller.mark_to_delete(id=item_id)

                elif action == 'undelete':
                    raw_data = controller.mark_to_undelete(id=item_id)

                elif hasattr(controller, action):
                    raw_data = getattr(controller, action)(id=item_id, args=request.args)

                else:
                    abort(404)

                data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=traceback.format_exc())


class SchemaCore(ma.ModelSchema):
    date_time_format = "%d.%m.%Y %H:%M:%S%z"
    created_at = fields.DateTime(format=date_time_format)
    updated_at = fields.DateTime(format=date_time_format)
    start_at = fields.DateTime(format=date_time_format)
    end_at = fields.DateTime(format=date_time_format)
    start_date = fields.DateTime(format=date_time_format)
    end_date = fields.DateTime(format=date_time_format)
    last_run = fields.DateTime(format=date_time_format)
    next_run = fields.DateTime(format=date_time_format)
