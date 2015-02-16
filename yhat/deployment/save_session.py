import pickle
import terragon
import ast
import inspect
import types
import json
import sys
import os
import pprint as pp

try:
    import dill
except:
    pass


def _in_directory(filepath, directory):
    #make both absolute    
    directory = os.path.realpath(directory)
    filepath = os.path.realpath(filepath)
    #return true, if the common prefix of both is equal to directory
    #e.g. /a/b/c/d.rst and directory is /a/b, the common prefix is /a/b
    return os.path.commonprefix([filepath, directory]) == directory

def _is_on_syspath(filepath):
    if filepath is None:
        return False
    for libpath in sys.path:
        if libpath==os.getcwd():
            continue
        elif libpath!="":
            if _in_directory(filepath, libpath)==True:
                return True
    return False

def _get_source(func):
    """
    Gets the source of a function and handles cases when user is in an 
    interactive session

    func: function
        a function who's source we want
    """
    try:
        return inspect.getsource(func)
    except:
        if inspect.isclass(func):
            source = ""
            source += "class %s(%s):" % (func.__name__, func.__base__.__name__)
            source += "\n"
            for name, method in inspect.getmembers(func, predicate=inspect.ismethod):
                if hasattr(method, '__wrapped_func__'):
                    wrapped_source = dill.source.getsource(method.__wrapped_func__)
                    wrapped_source = wrapped_source.split('\n')
                    nchar = len(wrapped_source[1]) - len(wrapped_source[1].lstrip())
                    wrapped_source[0] = " "*nchar + wrapped_source[0]
                    wrapped_source = "\n".join(wrapped_source)
                    wrapped_source = "\n" + wrapped_source + "\n"
                    source += wrapped_source
                else:
                    source += inspect.getsource(method) + "\n"
        else:
            return inspect.getsource(func) + "\n"
        return source


def _strip_function_source(src):
    """
    Takes the source code of a function and dedents it so that it.

    Parameters
    ----------
    src: string
        function code

    Returns
    -------
    source: string
        source code of the same function, but "dedented"
    """
    src = src.split('\n')
    n = len(src[0]) - len(src[0].lstrip())
    return "\n".join([line[n:] for line in src])

def _get_naked_loads(function):
    """
    Takes a reference to a function and determines which variables used in the 
    function are not defined within the scope of the function.

    Parameters
    ----------
    function: function

    Returns
    -------
    variables: generator
        returns the variables in a function that are not:
            1) passed in as parameters 
            2) created within the scope of the function
    """
    source = _get_source(function)
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
                    # variable = thingvars['id']
                    # if variable not in params and variable not in created:
                        # yield variable
            elif isinstance(thingvars['ctx'], ast.Store):
                if 'id' in thingvars:
                    created.add(thingvars['id'])
    
    for variable in loaded:
        # TODO: if created but loaded before that as something else
        if variable not in params and variable not in created:
            yield variable

def _extract_module(module_name, modules={}):
    module = sys.modules.get(module_name)
    # check if we've already seen it
    if module in modules or module is None:
        pass
    # make sure it's not a built in module
    elif hasattr(module, "__file__")==False:
        pass
    elif _is_on_syspath(module.__file__)==False:
        module_py = module.__file__.replace(".pyc", ".py")
        module_source = open(module_py, 'rb').read()
        parent_dir = module_py.replace(os.getcwd(), '').lstrip('/')
        parent_dir = os.path.dirname(parent_dir)
        modules[module] = {
            "parent_dir": parent_dir,
            "name": os.path.basename(module_py),
            "source": module_source
        }
        tree = ast.parse(module_source)
        for thing in ast.walk(tree):
            if hasattr(thing, "module"):
                modules.update(_extract_module(thing.module))
            elif isinstance(thing, (ast.Import, ast.ImportFrom)):
                for imp in thing.names:
                    if imp.name!="*":
                        modules.update(_extract_module(imp.name))
    else:
        modules[module_name] = None
    return modules


