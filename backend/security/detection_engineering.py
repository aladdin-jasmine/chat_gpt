class DetectionEngineering:
    async def generate_sigma(self, attack_type: str):
        return f'''
title: Suspicious {attack_type}
logsource:
  product: windows
  category: process_creation
detection:
  selection:
    CommandLine|contains: '{attack_type}'
  condition: selection
level: high
'''

    async def generate_yara(self, malware_family: str):
        return f'''
rule {malware_family}
{{
    strings:
        $a = "powershell"
        $b = "cmd.exe"
    condition:
        any of them
}}
'''
