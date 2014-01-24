#<start sys imports>
from yhat import StepModel
import inspect
import re
#<end sys imports>
#<start user imports>

#<end user imports>

#<start user functions>
#<end user functions>

class MyModel(StepModel):
    def __init__(self, **kwargs):
        for kw, arg in kwargs.iteritems():
            if kw=="requirements":
                arg = open(arg).read().strip()
            setattr(self, kw, arg)

    def _get_steps(self):
        steps = []
        for name, step in inspect.getmembers(self, predicate=inspect.ismethod):
            if re.match("step_", name):
                order = name.lstrip("step_")
                try:
                    order = int(order)
                except:
                    raise Exception("'%s' - step names must be integers" % name)
                steps.append((order, name, step))
        steps = sorted(steps, key=lambda x: x[0])
        return steps

    def execute(self, data):
        for _, name, step in self._get_steps():
            try:
                data = step(data)
            except Exception, e:
                print "Error executing step: '%s'" % name
                print "Exception: %s" % str(e)
                return
        return data

    def require(self):
        pass

    def step_1(self, data):
        return 1

    def step_2(self, data):
        return [data, 2]

    def step_3(self, data):
        return data + [3]

