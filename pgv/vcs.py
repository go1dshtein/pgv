import pgv.vcs_provider
import importlib
import logging


logger = logging.getLogger(__name__)


def get(provider=None, **kwargs):
    if provider is None:
        raise AttributeError("Undefined provider")

    for submodule_name in pgv.vcs_provider.__all__:
        importlib.import_module(".%s" % submodule_name, "pgv.vcs_provider")
        submodule = getattr(pgv.vcs_provider, submodule_name)
        if not hasattr(submodule, "provider"):
            continue
        if provider == submodule.provider["name"]:
            return submodule.provider["class"](**kwargs)

    raise NotImplementedError("Could not find provider %s" % name)
