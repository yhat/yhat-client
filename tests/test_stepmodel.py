from yhat.pml import StepModel
from yhat import Yhat

class MyModel(StepModel):
    def step_1(self, data):
        return 1
    def step_2(self, data):
        return [data, 2]
    def step_3(self, data):
        return data + [3]

mm = MyModel()

yh = Yhat("greg", "abcd1234")
print mm.execute("hello!")
yh.deploy_to_file("newmodel", mm)
