from bin.metadata.__basis__ import *

meta_name = 'example'


class ExampleModel(BaseModel):
    __tablename__ = meta_name


class ExampleController(BaseController):

    def __init__(self, **kwargs):
        kwargs['model'] = ExampleModel
        super().__init__(**kwargs)


class ExampleSchema(BaseSchema):
    class Meta:
        model = ExampleModel


class ExampleRouter(BaseRouter):
    endpoint = meta_name
    controller = ExampleController
    schema = ExampleSchema

    def add_resources(self, api):
        super().add_resource(api, type(self.endpoint + BaseRouter.Item.__name__, (BaseRouter.Item,), {}))
        super().add_resource(api, type(self.endpoint + BaseRouter.Items.__name__, (BaseRouter.Items,), {}))
        super().add_resource(api,
                             type(self.endpoint + BaseRouter.ItemsActions.__name__, (BaseRouter.ItemsActions,), {}))
