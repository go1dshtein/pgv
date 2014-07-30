import pgv.vcs_provider
import importlib


def get(name, **kwargs):
    for submodule_name in pgv.vcs_provider.__all__:
        importlib.import_module(".%s" % submodule_name, "pgv.vcs_provider")
        submodule = getattr(pgv.vcs_provider, submodule_name)
        if not hasattr(submodule, "provider"):
            continue
        provider, klass = submodule.provider
        if name == provider:
            return klass(**kwargs)

    raise NotImplementedError("Could not find provider %s" % name)
