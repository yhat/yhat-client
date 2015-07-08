import pickle
import terragon
import ast
import inspect
import tokenize
import types
import json
import StringIO
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

    if os.environ.get("CONDA_DEFAULT_ENV"):
        # CONDA wierdness. check and see if CONDA is messing with our 
        # syspath we're also going to have an exception for the yhat
        # library. not sure if this actually helps/hurts, but I don't 
        # want to find out
        conda_env = os.environ["CONDA_DEFAULT_ENV"]
        conda_syspath = os.path.join(conda_env, "lib", "python2.7")
        if conda_syspath in filepath:
            return True

    if os.environ.get("VIRTUAL_ENV"):
        # same nonsense as above,but for virtualenv
        if _in_directory(filepath, os.environ["VIRTUAL_ENV"]):
            return True

    return False

def _get_source(func):
    """
    Gets the source of a function and handles cases when user is in an 
    interactive session

    func: function
        a function who's source we want
    """
    # standardize source code indent to 4 spaces
    return reindent(_get_source_no_reindent(func))

def _get_source_no_reindent(func):
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
                    wrapped_source = "\n" + reindent(wrapped_source) + "\n"
                    source += wrapped_source
                else:
                    source += reindent(inspect.getsource(method)) + "\n"
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
    src = reindent(src)
    src = src.split('\n')
    n = len(src[0]) - len(src[0].lstrip())
    return "\n".join([line[n:] for line in src])

def _get_naked_loads(function, verbose=0):
    """
    Takes a reference to a function and determines which variables used in the 
    function are not defined within the scope of the function.

    Parameters
    ----------
    function: function
    verbose: int
        log level

    Returns
    -------
    variables: generator
        returns the variables in a function that are not:
            1) passed in as parameters 
            2) created within the scope of the function
    """
    source = _get_source(function)
    source = _strip_function_source(source)
    if verbose >= 1:
        sys.stderr.write("[INFO]: parsing source for %s\n" % str(function))
    if verbose >= 2:
        sys.stderr.write("[INFO]: %s\n" % source)
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

def _extract_module(module_name, modules={}, verbose=0):
    module = sys.modules.get(module_name)
    # check if we've already seen it
    if module in modules or module is None:
        pass
    # make sure it's not a built in module
    elif hasattr(module, "__file__")==False:
        pass
    elif _is_on_syspath(module.__file__)==False:
        if verbose >= 1:
            sys.stderr.write("[INFO]: file being parsed is: %s\n" % module.__file__)

        if module.__file__.endswith(".py"):
            module_py = module.__file__
        elif module.__file__.endswith(".pyc"):
            module_py = module.__file__.replace(".pyc", ".py")
        else:
            sys.stderr.write("[WARNING]: %s is not a .py or .pyc skipping: \n" % module.__file__)
            modules[module_name] = None
            return modules
            
        module_source = open(module_py, 'rb').read()
        parent_dir = module_py.replace(os.getcwd(), '').lstrip('/')
        parent_dir = os.path.dirname(parent_dir)
        modules[module] = {
            "parent_dir": parent_dir,
            "name": os.path.basename(module_py),
            "source": module_source
        }
        # Try to extract init files
        finit = os.path.join(parent_dir, "__init__.py")
        isinit = os.path.isfile(finit)
        if isinit:
            init_source = open(finit, 'rb').read()
            modules['init'] = {
                "parent_dir": parent_dir,
                "name": "__init__.py",
                "source": init_source
            }

        if verbose >= 1:
            sys.stderr.write("[INFO]: parsing source for %s\n" % module_name)
        if verbose >= 2:
            sys.stderr.write("[INFO]: %s\n" % module_source)
        tree = ast.parse(module_source)
        for thing in ast.walk(tree):
            if hasattr(thing, "module"):
                modules.update(_extract_module(thing.module, verbose=verbose))
            elif isinstance(thing, (ast.Import, ast.ImportFrom)):
                for imp in thing.names:
                    if imp.name!="*":
                        modules.update(_extract_module(imp.name, verbose=verbose))
    else:
        modules[module_name] = None
    return modules


def _spider_function(function, session, pickles={}, verbose=0):
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
    verbose: int
        log level

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
    
    for varname in _get_naked_loads(function, verbose=verbose):
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
                new_imports, new_source, new_pickles, new_modules = _spider_function(obj, session, pickles, verbose=verbose)
                source += new_source + '\n'
                imports += new_imports
                pickles.update(new_pickles)
                modules.update(new_modules)
            else:
                modules.update(_extract_module(obj.__module__, verbose=verbose))
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
            modules.update(_extract_module(obj.__name__, verbose=verbose))
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

def save_function(function, session, verbose=0):
    """
    Saves a user's session and all dependencies to a big 'ole JSON object with
    accompanying pickles for any variable.

    Parameters
    ----------
    function: function
        function we're saving
    session: dictionary
        globals() from the user's environment
    verbose: int
        log level
    """
    future_imports = "\n".join(_detect_future_imports(session))
    imports, source_code, pickles, modules = _spider_function(function, session, verbose=verbose)
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

