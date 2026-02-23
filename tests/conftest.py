import sys
from unittest.mock import MagicMock

# Mock jsonschema before any imports that might use it
if "jsonschema" not in sys.modules:
    jsonschema_mock = MagicMock()
    class ValidationError(Exception):
        pass
    jsonschema_mock.ValidationError = ValidationError
    sys.modules["jsonschema"] = jsonschema_mock
    sys.modules["jsonschema.validators"] = MagicMock()
