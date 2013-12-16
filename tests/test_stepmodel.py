from yhat.pml import StepModel


class MyModel(StepModel):
    def step_1(self, data):
        return 1
    def step_2(self, data):
        return [data, 2]
    def step_3(self, data):
        return data + [3]

mm = MyModel()

print mm.execute("hello!")
