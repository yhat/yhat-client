from example_app.models.yhat_model import TestModel, Foo
from yhat import Yhat
import json

yh = Yhat("greg", "7e00601199a406babda135e3e05dd2d6", "http://do-sb-kernel-master.x.yhat.com")
yh = Yhat(
        "greg",
        "d8c90dfecd2dc088a297c3cb21de1770",
        "https://sandbox.c.yhat.com"
        )
TestModel().execute(1)

# _, bundle = yh.deploy("Foo", TestModel, globals(), dry_run=True)
yh.deploy("Foo", TestModel, globals(), verbose=2)
# print json.dumps(bundle, indent=2)
