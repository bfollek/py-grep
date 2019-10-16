#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List, Optional, Tuple

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
    results: List[str] = []
    for file_name in state.files:
        with open(file_name) as f:
            # Each element in lines is a tuple: (line number, line text).
            # The line numbers start at 0.
            lines = enumerate(f.readlines())
            matches = filter(lambda nxt: _matches(state, nxt[1]), lines)
            results += map(lambda nxt: _fmt_match(state, nxt, file_name), matches)
    if state.options.only_names:
        results = _dedup(results)
    return ''.join(results)

def _dedup(results: List[str]) -> List[str]:
    """
    Remove duplicates.
    """
    d = {} # dictionary preserves insertion order; set does not.
    for result in results:
        d[result] = True
    return list(d) # list(dict) gets the keys

def _matches(state: _State, line: str) -> bool:
    if state.options.ignore_case:
        line = line.lower()
    if state.options.entire_lines:
        match = state.pattern == line
    else:
        match = state.pattern in line
    return not match if state.options.invert else match

def _fmt_match(state: _State, line_tuple: Tuple[int, str], file_name: str) -> str:
    """
    Format result based on the options.
    """
    if state.options.only_names:
        return file_name + '\n' # newline so that multiple lines work right
    (line_num, line_txt) = line_tuple
    result = ''
    if len(state.files) > 1:
        result += f"{file_name}:"
    if state.options.line_numbers:
        result += f"{line_num + 1}:" # zero-based
    result += line_txt
    return result
