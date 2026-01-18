import os

class ContextLoader:
    def __init__(self):
        self.root_dir = self._find_root()
        self.agents_dir = self._find_agents_dir()

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

    def load_persona(self, agent_name):
        """Reads the corresponding .md file for the agent."""
        # Normalize name
        agent_name = agent_name.lower()
        filepath = os.path.join(self.agents_dir, 'config', 'defaults', f'{agent_name}.md')

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Persona file not found: {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def load_tech_stack(self):
        """Reads TECH_STACK.md."""
        filepath = os.path.join(self.agents_dir, 'config', 'TECH_STACK.md')

        if not os.path.exists(filepath):
             raise FileNotFoundError(f"TECH_STACK.md not found at {filepath}")

        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()

    def build_system_context(self, agent_name):
        """Combines persona and tech stack into a system prompt dictionary."""
        persona_content = self.load_persona(agent_name)
        tech_stack_content = self.load_tech_stack()

        return {
            "role": agent_name,
            "persona": persona_content,
            "tech_stack": tech_stack_content,
            "system_prompt": f"{persona_content}\n\n## Technology Stack\n{tech_stack_content}"
        }

# Module-level helper
def load_context(agent_name):
    loader = ContextLoader()
    return loader.build_system_context(agent_name)
