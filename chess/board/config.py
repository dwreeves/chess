from typing import Any

DEFAULT_OPTIONS = {
    'display.size': 'big',  # 'big', 'medium', 'small'
    'display.axis_labels': True,
    'display.figurine': False,
    'api.notation_mismatch': 'error',  # 'error', 'warn', or 'ignore'
    'api.notifications': False,
    'api.safe_mode': True
}

options = DEFAULT_OPTIONS.copy()
ALL = '*'


def get_option(key: str):
    try:
        getter = _SPECIAL_GETTERS[key]
    except KeyError:
        return globals()['options'][key]
    else:
        return getter()


def set_option(key: str, val: Any):
    globals()['options'][key] = val


def reset_option(key: str):
    if key == ALL:
        globals()['options'] = DEFAULT_OPTIONS.copy()
    else:
        globals()['options'].update({key: DEFAULT_OPTIONS[key]})


# ~~~~~~

def _get_api_notation_mismatch():
    if not get_option('api.safe_mode'):
        return 'ignore'
    else:
        return globals()['options']['api.notation_mismatch']


_SPECIAL_GETTERS = {
    'api.notation_mismatch': _get_api_notation_mismatch
}
