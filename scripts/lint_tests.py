#!/usr/bin/env python3
import os
import re
import sys

def lint_tests():
    tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tests'))
    failed = False
    
    # Regex to catch pytest.raises(Exception) or pytest.raises((..., Exception, ...))
    # It catches "pytest.raises(Exception" and "pytest.raises((...Exception..."
    # A bit crude but effective for AST-free linting. Let's use AST for robustness.
    import ast

    for root, _, files in os.walk(tests_dir):
        for file in files:
            if not file.endswith('.py'):
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            try:
                tree = ast.parse(content, filename=path)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check if function is pytest.raises
                    func = node.func
                    is_pytest_raises = False
                    if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                        if func.value.id == 'pytest' and func.attr == 'raises':
                            is_pytest_raises = True
                    elif isinstance(func, ast.Name) and func.id == 'raises':
                        is_pytest_raises = True
                    
                    if is_pytest_raises and node.args:
                        arg0 = node.args[0]
                        
                        # Check for bare Exception
                        if isinstance(arg0, ast.Name) and arg0.id == 'Exception':
                            print(f"L-B LINT FAIL: {path}:{node.lineno} calls pytest.raises(Exception)")
                            failed = True
                        
                        # Check for tuple containing Exception
                        if isinstance(arg0, ast.Tuple):
                            for elt in arg0.elts:
                                if isinstance(elt, ast.Name) and elt.id == 'Exception':
                                    print(f"L-B LINT FAIL: {path}:{node.lineno} calls pytest.raises with a tuple containing Exception")
                                    failed = True
    
    if failed:
        sys.exit(1)
    else:
        print("L-B LINT PASS")
        sys.exit(0)

if __name__ == '__main__':
    lint_tests()
