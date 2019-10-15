from dataclasses import dataclass
from typing import List, Optional

class Grepper:
    def __init__(self, pattern: str, flags: str, files: List[str]):
        self._files = files
        self._options = _Options(flags)
        self._pattern = pattern.lower() if self._options.ignore_case else pattern
        if self._options.entire_lines:
            self._pattern += '\n' # lines have trailing newlines

    def run(self) -> str:
        results = {} # dict gives us ordered keys, no dups
        for file_name in self._files:
            with open(file_name) as f:
                cnt = 0
                # Doesn't work. (Because of the doctored File object they provide?)
                # for line in f:
                lines = f.readlines()
                for line in lines:
                    cnt += 1
                    match = self._matches(line)
                    result = self._calc_result(match, line, cnt, file_name)
                    if result:
                        results[result] = True
        return ''.join(list(results)) # list(dict) gets the keys

    def _matches(self, line: str) -> bool:
        if self._options.ignore_case:
            line = line.lower()
        if self._options.entire_lines:
            return self._pattern == line
        else:
            return self._pattern in line

    def _calc_result(self, match: bool, line: str, cnt: int, file_name: str) -> Optional[str]:
        """
        Potentially save result, depending on the options.
        """
        result = None
        # The invert option means we report what doesn't match.
        if (match and not self._options.invert) or (not match and self._options.invert):
            if self._options.only_names:
                return file_name + '\n'  # newline so that multiple lines work right
            result = ''
            if len(self._files) > 1:
                result += f"{file_name}:"
            if self._options.line_numbers:
                result += f"{cnt}:"
            result += line
        return result

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