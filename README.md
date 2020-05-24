# Chess

Lightweight chess API built in base Python.

Not done. Just using Github to document the progress.

Things missing other than docstrings and more unit-tests:

- Castling
- En passant
- Pawn promotion
- Updates to algebraic notation parsing:
  - add option `'api.notation_mismatch'` that can be set to `'warn'` `'error'` or `'ignore'` when captures and checks are not correct in notation.
- Optimization. API is very slow.

## Running unit tests:

From the root directory, run:

```shell script
python -m unittest discover -p 'chess/board/tests/'
```
