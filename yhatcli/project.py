import pip
import shutil
import urllib2
import json
import os

from utils import download_file
import credentials

PROJECT_DIR = os.path.join(os.environ['HOME'], ".yhat/templates")

def setup(template_name, project_name):
    """
    ***THIS IS AN EXAMPLE OF A PANDAS DOCSTRING***
    Return a DataFrame with the same shape as self and whose corresponding
    entries are from self where cond is True and otherwise are from other.

    Parameters
    ----------
    cond : boolean DataFrame or array
    other : scalar or DataFrame
    inplace : boolean, default False
    Whether to perform the operation in place on the data
    try_cast : boolean, default False
        try to cast the result back to the input type (if possible),
    raise_on_error : boolean, default True
        Whether to raise on invalid data types (e.g. trying to where on
        strings)

    Returns
    -------
    wh : DataFrame
    """
    if template_name=='*new project*':
        return setup_new_project()
    elif template_name=="*download project*":
        return find_template(project_name)
    replacements = {
        "project_name": project_name
    }
    replacements.update(credentials.read())
    config_filepath = os.path.join(PROJECT_DIR, template_name + '.json')
    config = json.load(open(config_filepath))
    if os.path.isdir(project_name):
        shutil.rmtree(project_name)
    print "creating project %s" % project_name
    os.mkdir(project_name)
    for dirname in config.get("dirs", []):
        path = os.path.join(project_name, dirname)
        if os.path.isdir(path)==False:
            os.mkdir(path)
    for newfile in config.get("files", []):
        filename = os.path.join(project_name, newfile['name'])
        with open(filename, "w") as f:
            f.write(newfile['content'].format(**replacements))

    print "Downloading data dependencies for project"
    print "="*80
    for datafile in config.get("data", []):
        print " >>> %s" % datafile['name']
        download_file(datafile['source'], datafile['name'])

    reqs_filepath = os.path.join(project_name, "reqs.txt")
    try:
        reqs = open(reqs_filepath).read().split('\n')
        pip_args = ['-vvv']
        pip_args.append('install')
        for req in reqs:
            pip_args.append(req)
        pip.main(initial_args=pip_args)
    except:
        print "%s not found!" % reqs_filepath

def setup_new_project():
    inputs = [
        {"prompt": "Project Name: ", "variable": "name"},
        {"prompt": "Description: ", "variable": "description"},
        {"prompt": "GitHub username: ", "variable": "github_username"},
        {"prompt": "Your name: ", "variable": "your_name"},
        {"prompt": "Your email: ", "variable": "your_email"}
    ]
    user_input = {}
    for prompt in inputs:
        user_input[prompt['variable']] = raw_input(Fore.CYAN + prompt['prompt'])
    
    return user_input

def find_template(query):
    ALL_TEMPLATES = [
        {"name": "something"}
    ]
    for template in ALL_TEMPLATES:
        if re.find(query, json.dumps(template)):
            yield template

def download_template(template_source):
    """
    Downloads a template and saves it to the .yhat/templates directory

    template_source - URL of the .json template file
    """
    if template_source.endswith(".json"):
        filename = os.path.basename(template_source)
        filename = os.path.join(os.environ['HOME'], '.yhat/templates', filename)
        download_file(template_source, filename)

def bundle(name, directory):
    """
    Grab each file and put it in a list with it's pathname (relative to 
    directory) and it's contents. Create a list of each directory (and any
    sub-directories). Create a list of data elements. These should have a 
    name and a source (url for now).
    """
    
    project_file = os.path.join(directory, name + ".json")
    project = {
        "name": name,
        "dirs": [],
        "files": [],
        "data": []
    }
    for i, (dirname, subdirs, files) in enumerate(os.walk(directory)):
        subdir = dirname.replace(directory, '').strip('/')
        if subdir:
            project["dirs"].append(subdir)
        for f in files:
            # TODO: make this more comprehensive; maybe a .gitignore?
            if f.endswith(".pyc"):
                continue
            f = os.path.join(dirname, f)
            # we don't want to bundle the bundle
            if os.path.basename(f)==os.path.basename(project_file):
                continue
            elif dirname==os.path.join(directory, "data"):
                # TODO: add option to upload to AWS/Dropbox
                source = raw_input("Input source URL for %s: " % f)
                f = f.replace(directory, '')
                f = f.strip('/')
                project["data"].append({"name": f, "source": source})
            else:
                content = open(f).read()
                f = f.replace(directory, '')
                f = f.strip('/')
                project["files"].append({"name": f, "content": content})
    with open(project_file, "wb") as f:
        json.dump(project, f, indent=2) 

