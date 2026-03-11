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

import os
from functools import lru_cache

class ContextLoader:
    def __init__(self):
        self.root_dir = self._find_root()
        self.agents_dir = self._find_agents_dir()
        self._tech_stack = None
        self._system_context_cache = {}

    def _find_root(self):
        # Assumes src/core/context.py
        # Go up two levels: src/core/ -> src/ -> root
        return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

    def _find_agents_dir(self):
        # Try root .agents first (Production/Deployed)
        prod_path = os.path.join(self.root_dir, '.agents')
        if os.path.exists(prod_path):
            return prod_path

        # Try template_source/.agents (Development)
        dev_path = os.path.join(self.root_dir, 'template_source', '.agents')
        if os.path.exists(dev_path):
            return dev_path

        raise FileNotFoundError(f"Could not locate .agents configuration directory. Searched: {prod_path}, {dev_path}")

    @lru_cache(maxsize=128)
    def load_persona(self, agent_name):
        """Reads the corresponding .md file for the agent."""
        # Normalize name and sanitize to prevent path traversal
        agent_name = os.path.basename(agent_name.lower())
        filepath = os.path.join(self.agents_dir, 'config', 'defaults', f'{agent_name}.md')

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Persona file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def load_tech_stack(self):
        """Reads TECH_STACK.md."""
        if self._tech_stack is not None:
            return self._tech_stack

        filepath = os.path.join(self.agents_dir, 'config', 'TECH_STACK.md')

        if not os.path.exists(filepath):
             raise FileNotFoundError(f"TECH_STACK.md not found at {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            self._tech_stack = f.read()
            return self._tech_stack

    def build_system_context(self, agent_name):
        """Combines persona and tech stack into a system prompt dictionary."""
        if agent_name in self._system_context_cache:
            return self._system_context_cache[agent_name]

        persona_content = self.load_persona(agent_name)
        tech_stack_content = self.load_tech_stack()

        context = {
            "role": agent_name,
            "persona": persona_content,
            "tech_stack": tech_stack_content,
            "system_prompt": f"{persona_content}\n\n## Technology Stack\n{tech_stack_content}"
        }
        self._system_context_cache[agent_name] = context
        return context

# Module-level helper
_SHARED_LOADER = None

def load_context(agent_name):
    global _SHARED_LOADER
    if _SHARED_LOADER is None:
        _SHARED_LOADER = ContextLoader()
    return _SHARED_LOADER.build_system_context(agent_name)
