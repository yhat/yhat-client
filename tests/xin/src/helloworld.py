from yhat import Yhat, YhatModel , preprocess

class HelloWorld(YhatModel):
    @preprocess(in_type=dict, out_type=dict) 
    def execute(self, data):
        me = data['name']
        greeting = "Hello " + str(me) + "!"
        return { "greeting": greeting }

yh = Yhat("rongxin1989@gmail.com", "ff7bb725be9e4a32af286f464b316a23", "http://umsi.yhathq.com/")
yh.deploy ("HelloWorld", HelloWorld, globals())