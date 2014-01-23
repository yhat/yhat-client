import pickle
import ast
import inspect
import types
import json


def _strip_function_source(src):
    """
    Takes the source code of a function and dedents it so that it.

    src - function code
    """
    src = src.split('\n')
    n = len(src[0]) - len(src[0].lstrip())
    return "\n".join([line[n:] for line in src])

def _get_naked_loads(function):
    """
    Takes a reference to a function and determines which variables used in the 
    function are not defined within the scope of the function.

    function - a function
    """
    source = inspect.getsource(function)
    source = _strip_function_source(source)
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

def _spider_function(function, session, pickles={}):
    """
    Takes a function and global variables referenced in an environment and 
    recursively finds dependencies required in order to execute the function. 
    This includes references to classes, libraries, variables, functions, etc.

    function - a function referenced in an environment
    session - variables referenced from a seperate environment (globals())
    pickles - holds the variables needed to execute the function
    """
    source = "# code for %s\n" % str(function)
    source += inspect.getsource(function) + '\n'
    for varname in _get_naked_loads(function):
        if varname not in session:
            continue
        obj = session[varname]
        if hasattr(obj, '__call__'):
            if session['__file__']!=vars(inspect.getmodule(obj))['__file__']:
                ref = inspect.getmodule(obj).__name__
                source = "from %s import %s\n%s" % (ref, varname, source)
            else:
                new_source, new_pickles = _spider_function(obj, session, pickles)
                source += new_source + '\n'
                pickles.update(new_pickles)
        elif inspect.isclass(obj):
            if session['__file__']!=vars(inspect.getmodule(obj))['__file__']:
                ref = inspect.getmodule(obj).__name__
                source = "import %s as %s\n%s" % (ref, varname, source)
            else:
                source += inspect.getsource(obj) + '\n'
                class_methods = inspect.getmembers(obj,
                                            predicate=inspect.ismethod)
                for name, method in class_methods:
                    for subfunc in _get_naked_loads(method):
                        if subfunc in session:
                            new_source, new_pickles = _spider_function(
                                    session[subfunc], session, pickles
                                    )
                            source += new_source
                            pickles.update(new_pickles)
        else:
            if isinstance(obj, types.ModuleType):
                ref = inspect.getmodule(obj).__name__
                source = "import %s as %s\n%s" % (ref, varname, source)
                continue
            pickles[varname] = pickle.dumps(obj)
    return source, pickles

def save_function(filename, function, session):
    """

    filename - name of the outputted JSON file with pickles and code
    function - name of the function we're saving
    session - globals() from the user's environment
    """
    source_code, pickles = _spider_function(function, session)
    source_code = "import json\nimport pickle\n" + source_code
    source_code += """pickles = json.load(open('%s', 'rb'))
for varname, pickled_value in pickles.get('objects', {}).items():
    globals()[varname] = pickle.loads(pickled_value)
    """ % filename
    pickles = {
        "objects": pickles,
        "code": source_code
    }
    with open(filename, "wb") as f:
        json.dump(pickles, f)

