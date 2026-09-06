class Formatter:
    def __init__(self):
        pass

    def run(self, executable):
        output = ""
        for instruction in executable:
            output += ' '.join([str(part) for part in instruction]) + '\n'

        return output.strip()