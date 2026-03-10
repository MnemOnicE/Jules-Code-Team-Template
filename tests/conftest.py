import sys
import os

# Add the new engine location to sys.path
engine_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "template_source", ".agents", "engine"))
sys.path.insert(0, engine_path)

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
