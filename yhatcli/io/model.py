import pickle
import ast
import inspect
import types
import json


def strip_function(src):
    """
    """
    src = src.split('\n')
    n = len(src[0]) - len(src[0].lstrip())
    return "\n".join([line[n:] for line in src])

def get_naked_loads(function):
    """
    """
    source = inspect.getsource(function)
    source = strip_function(source)
    tree = ast.parse(source)
    params = set()
    loaded = set()
    created = set()
    for thing in ast.walk(tree):
        thingvars = vars(thing)
        if "ctx" in thingvars:
            if isinstance(thingvars['ctx'], ast.Param):
                params.add(thingvars['id'])
            elif isinstance(thingvars['ctx'], ast.Load):
                if 'id' in thingvars:
                    loaded.add(thingvars['id'])
            elif isinstance(thingvars['ctx'], ast.Store):
                if 'id' in thingvars:
                    created.add(thingvars['id'])
    
    for variable in loaded:
        if variable not in params and variable not in created:
            yield variable

def spider_function(function, allvars, pickles={}):
    """
    """
    source = "# code for %s\n" % str(function)
    source += inspect.getsource(function) + '\n'
    for varname in get_naked_loads(function):
        if varname not in allvars:
            continue
        obj = allvars[varname]
        if hasattr(obj, '__call__'):
            if allvars['__file__']!=vars(inspect.getmodule(obj))['__file__']:
                ref = inspect.getmodule(obj).__name__
                source = "from %s import %s\n%s" % (ref, varname, source)
            else:
                source += spider_function(obj, allvars, pickles) + '\n'
        elif inspect.isclass(obj):
            if allvars['__file__']!=vars(inspect.getmodule(obj))['__file__']:
                ref = inspect.getmodule(obj).__name__
                source = "import %s as %s\n%s" % (ref, varname, source)
            else:
                source += inspect.getsource(obj) + '\n'
                class_methods = inspect.getmembers(obj,
                                    predicate=inspect.ismethod)
                for name, method in class_methods:
                    for subfunc in get_naked_loads(method):
                        if subfunc in allvars:
                            source += spider_function(allvars[subfunc],
                                    allvars, pickles)
        else:
            if isinstance(obj, types.ModuleType):
                ref = inspect.getmodule(obj).__name__
                source = "import %s as %s\n%s" % (ref, varname, source)
                continue
            pickles[varname] = pickle.dumps(obj)
    return source, pickles

