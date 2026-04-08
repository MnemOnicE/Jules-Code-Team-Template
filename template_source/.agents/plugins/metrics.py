# Example Plugin for Jules Code Team
# Demonstrates the plugin system capabilities

PLUGIN_INFO = {
    'name': 'Metrics Plugin',
    'version': '1.0.0',
    'description': 'Tracks and reports agent performance metrics',
    'author': 'Jules Code Team'
}

def on_session_start(task):
    """Called when a session starts"""
    print(f"📊 Metrics: Session started - Task length: {len(task)} characters")
    return True

def on_graph_generated(graph_id):
    """Called when a graph is generated"""
    print(f"📊 Metrics: Graph generated - ID: {graph_id}")
    return True

def on_session_complete(graph_id):
    """Called when a session completes"""
    print(f"📊 Metrics: Session completed - Graph: {graph_id}")
    return True