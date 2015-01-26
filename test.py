from yhat import Yhat, YhatModel , preprocess

x = range(10)
class HelloWorld(YhatModel):
    @preprocess(in_type=dict, out_type=dict)
    def execute(self, data):
        print x[:10]
        me = data['name']
        greeting = "Hello " + str(me) + "!"
        return { "greeting": greeting, "x": x}

# yh = Yhat("greg", "fCVZiLJhS95cnxOrsp5e2VSkk0GfypZqeRCntTD1nHA", "http://cloud.yhathq.com/")
yh = Yhat("greg", "9207b9a2dd9d48848b139b729d4354bc", "http://localhost:8080/")
yh.deploy("NewZippedModel", HelloWorld, globals())
