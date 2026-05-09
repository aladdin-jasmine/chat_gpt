class GoalEngine:
    def __init__(self):
        self.goals = {}

    async def register_goal(self, goal_id: str, objective: str):
        self.goals[goal_id] = {
            'objective': objective,
            'status': 'active',
            'subtasks': []
        }

        return self.goals[goal_id]

    async def add_subtask(self, goal_id: str, task: str):
        self.goals[goal_id]['subtasks'].append(task)

    async def complete_goal(self, goal_id: str):
        self.goals[goal_id]['status'] = 'completed'
