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
import uuid
import os

# Imports
try:
    from src.core.bus import NexusBus
    from src.core.context import load_context
    from src.core.tools.graph_executor import GraphExecutor
    from src.core.llm_provider import get_llm_provider
    from src.core.llm_config import LLMConfigManager
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)


def generate_mock_graph(task_description):
    """
    Generates a static execution graph for demonstration.
    Adheres to src/core/schema/execution_graph.json
    """
    graph_id = str(uuid.uuid4())

    return {
        "graph_id": graph_id,
        "intent_glyph": "🤖",
        "aether_mark": "mock_signature_verified",
        "entry_point": "node_1",
        "context_delta": {},
        "nodes": {
            "node_1": {
                "action": "logic_gate",
                "params": {
                    "condition": "Is task valid?"
                },
                "on_success": "node_2",
                "on_failure": "node_fail"
            },
            "node_2": {
                "action": "run_tool",
                "params": {
                    "tool": "plan_decomposition",
                    "args": {"task": task_description}
                },
                "on_success": "node_4"
            },
            "node_4": {
                "action": "terminate",
                "params": {}
            },
            "node_fail": {
                 "action": "terminate",
                 "params": {}
            }
        }
    }

def main():
    parser = argparse.ArgumentParser(description="Agent System V3 Command Interface")
    parser.add_argument("--task", type=str, help="The natural language task to perform")
    parser.add_argument("--file", type=str, help="A file to process")
    parser.add_argument("-c", "--config-llm", action="store_true", help="Run the interactive LLM configuration wizard")
    parser.add_argument("--llm", type=str, help="Override active LLM provider (openai, gemini, jules, ollama, llamacpp)")
    parser.add_argument("--model-path", type=str, help="Override model path or name (for local models)")
    parser.add_argument("-rs", "--raw-send", action="store_true", help="Output raw JSON payload sent to the LLM")
    parser.add_argument("-rr", "--raw-return", action="store_true", help="Output raw JSON response from the LLM")

    args = parser.parse_args()

    if args.config_llm:
        from src.core.llm_config import configure_llm_providers
        configure_llm_providers()
        sys.exit(0)

    # Initialize Config
    config_mgr = LLMConfigManager()

    # Check if we have an active provider, if not prompt
    if not config_mgr.get_active_provider() and not args.llm:
        print("⚠️ No LLM configuration found.")
        from src.core.llm_config import configure_llm_providers
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
    # Test LLM connection
    try:
        provider = get_llm_provider(
            provider_name=args.llm,
            raw_send=args.raw_send,
            raw_return=args.raw_return
        )
        print(f"✅ LLM Provider Ready: {type(provider).__name__}")
    except Exception as e:
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

    # 3. Generate Execution Graph (Brain)
    print(f"🧠 Brain: Analyzing task: '{task}'")
    graph = generate_mock_graph(task)
    print(f"✅ Generated Execution Graph ({graph['graph_id']})")

    # 4. Execute (Muscles)
    print("\n🚀 \033[1mExecuting Graph...\033[0m")
    executor = GraphExecutor(bus)
    executor.execute(graph)

    print("\n✨ Mission Complete.")

if __name__ == "__main__":
    main()
