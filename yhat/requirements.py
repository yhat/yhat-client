from pip._vendor.pkg_resources import Requirement
try:
    from pip.utils import get_installed_distributions # pip 6.0
except ImportError:
    from pip.util import get_installed_distributions  # pip 1.5.x
from warnings import warn
import types


"""
This package attempts to pull all the Python library imports and their
version numbers from a session's globals. These are called implicit
requirements. It also provides a function for merging implicit and explicit
requirement into one requirements list. Both return lists of requirement
instances from the pip library.

Example:

    from sklearn.svm import SVR as svr
    from yhat import requirements
    import pandas as pd

    print requirements.implicit(globals())
    print requirements.merge(globals(), "scikit-learn==0.15.2")
"""


def _get_package_name(obj):
    """Returns the package name (e.g. "sklearn") for a Python object"""
    try:
        if isinstance(obj, types.ModuleType):
            return obj.__package__.split(".")[0]
        elif isinstance(obj, types.TypeType):
            return obj.__module__.split(".")[0]
        elif isinstance(obj, types.ObjectType):
            return obj.__class__.__module__.split(".")[0]
        else:
            return None
    except:
        return None


def implicit(session):
    """
    Returns a list of Requirement instances for all the library dependencies
    of a given session. These are matched using the contents of "top_level.txt"
    metadata for all package names in the session.
    """
    package_names = [_get_package_name(g) for g in session.values()]
    package_names = set(filter(None, package_names))

    reqs = {}
    for d in get_installed_distributions():
        for top_level in d._get_metadata("top_level.txt"):
            if top_level in package_names:
                # Sanity check: if a distribution is already in our
                # requirements, make sure we only keep the latest version.
                if d.project_name in reqs:
                    reqs[d.project_name] = max(reqs[d.project_name], d.version)
                else:
                    reqs[d.project_name] = d.version

    return [Requirement.parse('%s==%s' % r) for r in reqs.items()]


def merge(session, explicit=""):
    """
    Merges implicit and explicit requirements together. Implicit requirements
    are pulled out the user's session (i.e. globals()). Explicit requirements
    are provided directly by the user (e.g. ["sklearn==0.15.2"]). This
    function reconciles them and merges them into one set of requirements.
    Warnings are given to the user in case of version mismatche or modules
    that do not need to be required explicitly.
    """
    implicit_dict = {}
    for r in implicit(session):
        implicit_dict[r.project_name] = r 

    # explicit can be one requirement in a string, or many in a list.
    if isinstance(explicit, basestring) and explicit:
        explicit = [explicit]
    explicit_list = [Requirement.parse(r) for r in explicit]
    explicit_dict = {}
    for r in explicit_list:
        explicit_dict[r.project_name] = r

    for project_name, exp_req in explicit_dict.items():
        # To be polite, we keep the explicit dependencies and add the implicit
        # ones to them. We respect versions on the former, except in the case
        # of yhat, which should be the installed version.
        if project_name in implicit_dict:
            imp_req = implicit_dict[project_name]
            if exp_req == imp_req:
                warn(
                    "Dependency %s found implicitly. It can be removed "
                    "from REQUIREMENTS." % exp_req
                )

            elif project_name == "yhat":
                warn(
                    "Dependency yhat will be set to version %s." % imp_req
                )

            else:
                warn(
                    "Dependency %s specified in REQUIREMENTS, but %s is "
                    "installed. Using the former." % (exp_req, imp_req)
                )
                implicit_dict[project_name] = exp_req

        else:
            implicit_dict[project_name] = exp_req

    # Verify that yhat is set to the installed version. Normally this whould
    # show up as an implicit requirement. But we want to be extra sure.
    import yhat
    implicit_dict['yhat'] = Requirement.parse('yhat==%s' % yhat.__version__)

    return implicit_dict.values()