def _spider_function(function, session, pickles={}):
    """
    Takes a function and global variables referenced in an environment and 
    recursively finds dependencies required in order to execute the function. 
    This includes references to classes, libraries, variables, functions, etc.

    Parameters
    ----------
    function: function
        a function referenced in an environment
    session: dictionary
        variables referenced from a seperate environment; i.e. globals()
    pickles: dictionary
        holds the variables needed to execute the function

    Returns
    -------
    imports: list
        list of import statements required for the function to execute
    source: string
        source code of the function
    pickles: dictionary
        dictionary of variable names and their values as pickled strings
    """

    if '_objects_seen' not in pickles:
        pickles['_objects_seen'] = []
    pickles['_objects_seen'].append(str(function))
    imports = []
    modules = {}
    source = "# code for %s\n" % (str(function)) 
    if isinstance(function, types.ModuleType):
        pass
    else:
        source += _get_source(function) + '\n'
    
    for varname in _get_naked_loads(function):
        if varname in pickles['_objects_seen']:
            continue
        pickles['_objects_seen'].append(varname)
        if varname not in session:
            continue
        obj = session[varname]
        # checking to see if this is an instance of an object
        if hasattr(obj, "__name__")==False:
            pickles[varname] = terragon.dumps_to_base64(obj)
        if hasattr(obj, "__module__"):
            if obj.__module__=="__main__":
                new_imports, new_source, new_pickles, new_modules = _spider_function(obj, session, pickles)
                source += new_source + '\n'
                imports += new_imports
                pickles.update(new_pickles)
                modules.update(new_modules)
            else:
                modules.update(_extract_module(obj.__module__))
                ref = inspect.getmodule(obj).__name__
                if hasattr(obj, "func_name") and obj.func_name!=varname:
                    imports.append("from %s import %s as %s" % (ref, obj.func_name, varname))
                else:
                    # we need to figure out how to import this library. i'm not 
                    # sure exactly what the right way to get the module and 
                    # class name, but this works just fine
                    try:
                        import_statement = "from %s import %s" % (ref, varname)
                        exec import_statement in locals()
                        imports.append(import_statement)
                    except:
                        try:
                            import_statement = "from %s import %s" % (ref, obj.__class__.__name__)
                            exec import_statement in locals()
                            imports.append(import_statement)
                        except:
                            pass

        elif isinstance(obj, types.ModuleType):
            modules.update(_extract_module(obj.__name__))
            if obj.__name__!=varname:
                imports.append("import %s as %s" % (obj.__name__, varname))
            else:
                imports.append("import %s" % (varname))
        else:
            # catch all. if all else fails, pickle it
            pickles[varname] = terragon.dumps_to_base64(obj)
    return imports, source, pickles, modules

def _detect_future_imports(session):
    """
    Detect all __future__ imports. Since these imports must come first in
    the source code, these are attempt to be detected outside of other
    spidering.
    
    Parameters
    ----------
    session: dictionary
        globals() from the user's environment
    """
    imports = []
    for k in session.keys():
        v = session[k]
        if hasattr(v,"__module__"):
            if v.__module__ == "__future__":
                if k is 'print_function':
                    continue
                if not k.startswith('_'):
                    imports.append("from __future__ import %s" % k)
    return imports

def save_function(function, session):
    """
    Saves a user's session and all dependencies to a big 'ole JSON object with
    accompanying pickles for any variable.

    Parameters
    ----------
    function: function
        function we're saving
    session: dictionary
        globals() from the user's environment
    """
    future_imports = "\n".join(_detect_future_imports(session))
    imports, source_code, pickles, modules = _spider_function(function, session)
    # de-dup and order the imports
    imports = sorted(list(set(imports)))
    imports.append("import json")
    imports.append("import pickle")
    imports.append("import terragon")
    source_code = "\n".join(imports) + "\n\n\n" + source_code
    pickles = {
        "objects": pickles,
        "future": future_imports,
        "code": source_code,
        "modules": [value for name, value in modules.items() if value is not None]
    }

    if "_objects_seen" in pickles["objects"]:
        del pickles["objects"]["_objects_seen"]
    return pickles

