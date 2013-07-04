from yhat import Yhat, BaseModel

def hello():
    return "HEY AUSTIN!"

class MyModel(BaseModel):
    def require(self):
        pass

    def transform(self, data):
        return "something"

    def predict(self, data):
        return data * 10


mm = MyModel(clf=range(10), udfs=[hello])

yh = Yhat("greg", "abcd1234")

yh.upload("functest", mm)


