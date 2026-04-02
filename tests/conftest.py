
import sys
from unittest.mock import MagicMock
# Patch modules for isolated test environments where dependencies might not be installed
if 'yaml' not in sys.modules:
    sys.modules['yaml'] = MagicMock()
if 'dotenv' not in sys.modules:
    sys.modules['dotenv'] = MagicMock()

from unittest.mock import MagicMock
import importlib.util

# Mock jsonschema if it's not installed in the environment
if importlib.util.find_spec("jsonschema") is None:
    jsonschema_mock = MagicMock()
    class ValidationError(Exception):
        def __init__(self, message, *args, **kwargs):
            self.message = message
            super().__init__(message, *args, **kwargs)

    jsonschema_mock.ValidationError = ValidationError
    sys.modules["jsonschema"] = jsonschema_mock
    sys.modules["jsonschema.validators"] = MagicMock()
