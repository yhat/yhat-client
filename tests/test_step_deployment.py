from yhat import StepModel
from yhat import Yhat
from yhat import credentials


class MyModel(StepModel):
    def step_1(self, data):
        return 1
    def step_2(self, data):
        return [data, 2]
    def step_3(self, data):
        return data + [3]

mm = MyModel()


creds = credentials.read()
yh = Yhat(creds['username'], creds['apikey'], "http://localhost:8080/")
yh.deploy("StepTestModel", mm)
