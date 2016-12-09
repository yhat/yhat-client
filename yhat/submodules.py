import os

def detect_explicit_submodules(model_object):
    submodules = []
    files = getattr(model_object, "FILES", [])
    for f in files:
        basename = os.path.basename(f)
        parent_dir = os.path.dirname(f)
        source = open(f, 'rb').read()
        submodule = {
            "parent_dir": parent_dir,
            "name": basename,
            "source": source
        }
        submodules.append(submodule)

        directories = parent_dir.split('/')
        # print("ze directories", directories)
        for i in range(len(directories) + 1):
            # print(i, "/".join(directories[:i]))
            submodules.append({
                "parent_dir": "/".join(directories[:i]),
                "name": "__init__.py",
                "source": ""
            })
        # print [os.path.join(s['parent_dir'], s['name']) for s in submodules]

    return submodules
