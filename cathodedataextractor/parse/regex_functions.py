# coding=utf-8
from . import POLYATOMIC_IONS
from functools import lru_cache

__all__ = ['end_parentheses', 'bracket_level']

OPEN, CLOSE = {'(', '[', '{'}, {')', ']', '}'}
OP_CL = {'(': ')', '[': ']', '{': '}'}
MIN_LENGTH = 11  # The threshold determines whether the return value is meaningful


@lru_cache(None)
def end_parentheses(cem: str):
    """
    Find the supplementary information string after the balanced
    or unbalanced bracket closest to the end of the chemical formula string.

    Lesson: The unbalanced bracket case only has a missing right bracket.
    Note: Nax(Cu-Fe-Mn) O2, NaFexCr1-X(SO4)2, etc. with return (None, None).

    Returns:
         (int, str[int:]) or (None, None).
    """
    stack, bracket_index, first_end = [], -1, True
    for i in range(len(cem) - 1, -1, -1):
        if cem[i] in CLOSE:
            if first_end:
                first_end = False
                if cem[i + 1:].endswith('O2') or cem[i + 1:].isdigit():
                    return None, None
            stack.append(i)
        elif cem[i] in OPEN:
            if stack:  # Indicates that it is not possible to find an unbalanced bracket.
                # Goal: Find the closest balanced bracket to the right
                CLindex = stack.pop()
                if cem[CLindex] != OP_CL[cem[i]]:
                    return i, cem[i:]
                if bracket_index == -1 and polyatomic_ions(cem[i + 1:CLindex]):
                    return None, None
                if not stack:
                    bracket_index = max(i, bracket_index)
            else:  # Unbalanced parentheses, return directly
                if polyatomic_ions(cem[i + 1:]):
                    return None, None
                return i, cem[i:]
    return (bracket_index, cem[bracket_index:]) if bracket_index > MIN_LENGTH else (None, None)


@lru_cache(None)
def polyatomic_ions(string):
    return any(_ == string for _ in POLYATOMIC_IONS)


@lru_cache(None)
def bracket_level(text):
    """
    Return 0 if string contains balanced brackets or no brackets.
    """
    level = 0
    for c in text:
        if c in OPEN:
            level += 1
        elif c in CLOSE:
            level -= 1
    return level
