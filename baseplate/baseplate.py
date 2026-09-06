#!/usr/bin/env python3

import sys
import os

from core import assembler
from core import formatter

def _throw_error(message):
    print(f"error: {message}")
    sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        _throw_error("no program path specified")
    
    path = sys.argv[1]
    if os.path.isfile(path) != True:
        _throw_error(f"no program found at \"{path}\"")

    with open(path, "r") as f:
        asm_lines = f.readlines()

    asm = assembler.Assembler()
    fmt = formatter.Formatter()
    executable = asm.run(asm_lines)
    output = fmt.run(executable)

    with open("out.o", "w") as f:
        f.write(output)