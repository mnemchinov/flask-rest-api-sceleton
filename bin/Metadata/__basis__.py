import datetime

from flask import request
from flask_restful import Resource, abort
from marshmallow_sqlalchemy.fields import fields

import bin.common.NotificationHandler as Log
import bin.common.ResponseHandler as ResponseHandler
from Config import EMPTY_DATE, DATE_FORMAT
from bin.App import db, parser, ma
from bin.common.Const import ERR


class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(150), index=True, unique=True)
    title = db.Column(db.String(250), index=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    is_deleted = db.Column(db.Boolean, default=False)

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

        return data


class BaseController:

    def __init__(self, **kwargs):
        self.model = kwargs.get("model")
        self.need_commit = kwargs.get("need_commit", True)
        self.throw_exception = kwargs.get("throw_exception", True)

    def _error(self, message, log_write=Log.error):
        log_write(message)

        if self.throw_exception:
            raise NotImplementedError(message)

    def create(self, **kwargs):

        data = self.model.delete_not_updated_fields(**kwargs)
        item_code = kwargs.get("code", None)

        if item_code is not None and self.model.code.comparator.unique:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

            if item is not None:
                self._error(f"Item with Code={item_code} already exists!", Log.error)

                return item

        item = self.model()
        item.__dict__.update(data)
        db.session.add(item)

        if self.need_commit:
            db.session.commit()

        Log.ok(f"Item '{item}' was created")

        return item

    def read(self, **kwargs):
        item_id = kwargs.get("id")
        item_code = kwargs.get("code")
        item = None

        if item_id is not None:
            item = db.session.query(self.model).get(item_id)

            if item is None:
                self._error(f"Item with ID={item_id} not found!", Log.warning)

        elif item_code is not None:
            item = db.session.query(self.model).filter(self.model.code == item_code).first()

            if item is None:
                self._error(f"Item with Code={item_code} not found!", Log.warning)

        return item

    def update(self, **kwargs):

        item_id = kwargs.get("id")

        if item_id is None:
            self._error(f"No id specified!", Log.error)

        item = db.session.query(self.model).get(item_id)

        if item is None:
            self._error(f"Item not found!", Log.error)

        data = self.model.delete_not_updated_fields(**kwargs)
        db.session.query(self.model).filter(self.model.id == item_id).update(data)
        item = self.read(**kwargs)

        if self.need_commit:
            db.session.commit()

        Log.ok(f"Item {item} was updated")

        return item

    def delete(self, **kwargs):

        item = self.read(**kwargs)

        if not item:
            self._error(f"Item not found!", Log.error)

        if item.is_deleted:
            db.session.delete(item)

        else:
            self._error(f"Item '{item}' cannot be deleted", Log.error)

        if self.need_commit:
            db.session.commit()

        Log.ok(f"Item '{item} ' was deleted")

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
            self._error(f"Item not found!", Log.error)

            return item

        if item.is_deleted:
            self._error(f"Item '{item}' cannot be mark to delete", Log.error)

        else:
            item.is_deleted = True
            db.session.add(item)

            if self.need_commit:
                db.session.commit()

        Log.ok(f"Item '{item} ' was marked to delete")

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
            self._error(f"Item not found!", Log.error)

            return item

        if not item.is_deleted:
            self._error(f"Item '{item}' cannot be mark to undelete", Log.error)

            return item

        else:
            item.is_deleted = False
            db.session.add(item)

        if self.need_commit:
            db.session.commit()

        Log.ok(f"Item '{item} ' was marked to undelete")

        return item

    def to_dict(self, **kwargs):
        item = self.read(**kwargs)
        result = item.__dict__.copy()
        _created_at = EMPTY_DATE if item.created_at is None else item.created_at
        _updated_at = EMPTY_DATE if item.updated_at is None else item.updated_at
        _code = "No_name" if item.code is None else item.code

        result["created_at"] = _created_at.strftime(DATE_FORMAT)
        result["updated_at"] = _created_at.strftime(DATE_FORMAT)
        result["code"] = _code

        return result

    def get_list(self, limit: int = None, page: int = None):
        query = self.model.query.order_by(self.model.created_at)

        if limit:
            items = query.paginate(page, limit, False)

        else:
            items = query.all()

        return items


class BaseRouter:
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

                return ResponseHandler.render_response(status=ERR, message=str(ex))

        def patch(self, item_id: int):
            """Update an item by ID"""

            try:

                data = request.json

                if data is None:
                    raise NotImplementedError("No data")

                data["id"] = item_id
                controller = self.controller()
                schema = self.schema(many=False)
                raw_data = controller.update(**data)
                data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=str(ex))

        def delete(self, item_id: int):

            try:

                controller = self.controller()
                is_success = controller.delete(id=item_id)

                if is_success:
                    return ResponseHandler.render_response(message="Successfully delete!")

                raise NotImplemented("Failed to perform the operation")

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=str(ex))

    class Items(Resource):
        """Routes by template '/item/' """

        @staticmethod
        def route(endpoint: str):
            route = f"/{endpoint}"

            return route

        def __init__(self, **kwargs):
            self.schema = kwargs.get("schema")
            self.controller = kwargs.get("controller")

        def get(self, limit: int = None, page: int = None):
            """Reads a list of items"""

            try:
                args = parser.parse_args()
                limit = args.get("limit")
                page = args.get("page")
                controller = self.controller()
                schema = self.schema(many=True)
                raw_data = controller.get_list(limit, page)

                if limit:
                    items = raw_data.items
                    items = schema.dump(items)
                    data = ResponseHandler.get_section_paginate(raw_data, items)

                else:
                    data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=str(ex))

        def post(self):
            """Adds a new item"""

            try:

                kwargs = request.json
                controller = self.controller()
                schema = self.schema(many=False)
                raw_data = controller.create(**kwargs)
                data = schema.dump(raw_data)

                return ResponseHandler.render_response(data=data)

            except Exception as ex:

                return ResponseHandler.render_response(status=ERR, message=str(ex))

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

                return ResponseHandler.render_response(status=ERR, message=str(ex))


class BaseSchema(ma.ModelSchema):
    date_time_format = "%d.%m.%Y %H:%M:%S%z"
    created_at = fields.DateTime(format=date_time_format)
    updated_at = fields.DateTime(format=date_time_format)
    start_at = fields.DateTime(format=date_time_format)
    end_at = fields.DateTime(format=date_time_format)
