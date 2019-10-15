#!/usr/bin/env python3

from dataclasses import dataclass
from typing import List

from grepper import Grepper

def grep(pattern: str, flags: str, files: List[str]) -> str:
    grepper = Grepper(pattern, flags, files)
    return grepper.run()
