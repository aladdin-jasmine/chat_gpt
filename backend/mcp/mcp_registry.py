class MCPRegistry:
    def __init__(self):
        self.servers = {
            'github': 'GitHub MCP',
            'browser': 'Browser MCP',
            'filesystem': 'Filesystem MCP',
            'database': 'Database MCP',
            'kubernetes': 'Kubernetes MCP'
        }

    def list_servers(self):
        return self.servers
