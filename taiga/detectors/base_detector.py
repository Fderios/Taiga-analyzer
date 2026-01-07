from abc import ABC, abstractmethod
from typing import List, Dict, Any
import ast


class BaseDetector(ABC):

    def __init__(self):
        self.name = self.__class__.__name__
        self.findings = []

    @abstractmethod
    def visit(self, node: ast.AST) -> None:
        pass

    def report(self) -> List[Dict[str, Any]]:
        return self.findings

    def add_finding(self,
                    node: ast.AST,
                    severity: str,
                    description: str,
                    pattern: str = None) -> None:

        finding = {
            'detector': self.name,
            'severity': severity,
            'description': description,
            'line': getattr(node, 'lineno', 0),
            'col': getattr(node, 'col_offset', 0),
            'pattern': pattern or str(node)
        }
        self.findings.append(finding)