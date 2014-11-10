from pip.util import get_installed_distributions
import types

"""
This package attempts to pull all the Python library imports and their
version numbers from a session's globals. It also provides a way to merge
those with a list of user-specified requirements which warns the user on
strange conditions.

Example:

    from sklearn.svm import SVR
    from yhat.requirements import get_requirements
    import pandas as pd

    print implicit_requirements(globals())
    print merge_requirements(globals(), [("sklearn", "0.15.2")])

"""

# TODO:
#
# 0. Make pip a requirement for yhat.
#
# 1. The idea here is that we can completely remove the REQUIREMENTS
#    variable from Python models. Test that against as many of the models
#    in cloud as possible. Does it detect all theif necessary requirements?
#
# 2. If (1.) fails, we may need to allow specification of additional
#    requirements in the models (things like distutils-based modules).
#    If this is the case, we have to deal with some error conditions:
#
#        a. Something is in the REQUIREMENTS that doesn't exist.
#        b. A version in REQUIREMENTS is not what they have on their system.
#
# 3. Append to requirements if the model isn't in there. Give warning:
#
#        a. We've detected the same thing on your system. Don't need.
#        b. Diff version.

def _get_package_name(obj):
    """Returns the package name (e.g. "sklearn") for a Python object"""
    if isinstance(obj, types.ModuleType):
        return obj.__package__
    elif isinstance(obj, types.TypeType):
        return obj.__module__.split(".")[0]
    elif isinstance(obj, types.ObjectType):
        return obj.__class__.__module__.split(".")[0]
    else:
        return None


def implicit_requirements(session):
    """
    Returns a list of (library, version) tuples for all the library
    requirements of a given session. These are matched using the contents of
    "top_level.txt" metadata for all package names in the session.
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

    return reqs.items()


def merge_requirements(session, requirements):
    """
    Merges the implicit requirements for a given session into an explicit
    list of user-provided requirements. Gives the user warnings if there is
    a version mismatch between the two, or if an explicit requirement can
    be found implicitly.
    """


