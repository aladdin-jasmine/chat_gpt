class AIGuardrails:
    def detect_prompt_injection(self, prompt: str):
        suspicious = ['ignore previous', 'bypass', 'override system']
        return any(word in prompt.lower() for word in suspicious)

    def filter_output(self, output: str):
        blocked = ['malicious_payload']
        for item in blocked:
            output = output.replace(item, '[FILTERED]')
        return output

    def rate_limit(self, user_id: str):
        return {
            'user': user_id,
            'status': 'allowed'
        }
