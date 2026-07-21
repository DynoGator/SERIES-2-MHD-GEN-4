import os
import re

for root, _, files in os.walk('tests'):
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r') as file:
                content = file.read()
            
            if '({})' in content:
                new_content = content.replace('({})', '(SystemConfig())')
                if 'SystemConfig' not in new_content[:500]:
                    new_content = 'from config.system_config import SystemConfig\n' + new_content
                
                with open(path, 'w') as file:
                    file.write(new_content)
