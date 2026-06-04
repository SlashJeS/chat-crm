import os

from django.core.exceptions import ImproperlyConfigured

_TRUE_VALUES = frozenset({"1", "true", "True", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "False", "no", "off"})


def get_env(name: str) -> str:
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        raise ImproperlyConfigured(f"Required environment variable {name} is not set.")
    return str(value).strip()


def get_optional_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        return None
    return str(value).strip()


def get_bool_env(name: str) -> bool:
    value = os.environ.get(name)
    if value is None or not str(value).strip():
        raise ImproperlyConfigured(f"Required environment variable {name} is not set.")
    normalized = str(value).strip()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False
    raise ImproperlyConfigured(
        f"Environment variable {name} must be a boolean (true/false, 1/0, yes/no, on/off)."
    )


def get_int_env(name: str) -> int:
    value = get_env(name)
    try:
        return int(value)
    except ValueError as exc:
        raise ImproperlyConfigured(
            f"Environment variable {name} must be an integer."
        ) from exc


def get_list_env(name: str, separator: str = ",") -> list[str]:
    value = get_env(name)
    items = [item.strip() for item in value.split(separator) if item.strip()]
    if not items:
        raise ImproperlyConfigured(
            f"Environment variable {name} must contain at least one value."
        )
    return items
