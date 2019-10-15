#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Optional

# -------------------------------------------------------------------

@dataclass
class _Options:
    entire_lines: bool
    ignore_case: bool
    invert: bool
    line_numbers: bool
    only_names: bool

    def __init__(self, flags: str):
        self.entire_lines = '-x' in flags
        self.ignore_case  = '-i' in flags
        self.invert       = '-v' in flags
        self.line_numbers = '-n' in flags
        self.only_names   = '-l' in flags

# -------------------------------------------------------------------

@dataclass
class _State:
    pattern: str
    options: _Options
    files: List[str]

    def __init__(self, pattern: str, flags: str, files: List[str]):
        self.options = _Options(flags)
        self.pattern = pattern.lower() if self.options.ignore_case else pattern
        if self.options.entire_lines:
            self.pattern += '\n' # lines have trailing newlines
        self.files = files

# -------------------------------------------------------------------

def grep(pattern: str, flags: str, files: List[str]) -> str:
    state = _State(pattern, flags, files)
    return _run(state)

def _run(state: _State) -> str:
    results = {} # dict gives us ordered keys, no dups
    for file_name in state.files:
        with open(file_name) as f:
            cnt = 0
            # Doesn't work. (Because of the doctored File object they provide?)
            # for line in f:
            lines = f.readlines()
            for line in lines:
                cnt += 1
                match = _matches(state, line)
                result = _calc_result(state, match, line, cnt, file_name)
                if result:
                    results[result] = True
    return ''.join(list(results)) # list(dict) gets the keys

def _matches(state: _State, line: str) -> bool:
    if state.options.ignore_case:
        line = line.lower()
    if state.options.entire_lines:
        return state.pattern == line
    else:
        return state.pattern in line

def _calc_result(state: _State, match: bool, line: str, cnt: int, file_name: str) -> Optional[str]:
    """
    Potentially save result, depending on the options.
    """
    result = None
    # The invert option means we report what doesn't match.
    if (match and not state.options.invert) or (not match and state.options.invert):
        if state.options.only_names:
            return file_name + '\n'  # newline so that multiple lines work right
        result = ''
        if len(state.files) > 1:
            result += f"{file_name}:"
        if state.options.line_numbers:
            result += f"{cnt}:"
        result += line
    return result
