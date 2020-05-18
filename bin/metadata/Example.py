from bin.core.MetadataCore import *

meta_name = 'example'


class ExampleModel(ModelCore):
    __tablename__ = meta_name


class ExampleController(ControllerCore):

    def __init__(self, **kwargs):
        kwargs['model'] = ExampleModel
        super().__init__(**kwargs)


class ExampleSchema(SchemaCore):
    class Meta:
        model = ExampleModel


class ExampleRouter(RouterCore):
    endpoint = meta_name
    controller = ExampleController
    schema = ExampleSchema

    def add_resources(self, api):
        super().add_resource(api, type(self.endpoint + RouterCore.Item.__name__, (RouterCore.Item,), {}))
        super().add_resource(api, type(self.endpoint + RouterCore.Items.__name__, (RouterCore.Items,), {}))
        super().add_resource(api,
                             type(self.endpoint + RouterCore.ItemsActions.__name__, (RouterCore.ItemsActions,), {}))
