import sys
import importlib

if __name__ == "__main__":
    script = sys.argv[1].lower()

    module = importlib.import_module(f'_scripts.{script}')

    # Get the function from the module
    func = getattr(module, 'execute_command')
    func()
