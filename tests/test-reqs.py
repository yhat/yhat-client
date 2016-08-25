from yhat import Yhat, YhatModel


class Test(YhatModel):
    REQUIREMENTS = ['numpy']
    def execute(self, data):
        print data
        return data

t = Test()
yh = Yhat("fakeuser", "foo", "http://api.yhathq.com/")
yh.deploy("Test", Test, globals())
