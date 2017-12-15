import datetime
import inspect
import os

from importlib import import_module

# alias these to the utils module
from .clips_pattern import de_camel, pluralize, singularize


def get_boolean_env(name, default):
    default = 'true' if default else 'false'
    return os.getenv(name, default).lower() in ['true', 'yes', 'y', '1']


def get_members(module, predicate):
    """
    Like inspect.getmembers except predicate is passed both name and object
    """
    for name, obj in inspect.getmembers(module):
        if predicate(name, obj):
            yield (name, obj)


def kebab_case(string):
    return de_camel(string, '-')


def safe_import_module(module_name):
    """
    Like importlib's import_module, except it does not raise ImportError
    if the requested module_name was not found
    """
    try:
        return import_module(module_name)
    except ImportError as e:
        if module_name not in str(e):
            raise e


def snake_case(string):
    return de_camel(string)


def title_case(string):
    return de_camel(string, ' ').title()


def utcnow():
    """
    Returns a current timezone-aware datetime.datetime in UTC
    """
    return datetime.datetime.now(datetime.timezone.utc)