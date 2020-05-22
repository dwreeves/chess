from typing import Any

DEFAULT_OPTIONS = {
    'display.size': 'big',  # 'big', 'medium', 'small'
    'display.axis_labels': True,
    'display.figurine': False,
    'api.stateless': False
}

options = DEFAULT_OPTIONS.copy()
ALL = '*'


def get_option(key: str):
    return globals()['options'][key]


def set_option(key: str, val: Any):
    globals()['options'][key] = val


def reset_option(key: str):
    if key == ALL:
        globals()['options'] = DEFAULT_OPTIONS.copy()
    else:
        globals()['options'].update({key: DEFAULT_OPTIONS[key]})
