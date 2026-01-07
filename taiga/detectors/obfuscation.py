import ast
import base64
import re
from math import log2
from .base_detector import BaseDetector


class ObfuscationDetector(BaseDetector):

    def __init__(self):
        super().__init__()
        self.string_nodes = []

    def visit(self, node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            self.string_nodes.append(node)

        if isinstance(node, ast.Call):
            self._check_base64_call(node)

        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            self._check_string_concat(node)

    def finalize(self) -> None:
        for node in self.string_nodes:
            self._check_string_entropy(node)

    def _check_base64_call(self, node: ast.Call) -> None:
        func_name = self._get_func_name(node.func)

        if 'base64' in func_name or 'b64decode' in func_name:
            parent = getattr(node, 'parent', None)
            if parent and isinstance(parent, ast.Call):
                parent_func = self._get_func_name(parent.func)
                if parent_func in {'eval', 'exec'}:
                    self.add_finding(
                        node=node,
                        severity='HIGH',
                        description='Использование base64 с eval/exec - явная обфускация',
                        pattern=f'{func_name} -> {parent_func}'
                    )

    def _check_string_concat(self, node: ast.BinOp) -> None:
        pass

    def _check_string_entropy(self, node: ast.Constant) -> None:
        s = node.value
        if len(s) < 20:
            return

        freq = {}
        for char in s:
            freq[char] = freq.get(char, 0) + 1

        entropy = 0
        for count in freq.values():
            p = count / len(s)
            entropy -= p * log2(p)

        max_entropy = log2(256) if len(s) > 50 else log2(94)
        entropy_ratio = entropy / max_entropy

        if entropy_ratio > 0.85 and len(s) > 30:
            self.add_finding(
                node=node,
                severity='MEDIUM',
                description=f'Высокая энтропия строки ({entropy_ratio:.2f}) - возможна обфускация',
                pattern=f'Энтропия: {entropy:.2f}'
            )

    def _get_func_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return node.attr
        return ''