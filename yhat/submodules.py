import os

def detect_explicit_submodules(model_object):
    submodules = []
    files = getattr(model_object, "FILES", [])
    for f in files:
        basename = os.path.basename(f)
        parent_dir = os.path.dirname(f)

        source = open(f, 'rb').read()
        with open(f, 'rb') as f:
            source = f.read()

        submodule = {
            "parent_dir": parent_dir,
            "name": basename,
            "source": source
        }
        submodules.append(submodule)

        directories = parent_dir.split('/')
        for i in range(len(directories) + 1):
            submodules.append({
                "parent_dir": "/".join(directories[:i]),
                "name": "__init__.py",
                "source": ""
            })

    return submodules
