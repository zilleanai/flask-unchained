import inspect

from flask import Flask
from typing import List, Tuple

from .bundle import Bundle
from .utils import safe_import_module


class BundleOverrideModuleNameAttr:
    def __get__(self, instance, cls):
        return f'{cls.bundle_module_name}_module_name'


class AppFactoryHook:
    priority = 50

    bundle_module_name = None
    bundle_override_module_name_attr = BundleOverrideModuleNameAttr()

    def __init__(self):
        if not self.bundle_module_name:
            raise AttributeError(
                f'{self.__class__.__name__} is missing a `bundle_module_name` attribute')

    def run_hook(self, app: Flask, app_config_cls, bundles: List[Bundle]):
        objects = self.collect_objects(bundles)
        self.process_objects(app, app_config_cls, objects)

    def process_objects(self, app: Flask, app_config_cls, objects):
        raise NotImplementedError

    def collect_objects(self, bundles: List[Bundle]) -> List[Tuple[str, object]]:
        objects = []
        for bundle in bundles:
            objects += self.collect_from_bundle(bundle)
        return objects

    def collect_from_bundle(self, bundle: Bundle) -> List[Tuple[str, object]]:
        module = self.import_bundle_module(bundle)
        if not module:
            return []
        return inspect.getmembers(module, self.type_check)

    def type_check(self, obj: object) -> bool:
        raise NotImplementedError

    def import_bundle_module(self, bundle: Bundle):
        module_name = getattr(bundle,
                              self.bundle_override_module_name_attr,
                              self.bundle_module_name)
        module = safe_import_module(f'{bundle.module_name}.{module_name}')
        if not module:
            super_class = bundle.__class__.__mro__[1]
            if super_class != Bundle:
                module = safe_import_module(
                    f'{super_class.module_name}.{module_name}')
        return module

    def update_shell_context(self, ctx: dict):
        pass