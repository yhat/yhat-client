from example_app.models.yhat_model import TestModel, Foo
from yhat import Yhat
import json

yh = Yhat(
        "greg",
        "foo",
        "http://api.yhat.com/"
        )
TestModel().execute(1)

# _, bundle = yh.deploy("Foo", TestModel, globals(), dry_run=True)
yh.deploy("Foo", TestModel, globals(), verbose=2)
# print json.dumps(bundle, indent=2)
