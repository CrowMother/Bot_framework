# src/Bot_App/__init__.py

# Expose functionality from module1 and module2
"""Bot_App package initialization.

This module exposes utilities and other helpers. Some submodules have
additional third‑party dependencies which may not be installed in all
environments (e.g. during testing). To keep imports lightweight and avoid
ImportError when optional dependencies are missing, each import is wrapped in a
``try``/``except`` block.  When a dependency is unavailable the corresponding
module is simply skipped.
"""

# Always expose util as it has no external requirements
from .util import *

# Optionally expose additional modules. Missing third‑party dependencies should
# not cause import failures during test discovery.
try:  # schwabdev dependency
    from .schwab import *
except Exception:  # pragma: no cover - optional dependency
    pass

try:  # may require database drivers
    from .data import *
    from .SQL import *
except Exception:  # pragma: no cover - optional dependency
    pass

try:  # web framework dependencies
    from .webhook import *
except Exception:  # pragma: no cover - optional dependency
    pass

try:  # google API dependencies
    from .gsheet import *
except Exception:  # pragma: no cover - optional dependency
    pass

# Optional: Define the version of your library
__version__ = "0.2.0"

# Define what gets imported with `from Bot_App import *`
# __all__ = ["function1", "Class1"]
