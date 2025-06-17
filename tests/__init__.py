import os
import sys

# Ensure the package under src is discoverable during tests
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
