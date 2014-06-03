from yhat import YhatModel, Yhat, preprocess
# from first import hello as h2
import first as f2
from first import Support
from another.testfile import bye

def goodbye(y):
    bye()
    print y, "goodbye!"


class Example(YhatModel):
    @preprocess(in_type=dict, out_type=dict)
    def execute(self, data):
        goodbye(x)
        return Support().hello(10)
        # return h2(data)

from first import x

yh = Yhat("greg", "fCVZiLJhS95cnxOrsp5e2VSkk0GfypZqeRCntTD1nHA", "http://api.yhathq.com/")
yh.deploy_to_file("Example", Example, globals())
