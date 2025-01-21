# src/Bot_App/__init__.py

# Expose functionality from module1 and module2
from .module1 import function1
from .module2 import Class1

# Optional: Define the version of your library
__version__ = "0.1.0"

# Define what gets imported with `from Bot_App import *`
__all__ = ["function1", "Class1"]
