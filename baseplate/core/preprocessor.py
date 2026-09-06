import sys
import os

from core import grammar

class Preprocessor:
    def __init__(self):
        self._directives = {
            "include": self._process_include,
            "label": self._process_label,
            "macro": self._process_macro
        }

        self._labels = {}
        self._macros = {}

    def run(self, asm_lines):
        processed_lines = self._process_lines(asm_lines)
        include_count = 0

        while True:
            included_program_lines = None
            for instruction_index, line_parts in enumerate(processed_lines):
                if not line_parts[0].startswith(grammar.DIRECTIVE_TOKEN):
                    continue

                directive_name = line_parts[0][len(grammar.DIRECTIVE_TOKEN):] # truncate token
                if directive_name not in self._directives.keys():
                    self._throw_error(f"unknown directive \"{directive_name}\"")

                included_program_lines = self._directives[directive_name](instruction_index, line_parts[1:])
                if included_program_lines != None:
                    break

            # reprocess entire program on include
            if included_program_lines != None:
                if include_count > 1000:
                    self._throw_error("infinite include detected")
                    
                del processed_lines[instruction_index]
                processed_lines[instruction_index:instruction_index] = included_program_lines
                include_count += 1

            else:
                break

        try:
            return self._process_macros(processed_lines)

        except RecursionError:
            self._throw_error("macro recursion depth limit exceeded")

    def get_label(self, name):
        return self._labels.get(name)

    def _process_lines(self, asm_lines):
        processed_lines = []
        multiline_parts = []
        for asm_line in asm_lines:
            # ignore whitespace
            if len(asm_line) == 0 or asm_line.isspace():
                continue

            line_parts = asm_line.strip().split(' ')
            
            processed_parts = []

            # process comments
            for part in line_parts:
                valid_part_chars = ""
                is_commented = False
                for char in part:
                    if char == grammar.COMMENT_TOKEN:
                        is_commented = True
                        break
        
                    valid_part_chars += char

                if len(valid_part_chars) > 0:
                    processed_parts.append(valid_part_chars)

                if is_commented == True:
                    break

            if len(processed_parts) == 0:
                continue

            # multi-line support
            if processed_parts[0] == grammar.MULTILINE_TOKEN:
                del processed_parts[0]
                multiline_parts.extend(processed_parts)

            else:
                if len(multiline_parts) > 0:
                    processed_lines.append(multiline_parts)
                    multiline_parts = []

                else:
                    processed_lines.append(processed_parts)

        # flush remaining multiline parts
        if len(multiline_parts) > 0:
            processed_lines.append(multiline_parts)

        return processed_lines

    def _process_macros(self, lines):
        processed_lines = []
        for line_parts in lines:
            line_index = 0
            processed_line_parts = []

            # macro definitions are shielded
            if line_parts[0].startswith(grammar.DIRECTIVE_TOKEN) and line_parts[1] in self._macros.keys():
                processed_line_parts.extend(line_parts[:2])
                line_index = 2

            while line_index < len(line_parts):
                part = line_parts[line_index]
                if part in self._macros.keys():
                    processed_macro = self._process_macros([self._macros[part]])[0]
                    processed_line_parts.extend(processed_macro)

                else:
                    processed_line_parts.append(part)

                line_index += 1

            processed_lines.append(processed_line_parts)

        return processed_lines

    def _process_include(self, instruction_index, operands):
        if len(operands) < 1:
            self._throw_error("not enough operands for include")

        program_path = ' '.join(operands)
        if os.path.isfile(program_path) != True:
            self._throw_error(f"no program to include found at \"{program_path}\"")

        with open(program_path, "r") as f:
            asm_lines = f.readlines()

        processed_lines = self._process_lines(asm_lines)
        return processed_lines

    def _process_label(self, instruction_index, operands):
        if len(operands) < 1:
            self._throw_error("not enough operands for label")

        label_name = operands[0]
        self._labels[label_name] = instruction_index
        return None

    def _process_macro(self, instruction_index, operands):
        if len(operands) < 2:
            self._throw_error("not enough operands for macro")

        macro_name = operands[0]
        if macro_name.startswith(grammar.DIRECTIVE_TOKEN):
            self._throw_error(f"macro \"{macro_name}\" cannot operate on directives")

        macro_value = operands[1:]
        self._macros[macro_name] = macro_value
        return None

    def _throw_error(self, message):
        print(f"preprocessor error: {message}")
        sys.exit(1)