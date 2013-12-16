from yhat import StepModel
from yhat import Yhat


class MyModel(StepModel):
    def step_1(self, data):
        return 1
    def step_2(self, data):
        return [data, 2]
    def step_3(self, data):
        return data + [3]

mm = MyModel()

yh = Yhat("greg", "abcd123", "http://localhost:3000/")
yh.deploy("hello", mm)
