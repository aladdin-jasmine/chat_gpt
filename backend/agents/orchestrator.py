class AgentOrchestrator:
    def __init__(self):
        self.agents = {}

    def register(self, name, agent):
        self.agents[name] = agent

    async def execute(self, task, payload):
        if task in self.agents:
            return await self.agents[task].run(payload)
        return {'error': 'agent not found'}
