import sys

from core import preprocessor
from core import arch
from core import grammar

class Assembler:
    def __init__(self):
        self._preprocessor = preprocessor.Preprocessor()
        self._special_assemblers = {
            "jump": self._assemble_jump,
            "jumpif0": self._assemble_jump
        }
        self._operand_types = ["c", "m", "io"]

    def run(self, asm_lines):
        output = []
        processed_lines = self._preprocessor.run(asm_lines)

        for line_parts in processed_lines:
            if line_parts[0].startswith(grammar.DIRECTIVE_TOKEN):
                continue

            instruction_name = line_parts[0]
            operands = line_parts[1:]
            if instruction_name in self._special_assemblers.keys():
                output_instruction = self._special_assemblers[instruction_name](
                    instruction_name,
                    operands
                )

            else:
                output_instruction = self._assemble_generic(
                    instruction_name,
                    operands
                )

            output.append(output_instruction)

        return output

    def _assemble_generic(self, instruction_name, operands):
        output = [self._assemble_opcode(instruction_name)]
        output.extend(self._assemble_operands(operands))
        return output

    def _assemble_jump(self, instruction_name, operands):
        output = [self._assemble_opcode(instruction_name)]
        label_name = operands[0]
        label_index = self._preprocessor.get_label(label_name)
        if label_index == None:
            self._throw_error(f"use of undefined label \"{label_name}\"")

        output.append(label_index)
        output.extend(self._assemble_operands(operands[1:]))
        return output

    def _assemble_opcode(self, instruction_name):
        if instruction_name not in arch.INSTRUCTIONS.keys():
            self._throw_error(f"unknown instruction \"{instruction_name}\"")

        return arch.INSTRUCTIONS[instruction_name]

    def _assemble_operands(self, operands):
        output = []
        for operand in operands:
            # handle types
            for operand_type_prefix in self._operand_types:
                if operand.startswith(operand_type_prefix):
                    int_operand = self._operand_to_int(
                        operand[len(operand_type_prefix):],
                        operand
                    )
                    output.append(int_operand)
                    break

            else:
                output.append(self._operand_to_int(operand, operand))

        return output

    def _operand_to_int(self, operand, original_operand):
        try:
            return int(operand)

        except ValueError:
            self._throw_error(f"invalid operand \"{original_operand}\"")

    def _throw_error(self, message):
        print(f"assembler error: {message}")
        sys.exit(1)