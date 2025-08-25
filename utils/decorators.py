from functools import wraps
from typing import Dict, Any


def singleton(cls):
    """
    Decorator to make any class a singleton.

    Usage:
        @singleton
        class MyClass:
            def __init__(self):
                pass
    """
    instances: Dict[Any, Any] = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
