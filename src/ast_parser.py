try:
    import error_handling  # installs global excepthook and helpers
except Exception:
    pass

import ast
import sys

def parse_python_file(file_path):
    with open(file_path, 'r') as file:
        source_code = file.read()
    tree = ast.parse(source_code)
    print(ast.dump(tree, indent=4))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ast_parser.py <python_file>")
    else:
        parse_python_file(sys.argv[1])
