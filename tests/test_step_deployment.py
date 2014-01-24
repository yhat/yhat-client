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

yh = Yhat("greg", "fCVZiLJhS95cnxOrsp5e2VSkk0GfypZqeRCntTD1nHA", "http://cloud.yhathq.com/")
yh.deploy("StepTestModel", mm)
