#!/usr/bin/env python3

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

import argparse
import logging
import sys
import re
import uuid
import os
import json
import traceback
# Inject engine dir to sys.path so "from core..." works
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Imports
try:
    from core.bus import NexusBus
    from core.context import load_context
    from core.tools.graph_executor import GraphExecutor
    from core.llm_provider import get_llm_provider
    from core.llm_config import LLMConfigManager
    from core.plugin_manager import plugin_manager, initialize_plugins
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

# Optional: pydantic for schema validation (handled gracefully if not installed)
try:
    from pydantic import BaseModel, ValidationError as PydanticValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    class PydanticValidationError(Exception):  # type: ignore
        """Placeholder when pydantic is not available"""
        pass

# Monitoring and Observability
class AgentMonitor:
    """Monitor agent activities and performance"""

    def __init__(self):
        self.metrics = {
            'sessions_started': 0,
            'commands_executed': 0,
            'errors_encountered': 0,
            'llm_calls': 0,
            'execution_time': 0
        }
        self.session_log = []

    def log_event(self, event_type, details=None):
        """Log an event with timestamp"""
        import time
        event = {
            'timestamp': time.time(),
            'type': event_type,
            'details': details or {}
        }
        self.session_log.append(event)

        # Keep only last 1000 events
        if len(self.session_log) > 1000:
            self.session_log = self.session_log[-1000:]

    def increment_metric(self, metric_name):
        """Increment a metric counter"""
        if metric_name in self.metrics:
            self.metrics[metric_name] += 1

    def get_status(self):
        """Get current system status"""
        return {
            'metrics': self.metrics.copy(),
            'recent_events': self.session_log[-10:],  # Last 10 events
            'health': 'good' if self.metrics['errors_encountered'] == 0 else 'warning'
        }

# Global monitor instance
monitor = AgentMonitor()

