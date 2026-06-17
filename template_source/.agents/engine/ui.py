import os
import sys
from textual.app import App, ComposeResult
from textual.containers import Grid, Container
from textual.widgets import Label, ProgressBar, Tree, RichLog, Input
from textual import work
from textual.message import Message

# Import necessary engine components (which will be orchestrated by main.py)
from core.tools.graph_executor import GraphExecutor
from core.plugin_manager import plugin_manager
from core.bus import NexusBus
from main import generate_llm_graph

# --- Custom Messages ---

class UpdateCoT(Message):
    def __init__(self, text: str) -> None:
        self.text = text
        super().__init__()

class UpdateToolFeed(Message):
    def __init__(self, data: dict) -> None:
        self.data = data
        super().__init__()

class UpdateNodeStatus(Message):
    def __init__(self, node_id: str, status: str) -> None:
        self.node_id = node_id
        self.status = status
        super().__init__()

class UpdateGraph(Message):
    def __init__(self, graph: dict) -> None:
        self.graph = graph
        super().__init__()


# --- Main App ---

class AgentTUI(App):
    CSS = """
    Screen {
        layout: grid;
        grid-size: 4 4;
        grid-columns: 1fr 1fr 1fr 1fr;
        grid-rows: 1fr 1fr 1fr 1fr;
    }

    #header-container {
        column-span: 4;
        row-span: 1;
        height: 100%;
        border: solid green;
        background: $panel;
    }

    #mission-label {
        width: 100%;
        text-align: center;
        text-style: bold;
    }

    #mission-progress {
        width: 100%;
        margin-top: 1;
    }

    #task-graph {
        column-span: 1;
        row-span: 2;
        border: solid yellow;
        height: 100%;
    }

    #cot-pane {
        column-span: 3;
        row-span: 1;
        border: solid cyan;
        height: 100%;
    }

    #tool-pane {
        column-span: 3;
        row-span: 1;
        border: solid magenta;
        height: 100%;
    }

    #command-bar {
        column-span: 4;
        row-span: 1;
        height: 100%;
        border: solid blue;
    }
    """

    def __init__(self, task, provider, brain_context, **kwargs):
        super().__init__(**kwargs)
        self.task = task
        self.provider = provider
        self.brain_context = brain_context
        self.tree_nodes = {}  # Map node ID to Tree node
        self.total_nodes = 0
        self.completed_nodes = 0

    def compose(self) -> ComposeResult:
        with Container(id="header-container"):
            yield Label(f"Mission: {self.task}", id="mission-label")
            yield ProgressBar(total=100, show_eta=False, id="mission-progress")

        yield Tree("Execution Plan", id="task-graph")
        yield RichLog(id="cot-pane", highlight=True, markup=True)
        yield RichLog(id="tool-pane", highlight=True, markup=True)
        yield Input(placeholder="Enter command or interrupt...", id="command-bar")

    def on_mount(self) -> None:
        self.query_one("#cot-pane", RichLog).write("[bold cyan]Initializing...[/bold cyan]")
        self.query_one("#tool-pane", RichLog).write("[bold magenta]Waiting for execution...[/bold magenta]")
        self.run_agent(self.task, self.provider, self.brain_context)

    # --- Message Handlers ---

    def on_update_cot(self, event: UpdateCoT) -> None:
        self.query_one("#cot-pane", RichLog).write(event.text)

    def on_update_tool_feed(self, event: UpdateToolFeed) -> None:
        import json
        tool = event.data.get('tool', 'unknown')
        result = event.data.get('result', {})
        try:
            formatted_result = json.dumps(result, indent=2)
        except Exception:
            formatted_result = str(result)

        self.query_one("#tool-pane", RichLog).write(f"[bold magenta]Tool:[/] {tool}\n[bold magenta]Result:[/] {formatted_result}\n---")

    def on_update_graph(self, event: UpdateGraph) -> None:
        tree = self.query_one("#task-graph", Tree)
        tree.clear()
        self.tree_nodes.clear()

        nodes = event.graph.get("nodes", {})
        self.total_nodes = len(nodes)
        if self.total_nodes > 0:
            pb = self.query_one("#mission-progress", ProgressBar)
            pb.update(total=self.total_nodes)

        for node_id, node_data in nodes.items():
            intent = node_data.get('action', node_id)
            label = f"⏳ pending: {node_id} ({intent})"
            tree_node = tree.root.add(label, expand=True)
            self.tree_nodes[node_id] = tree_node

    def on_update_node_status(self, event: UpdateNodeStatus) -> None:
        if event.node_id in self.tree_nodes:
            tree_node = self.tree_nodes[event.node_id]
            # Extract existing node id/intent from label (e.g., "⏳ pending: NODE_ID (INTENT)")
            old_label = str(tree_node.label)
            parts = old_label.split(": ", 1)
            core_label = parts[1] if len(parts) > 1 else old_label

            if event.status == "active":
                tree_node.set_label(f"⚡ active: {core_label}")
            elif event.status == "done":
                tree_node.set_label(f"✅ done: {core_label}")
                self.completed_nodes += 1
                pb = self.query_one("#mission-progress", ProgressBar)
                pb.update(progress=self.completed_nodes)
            elif event.status == "failed":
                tree_node.set_label(f"❌ failed: {core_label}")

    # --- Worker Thread ---

    @work(thread=True)
    def run_agent(self, task, provider, brain_context):
        # Define closures for hooks to post messages
        def handle_cot(text):
            self.post_message(UpdateCoT(text))

        def handle_node_start(data):
            self.post_message(UpdateNodeStatus(data['id'], 'active'))

        def handle_node_complete(data):
            status = 'done' if data['status'] == 'success' else 'failed'
            self.post_message(UpdateNodeStatus(data['id'], status))
            if status == 'failed':
                 self.post_message(UpdateCoT(f"[bold red]Node Failed:[/] {data.get('error', 'Unknown Error')}"))

        def handle_tool_invoke(data):
            self.post_message(UpdateToolFeed(data))

        def handle_graph_generated(graph):
            if isinstance(graph, dict):
                self.post_message(UpdateGraph(graph))

        # Register dynamic hooks
        hooks = {
            'on_cot_thought': handle_cot,
            'on_node_start': handle_node_start,
            'on_node_complete': handle_node_complete,
            'on_tool_invoke': handle_tool_invoke,
            'on_graph_generated': handle_graph_generated
        }

        for event, fn in hooks.items():
            plugin_manager.register_hook(event, fn)

        try:
            # Re-initialize Bus for the worker thread
            bus = NexusBus()
            self.post_message(UpdateCoT("[bold green]NexusBus Online. Generating Execution Graph...[/bold green]"))

            # Generate the execution graph
            graph = generate_llm_graph(task, provider)

            self.post_message(UpdateCoT("[bold green]Executing Graph...[/bold green]"))

            # Execute
            executor = GraphExecutor(bus, system_context=brain_context)
            executor.execute(graph)

            self.post_message(UpdateCoT("[bold green]Mission Complete.[/bold green]"))

        except Exception as e:
            self.post_message(UpdateCoT(f"[bold red]Critical Agent Error:[/] {e}"))
        finally:
            # Always deregister to prevent hook stacking
            for event, fn in hooks.items():
                plugin_manager.deregister_hook(event, fn)

if __name__ == "__main__":
    # Test script entry point if run directly
    print("Run via main.py --ui")
