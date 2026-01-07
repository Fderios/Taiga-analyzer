import ast
from .base_detector import BaseDetector


class DangerousCallsDetector(BaseDetector):

    DANGEROUS_FUNCTIONS = {
        'eval', 'exec', 'execfile', 'compile',
        'os.system', 'os.popen', 'os.popen2', 'os.popen3', 'os.popen4',
        'subprocess.Popen', 'subprocess.call', 'subprocess.run',
        'pickle.loads', 'marshal.loads', 'yaml.load',
        '__import__'
    }

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.Call):
            self._check_call(node)

    def _check_call(self, node: ast.Call) -> None:

        func_name = self._get_func_name(node.func)

        if func_name in self.DANGEROUS_FUNCTIONS:
            severity = 'HIGH' if func_name in {'eval', 'exec', '__import__'} else 'MEDIUM'
            self.add_finding(
                node=node,
                severity=severity,
                description=f'Вызов опасной функции: {func_name}',
                pattern=func_name
            )

    def _get_func_name(self, node: ast.AST) -> str:

        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            parts = []
            current = node
            while isinstance(current, ast.Attribute):
                parts.append(current.attr)
                current = current.value
            if isinstance(current, ast.Name):
                parts.append(current.id)
            return '.'.join(reversed(parts))
        return ''