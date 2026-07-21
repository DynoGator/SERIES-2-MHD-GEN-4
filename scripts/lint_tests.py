#!/usr/bin/env python3
import os
import ast
import sys

def check_pytest_raises_exception(node, path):
    if isinstance(node, ast.Call):
        func = node.func
        is_pytest_raises = False
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
            if func.value.id == 'pytest' and func.attr == 'raises':
                is_pytest_raises = True
        elif isinstance(func, ast.Name) and func.id == 'raises':
            is_pytest_raises = True
        
        if is_pytest_raises and node.args:
            arg0 = node.args[0]
            if isinstance(arg0, ast.Name) and arg0.id == 'Exception':
                print(f"LINT FAIL: {path}:{node.lineno} calls pytest.raises(Exception)")
                return True
            if isinstance(arg0, ast.Tuple):
                for elt in arg0.elts:
                    if isinstance(elt, ast.Name) and elt.id == 'Exception':
                        print(f"LINT FAIL: {path}:{node.lineno} calls pytest.raises with a tuple containing Exception")
                        return True
    return False

def check_getattr_numeric_default(node, path):
    if "physics" in path or "validation" in path:
        if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'getattr':
            if len(node.args) == 3:
                # Check for ast.Constant and ast.Num
                arg2 = node.args[2]
                if isinstance(arg2, ast.Constant) and isinstance(arg2.value, (int, float)):
                    print(f"LINT FAIL: {path}:{node.lineno} uses getattr with numeric literal default")
                    return True
                elif type(arg2).__name__ == 'Num':
                    print(f"LINT FAIL: {path}:{node.lineno} uses getattr with numeric literal default")
                    return True
    return False

def check_max_clamp_state_vector(node, path):
    if "core/state_vector.py" in path:
        if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'max':
            print(f"LINT FAIL: {path}:{node.lineno} uses max() clamp pattern")
            return True
    return False

def check_gate_result_boolean(node, path):
    if isinstance(node, ast.Call) and getattr(node.func, 'id', '') == 'GateResult':
        if len(node.args) > 1:
            verdict_arg = node.args[1]
            if isinstance(verdict_arg, ast.Constant) and isinstance(verdict_arg.value, bool):
                print(f"LINT FAIL: {path}:{node.lineno} GateResult with boolean verdict")
                return True
            elif type(verdict_arg).__name__ == 'NameConstant' and isinstance(verdict_arg.value, bool):
                print(f"LINT FAIL: {path}:{node.lineno} GateResult with boolean verdict")
                return True
    return False

def check_scavenger_status(content, path):
    if "scavengers" in path:
        if "EARNED" in content or "KILLED" in content:
            if "MODULE-STATUS: PLACEHOLDER" in content:
                print(f"LINT FAIL: {path} has EARNED/KILLED status paired with PLACEHOLDER")
                return True
    return False

def lint_all():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    failed = False
    
    for root, _, files in os.walk(root_dir):
        if "venv" in root or ".git" in root: continue
        for file in files:
            if not file.endswith('.py'):
                continue
            path = os.path.join(root, file)
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if "lint_tests.py" in path:
                continue
            if check_scavenger_status(content, path):
                failed = True
            
            try:
                tree = ast.parse(content, filename=path)
            except SyntaxError:
                continue

            for node in ast.walk(tree):
                if check_pytest_raises_exception(node, path): failed = True
                if check_getattr_numeric_default(node, path): failed = True
                if check_max_clamp_state_vector(node, path): failed = True
                if check_gate_result_boolean(node, path): failed = True

    if failed:
        sys.exit(1)
    else:
        print("LINT PASS")
        sys.exit(0)

if __name__ == '__main__':
    lint_all()