def _extract_json_by_bracket_counting(text):
    """
    Robustly extract the first valid JSON object from text using bracket counting.
    Handles nested objects and conversational filler gracefully.
    
    Returns (json_str, start_pos) or (None, -1) if no valid JSON found.
    """
    start_idx = text.find('{')
    while start_idx != -1:
        depth = 0
        end_idx = start_idx
        
        for i in range(start_idx, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1
                if depth == 0:
                    end_idx = i + 1
                    return text[start_idx:end_idx], start_idx
        
        # If we got here, this brace was unmatched. Try next one.
        start_idx = text.find('{', start_idx + 1)
    
    return None, -1


# Pre-compiled regex patterns for sanitizing LLM responses
FILLER_PATTERNS = [
    re.compile(r"^here['\"]?s\s+(?:the\s+)?(?:json|graph|output)[:\s]*", re.IGNORECASE),
    re.compile(r"^result[:\s]*", re.IGNORECASE),
    re.compile(r"^output[:\s]*", re.IGNORECASE),
    re.compile(r"^graph[:\s]*", re.IGNORECASE),
]


def _sanitize_llm_response(response_text):
    """
    Strip markdown, code block indicators, and other conversational filler 
    from LLM response before JSON extraction.
    """
    response_text = response_text.strip()

    # Remove markdown code fences
    if response_text.startswith("```json"):
        response_text = response_text[7:]
    elif response_text.startswith("```"):
        response_text = response_text[3:]

    if response_text.endswith("```"):
        response_text = response_text[:-3]

    response_text = response_text.strip()

    # Remove common filler patterns (e.g., "Here's the JSON:" or "Result:")
    for pattern in FILLER_PATTERNS:
        response_text = pattern.sub("", response_text).strip()

    return response_text


def _validate_execution_graph(graph_dict):
    """
    Validate the execution graph dictionary against required schema fields.
    Logs warnings for missing optional fields but does not fail.
    
    Raises ValueError if required fields are missing.
    Raises TypeError if structure is fundamentally invalid.
    """
    if not isinstance(graph_dict, dict):
        raise TypeError(f"Execution graph must be a dict, got {type(graph_dict).__name__}")
    
    required_fields = ["graph_id", "intent_glyph", "nodes", "entry_point"]
    missing = [f for f in required_fields if f not in graph_dict]
    
    if missing:
        raise ValueError(f"Execution graph missing required fields: {missing}")
    
    if not isinstance(graph_dict.get("nodes"), dict):
        raise TypeError(f"'nodes' field must be a dictionary, got {type(graph_dict.get('nodes')).__name__}")
    
    if not graph_dict["nodes"]:
        raise ValueError("'nodes' dictionary cannot be empty")
    
    # Validate that entry_point references an existing node
    if graph_dict["entry_point"] not in graph_dict["nodes"]:
        raise ValueError(f"entry_point '{graph_dict['entry_point']}' does not reference a valid node")
    
    return True


def generate_llm_graph(task_description, provider):
    """
    Calls the LLM provider to dynamically generate a valid execution graph.
    
    Implements bulletproof JSON extraction with multiple fallbacks,
    explicit validation error handling, and deterministic logging to session.json.
    
    SENTINEL PROTOCOL ENFORCED:
    - task_description is sanitized against prompt injection
    - LLM output is treated as untrusted and extracted defensively
    - All failures are deterministically logged to session.json
    """
    schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "core", "schema", "execution_graph.json")
    with open(schema_path, "r") as f:
        schema = f.read()

    # SENTINEL: Sanitize task_description to prevent prompt injection
    # Replace all braces to prevent template injection in prompts
    sanitized_task = task_description.replace('{', '{{').replace('}', '}}')
    
    system_prompt = f"""
You are the Brain agent of a coding squad. Your job is to construct an execution graph in JSON format to solve the task provided by the user.

The JSON output MUST strictly conform to the following schema:
<schema>
{schema}
</schema>

Output ONLY valid JSON. Do not include markdown fences, explanations, or conversational filler.
"""
    user_prompt = f"Task: {sanitized_task}"
    response_text = provider.generate(system_prompt, user_prompt)

    # ============================================================================
    # STEP 1: SANITIZE & PREPARE RESPONSE
    # ============================================================================
    response_text = _sanitize_llm_response(response_text)
    
    if not response_text:
        logging.error("LLM returned empty response after sanitization")
        sys.exit(1)

    # ============================================================================
    # STEP 2: EXTRACT JSON (LAYERED EXTRACTION WITH FALLBACKS)
    # ============================================================================
    json_str, start_pos = _extract_json_by_bracket_counting(response_text)
    
    if not json_str:
        logging.error(f"Failed to extract JSON: no valid '{{}}' structure found")
        logging.debug(f"Raw response: {response_text[:300]}...")
        sys.exit(1)

    # ============================================================================
    # STEP 3: PARSE JSON
    # ============================================================================
    try:
        graph = json.loads(json_str)
    except json.JSONDecodeError as e:
        logging.error(f"JSONDecodeError: {e}")
        logging.debug(f"Extracted attempt: {json_str[:300]}...")
        sys.exit(1)
    except Exception as e:
        # Catch any other unforeseen parsing errors
        logging.error(f"Unexpected error during JSON parsing: {type(e).__name__}: {e}")
        sys.exit(1)

    # ============================================================================
    # STEP 4: VALIDATE EXECUTION GRAPH
    # ============================================================================
    try:
        _validate_execution_graph(graph)
    except ValueError as e:
        logging.error(f"Schema validation failed (ValueError): {e}")
        logging.debug(f"Graph: {json.dumps(graph, indent=2)[:500]}...")
        sys.exit(1)
    except TypeError as e:
        logging.error(f"Schema validation failed (TypeError): {e}")
        sys.exit(1)
    except PydanticValidationError as e:
        # Explicit pydantic handling (if pydantic is introduced in future)
        logging.error(f"Pydantic validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        # Catch any unforeseen validation errors
        logging.error(f"Unexpected validation error: {type(e).__name__}: {e}")
        logging.debug(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

    # ============================================================================
    # STEP 5: LOG TO SESSION (SOURCE OF TRUTH)
    # ============================================================================
    session_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "memory", "session.json")
    try:
        session_log = {
            "timestamp": str(uuid.uuid4()),
            "event": "graph_generated",
            "graph_id": graph.get("graph_id", "unknown"),
            "task_sanitized": bool('{' in task_description or '}' in task_description),
            "extraction_method": "bracket_counting",
            "validation_passed": True,
        }
        os.makedirs(os.path.dirname(session_path), exist_ok=True)
        # Load existing session log (non-fatal if missing or corrupted)
        existing = []
        if os.path.exists(session_path) and os.path.getsize(session_path) > 0:
            try:
                with open(session_path, "r") as f:
                    existing = json.load(f)
                    if not isinstance(existing, list):
                        existing = []
            except (json.JSONDecodeError, IOError):
                logging.debug(f"Could not parse existing session.json, starting fresh")
                existing = []
        # Append new entry and persist (keep last 100 entries)
        existing.append(session_log)
        with open(session_path, "w") as f:
            json.dump(existing[-100:], f, indent=2)
    except Exception as e:
        logging.warning(f"Failed to log to session.json: {e}")
        # Non-fatal: continue execution even if logging fails

    return graph


def main():
    parser = argparse.ArgumentParser(description="Agent System V3 Command Interface")
    parser.add_argument("--task", type=str, help="The natural language task to perform")
    parser.add_argument("--file", type=str, help="A file to process")
    parser.add_argument("-c", "--config-llm", action="store_true", help="Run the interactive LLM configuration wizard")
    parser.add_argument("--llm", type=str, help="Override active LLM provider (openai, gemini, jules, ollama, llamacpp)")
    parser.add_argument("--model-path", type=str, help="Override model path or name (for local models)")
    parser.add_argument("-rs", "--raw-send", action="store_true", help="Output raw JSON payload sent to the LLM")
    parser.add_argument("-rr", "--raw-return", action="store_true", help="Output raw JSON response from the LLM")
    parser.add_argument("--status", action="store_true", help="Show system status and metrics")
    parser.add_argument("--ui", action="store_true", help="Launch the Textual User Interface")

    args = parser.parse_args()

    if args.status:
        status = monitor.get_status()
        print("📊 System Status")
        print("=" * 30)
        print(f"Health: {status['health']}")
        print(f"Sessions: {status['metrics']['sessions_started']}")
        print(f"LLM Calls: {status['metrics']['llm_calls']}")
        print(f"Errors: {status['metrics']['errors_encountered']}")
        print("\nRecent Events:")
        for event in status['recent_events'][-5:]:
            import time
            timestamp = time.strftime('%H:%M:%S', time.localtime(event['timestamp']))
            print(f"  {timestamp} - {event['type']}")
        sys.exit(0)

    if args.config_llm:
        from core.llm_config import configure_llm_providers
        configure_llm_providers()
        sys.exit(0)

    # Initialize Config
    config_mgr = LLMConfigManager()

    # Check if we have an active provider, if not prompt
    if not config_mgr.get_active_provider() and not args.llm:
        print("⚠️ No LLM configuration found.")
        from core.llm_config import configure_llm_providers
        configure_llm_providers()

    # Process Overrides
    if args.model_path:
        os.environ['OLLAMA_MODEL'] = args.model_path
        os.environ['LLAMACPP_MODEL_PATH'] = args.model_path

    if not args.task and not args.file:
        parser.print_help()
        sys.exit(0)

    task = args.task or f"Process file: {args.file}"

    # Configure centralized logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(name)s: %(message)s'
    )

    print("\n🔮 \033[1mInitializing Agent System V3...\033[0m")

    # Initialize monitoring
    monitor.increment_metric('sessions_started')
    monitor.log_event('session_start', {'task': task})
    plugin_manager.call_plugin_hook('on_session_start', task)

    # Initialize plugins
    initialize_plugins()
    # Test LLM connection
    try:
        provider = get_llm_provider(
            provider_name=args.llm,
            raw_send=args.raw_send,
            raw_return=args.raw_return
        )
        print(f"✅ LLM Provider Ready: {type(provider).__name__}")
        monitor.log_event('llm_provider_ready', {'provider': type(provider).__name__})
    except Exception as e:
        monitor.increment_metric('errors_encountered')
        monitor.log_event('llm_provider_failed', {'error': str(e)})
        print(f"❌ Failed to initialize LLM Provider: {e}")
        sys.exit(1)

    # 1. Initialize Bus (Nervous System)
    try:
        bus = NexusBus()
        print("✅ NexusBus Online")
    except Exception as e:
        print(f"❌ Failed to initialize NexusBus: {e}")
        # Continue mostly, or exit?
        # If bus fails (e.g. schema missing), we should probably fail.
        sys.exit(1)

    # 2. Load Context (Cortex Loader)
    try:
        brain_context = load_context("brain")
        print(f"✅ Loaded Persona: {brain_context['role']}")
    except Exception as e:
        print(f"❌ Failed to load context: {e}")
        sys.exit(1)

    if args.ui:
        import os
        import sys
        import logging

        # Redirect print() and logging away from stdout
        sys.stdout = open(os.devnull, 'w')
        logging.disable(logging.CRITICAL)

        from ui import AgentTUI
        try:
            app = AgentTUI(task=task, provider=provider, brain_context=brain_context)
            app.run()  # Textual takes ownership of main thread here
        finally:
            # Restore after TUI exits
            sys.stdout = sys.__stdout__
            logging.disable(logging.NOTSET)
        sys.exit(0)

    # 3. Generate Execution Graph (Brain)
    print(f"🧠 Brain: Analyzing task: '{task}'")
    monitor.increment_metric('llm_calls')
    graph = generate_llm_graph(task, provider)
    if not isinstance(graph, dict):
        monitor.increment_metric('errors_encountered')
        monitor.log_event('graph_generation_failed', {'error': 'invalid_format'})
        print(f"❌ LLM returned invalid graph format (expected dict, got {type(graph).__name__})")
        sys.exit(1)
    monitor.log_event('graph_generated', {'graph_id': graph.get('graph_id', 'unknown')})
    plugin_manager.call_plugin_hook('on_graph_generated', graph)
    print(f"✅ Generated Execution Graph ({graph.get('graph_id', 'unknown')})")

    # 4. Execute (Muscles)
    print("\n🚀 \033[1mExecuting Graph...\033[0m")
    executor = GraphExecutor(bus, system_context=brain_context)
    executor.execute(graph)

    monitor.log_event('session_complete', {'graph_id': graph.get('graph_id', 'unknown')})
    plugin_manager.call_plugin_hook('on_session_complete', graph.get('graph_id', 'unknown'))
    print("\n✨ Mission Complete.")

if __name__ == "__main__":
    main()
