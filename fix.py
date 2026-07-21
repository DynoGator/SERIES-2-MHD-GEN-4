import os, re

def fix():
    for root, _, files in os.walk('physics'):
        for f in files:
            if f.endswith('.py'):
                path = os.path.join(root, f)
                with open(path, 'r') as file:
                    content = file.read()
                new_content = re.sub(r"getattr\(([^,]+),\s*['\"](\w+)['\"],\s*([0-9.eE-]+)\)", r"\1.\2", content)
                if new_content != content:
                    print(f'Updating {path}')
                    with open(path, 'w') as file:
                        file.write(new_content)
fix()
