import pip
import shutil
import urllib2
import json
import os

from progressbar import ProgressBar, Bar, ETA, Percentage

import credentials

PROJECT_DIR = os.path.join(os.environ['HOME'], ".yhat/templates")

def setup(template_name, project_name):
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
        file_conn = urllib2.urlopen(datafile['source'])
        filesize = file_conn.headers['content-length']
        data_filepath = os.path.join(project_name, "data", datafile["name"])
        print " >>> %s" % datafile['name']
        processed = 0
        pbar = ProgressBar(widgets=[Bar(), ' ', ETA(), ' ', Percentage()],
                maxval=int(filesize)).start()
        with open(data_filepath, "wb") as f:
            # add in progress bar here
            for line in file_conn:
                processed += len(line)
                pbar.update(processed)
                f.write(line)
        print

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
