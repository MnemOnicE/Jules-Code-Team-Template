import sys
from unittest.mock import MagicMock
import importlib.util

# Mock jsonschema if it's not installed in the environment
if importlib.util.find_spec("jsonschema") is None:
    jsonschema_mock = MagicMock()
    class ValidationError(Exception):
        pass
    jsonschema_mock.ValidationError = ValidationError
    sys.modules["jsonschema"] = jsonschema_mock
    sys.modules["jsonschema.validators"] = MagicMock()
