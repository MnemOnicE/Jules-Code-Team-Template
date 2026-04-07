import re

file_path = "template_source/.agents/engine/main.py"
with open(file_path, "r") as f:
    content = f.read()

# Modify argparse to add --ui flag
argparse_target = """    parser.add_argument("--status", action="store_true", help="Show system status and metrics")"""
argparse_replacement = """    parser.add_argument("--status", action="store_true", help="Show system status and metrics")
    parser.add_argument("--ui", action="store_true", help="Launch the Textual User Interface")"""

content = content.replace(argparse_target, argparse_replacement)

# Update on_graph_generated payload
graph_gen_target = """    plugin_manager.call_plugin_hook('on_graph_generated', graph.get('graph_id', 'unknown'))
    print(f"✅ Generated Execution Graph ({graph.get('graph_id', 'unknown')})")"""
graph_gen_replacement = """    plugin_manager.call_plugin_hook('on_graph_generated', graph)
    print(f"✅ Generated Execution Graph ({graph.get('graph_id', 'unknown')})")"""

content = content.replace(graph_gen_target, graph_gen_replacement)

# Add TUI handoff logic
# First find the context/provider loading part and replace the execution block
handoff_target = """    # 3. Generate Execution Graph (Brain)
    print(f"🧠 Brain: Analyzing task: '{task}'")
    monitor.increment_metric('llm_calls')
    graph = generate_llm_graph(task, provider)"""

handoff_replacement = """    if args.ui:
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
    graph = generate_llm_graph(task, provider)"""

content = content.replace(handoff_target, handoff_replacement)

with open(file_path, "w") as f:
    f.write(content)
