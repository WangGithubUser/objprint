# Licensed under the Apache License: http://www.apache.org/licenses/LICENSE-2.0
# For details: https://github.com/gaogaotiantian/objprint/blob/master/NOTICE.txt


import functools
from .func_timeout import func_set_timeout
from typing import Callable, Optional, Type, Set, Union


def add_objprint(
        orig_class: Optional[Type] = None,
        format: str = "string", **kwargs) -> Union[Type, Callable[[Type], Type]]:

    from . import _objprint

    if format == "json":
        import json

        def __str__(self) -> str:
            return json.dumps(_objprint.objjson(self), **kwargs)
    else:
        def __str__(self) -> str:
            cfg = _objprint._configs.overwrite(**kwargs)

            @func_set_timeout(timeout=cfg.time_limit)
            def get_result():
                memo: Optional[Set] = set() if cfg.skip_recursion else None
                return _objprint._get_custom_object_str(self, memo, indent_level=0, cfg=cfg)

            return _objprint.run_timeout_func(get_result, (self,), time_limit=cfg.time_limit)

    if orig_class is None:
        def wrapper(cls: Type) -> Type:
            cls.__str__ = functools.wraps(cls.__str__)(__str__)  # type: ignore
            return cls
        return wrapper
    else:
        orig_class.__str__ = functools.wraps(orig_class.__str__)(__str__)  # type: ignore
        return orig_class
