import os
import importlib

# Define the package version
__version__ = '0.1.0'

# Automatically import all submodules and make them available
__all__ = []

# Get the directory path for the current package
package_dir = os.path.dirname(__file__)

# Walk through the directory to find all modules
for root, _, files in os.walk(package_dir):
    for file in files:
        if file.endswith('.py') and file != '__init__.py':  # Ignore __init__.py itself
            # Build the module name relative to the package
            relative_path = os.path.relpath(root, package_dir)
            module_name = os.path.splitext(file)[0]
            if relative_path != '.':
                module_name = f"{relative_path.replace(os.sep, '.')}.{module_name}"
            
            # Import the module dynamically
            full_module_name = f"{__name__}.{module_name}"
            imported_module = importlib.import_module(full_module_name)

            # Add all public names (if defined) or the module itself to __all__
            if hasattr(imported_module, '__all__'):
                __all__.extend([f"{module_name}.{name}" for name in imported_module.__all__])
            else:
                __all__.append(module_name)