def reindent(code):
    r = Reindenter(StringIO.StringIO(code))
    r.run()
    out = StringIO.StringIO()
    r.write(out)
    return out.getvalue()

def _rstrip(line, JUNK='\n \t'):
    i = len(line)
    while i > 0 and line[i-1] in JUNK:
        i -= 1
    return line[:i]

# Count number of leading blanks.
def getlspace(line):
    i, n = 0, len(line)
    while i < n and line[i] == " ":
        i += 1
    return i

class Reindenter:

    def __init__(self, f):
        self.find_stmt = 1  # next token begins a fresh stmt?
        self.level = 0      # current indent level

        # Raw file lines.
        self.raw = f.readlines()

        # File lines, rstripped & tab-expanded.  Dummy at start is so
        # that we can use tokenize's 1-based line numbering easily.
        # Note that a line is all-blank iff it's "\n".
        self.lines = [_rstrip(line).expandtabs() + "\n"
                      for line in self.raw]
        self.lines.insert(0, None)
        self.index = 1  # index into self.lines of next line

        # List of (lineno, indentlevel) pairs, one for each stmt and
        # comment line.  indentlevel is -1 for comment lines, as a
        # signal that tokenize doesn't know what to do about them;
        # indeed, they're our headache!
        self.stats = []

    def run(self):
        tokenize.tokenize(self.getline, self.tokeneater)
        # Remove trailing empty lines.
        lines = self.lines
        while lines and lines[-1] == "\n":
            lines.pop()
        # Sentinel.
        stats = self.stats
        stats.append((len(lines), 0))
        # Map count of leading spaces to # we want.
        have2want = {}
        # Program after transformation.
        after = self.after = []
        # Copy over initial empty lines -- there's nothing to do until
        # we see a line with *something* on it.
        i = stats[0][0]
        after.extend(lines[1:i])
        for i in range(len(stats)-1):
            thisstmt, thislevel = stats[i]
            nextstmt = stats[i+1][0]
            have = getlspace(lines[thisstmt])
            want = thislevel * 4
            if want < 0:
                # A comment line.
                if have:
                    # An indented comment line.  If we saw the same
                    # indentation before, reuse what it most recently
                    # mapped to.
                    want = have2want.get(have, -1)
                    if want < 0:
                        # Then it probably belongs to the next real stmt.
                        for j in xrange(i+1, len(stats)-1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                if have == getlspace(lines[jline]):
                                    want = jlevel * 4
                                break
                    if want < 0:           # Maybe it's a hanging
                                           # comment like this one,
                        # in which case we should shift it like its base
                        # line got shifted.
                        for j in xrange(i-1, -1, -1):
                            jline, jlevel = stats[j]
                            if jlevel >= 0:
                                want = have + getlspace(after[jline-1]) - \
                                       getlspace(lines[jline])
                                break
                    if want < 0:
                        # Still no luck -- leave it alone.
                        want = have
                else:
                    want = 0
            assert want >= 0
            have2want[have] = want
            diff = want - have
            if diff == 0 or have == 0:
                after.extend(lines[thisstmt:nextstmt])
            else:
                for line in lines[thisstmt:nextstmt]:
                    if diff > 0:
                        if line == "\n":
                            after.append(line)
                        else:
                            after.append(" " * diff + line)
                    else:
                        remove = min(getlspace(line), -diff)
                        after.append(line[remove:])
        return self.raw != self.after

    def write(self, f):
        f.writelines(self.after)

    # Line-getter for tokenize.
    def getline(self):
        if self.index >= len(self.lines):
            line = ""
        else:
            line = self.lines[self.index]
            self.index += 1
        return line

    # Line-eater for tokenize.
    def tokeneater(self, type, token, (sline, scol), end, line,
                   INDENT=tokenize.INDENT,
                   DEDENT=tokenize.DEDENT,
                   NEWLINE=tokenize.NEWLINE,
                   COMMENT=tokenize.COMMENT,
                   NL=tokenize.NL):

        if type == NEWLINE:
            # A program statement, or ENDMARKER, will eventually follow,
            # after some (possibly empty) run of tokens of the form
            #     (NL | COMMENT)* (INDENT | DEDENT+)?
            self.find_stmt = 1

        elif type == INDENT:
            self.find_stmt = 1
            self.level += 1

        elif type == DEDENT:
            self.find_stmt = 1
            self.level -= 1

        elif type == COMMENT:
            if self.find_stmt:
                self.stats.append((sline, -1))
                # but we're still looking for a new stmt, so leave
                # find_stmt alone

        elif type == NL:
            pass

        elif self.find_stmt:
            # This is the first "real token" following a NEWLINE, so it
            # must be the first token of the next program statement, or an
            # ENDMARKER.
            self.find_stmt = 0
            if line:   # not endmarker
                self.stats.append((sline, self.level))
