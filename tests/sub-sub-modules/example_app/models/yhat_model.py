from yhat import YhatModel

class TestModel(YhatModel):
    def execute(self, data):
        f = Foo()
        print f.hello()
        return data

class Foo(object):

    def hello(self):
        return "Hello!"
