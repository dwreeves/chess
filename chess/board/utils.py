def sign(x: float) -> int:
    return x and (-1 if x < 0 else 1)


def invert_color(s: str) -> str:
    return {
        'white': 'black',
        'black': 'white'
    }[s]
