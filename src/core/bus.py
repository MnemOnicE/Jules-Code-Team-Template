# Jules Code Team Template
# Copyright (C) 2026  MnemOnicE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
from pathlib import Path
import threading
import jsonschema

class NexusBus:
    _schema = None
    _validator = None
    _lock = threading.Lock()

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Use class-level caching for schema and validator to improve performance
        if NexusBus._validator is None:
            with NexusBus._lock:
                if NexusBus._validator is None:
                    # Locate the schema file relative to this file
                    schema_path = Path(__file__).parent / 'schema' / 'execution_graph.json'

                    if not schema_path.exists():
                        raise FileNotFoundError(f"Schema file not found at: {schema_path}")

                    with schema_path.open('r') as f:
                        NexusBus._schema = json.load(f)

                    # Pre-compile the validator for performance
                    ValidatorClass = jsonschema.validators.validator_for(NexusBus._schema)
                    ValidatorClass.check_schema(NexusBus._schema)
                    NexusBus._validator = ValidatorClass(NexusBus._schema)

        self.schema = NexusBus._schema
        self.validator = NexusBus._validator

    def validate_graph(self, graph_data):
        """Validates the given graph data against the Sovereign Execution Graph schema."""
        try:
            self.validator.validate(instance=graph_data)
            self.logger.info("[VALIDATION] Graph structure is valid.")
            return True
        except jsonschema.ValidationError as e:
            self.logger.error(f"[VALIDATION ERROR] {e.message}", exc_info=True)
            raise e

