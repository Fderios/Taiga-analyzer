import ast
import tokenize
from io import StringIO
from typing import List, Dict, Any
from pathlib import Path

from .detectors.dangerous_calls import DangerousCallsDetector
from .detectors.obfuscation import ObfuscationDetector


class ASTVisitor(ast.NodeVisitor):
    def __init__(self, detectors: list):
        self.detectors = detectors

    def visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            child.parent = node

        for detector in self.detectors:
            detector.visit(node)

        self.generic_visit(node)


class TaigaAnalyzer:
    def __init__(self):
        self.detectors = [
            DangerousCallsDetector(),
            ObfuscationDetector()
        ]
        self.results = []

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
        except UnicodeDecodeError:
            return {'error': f'Не удалось декодировать файл: {file_path}'}

        return self.analyze_source(source_code, str(file_path))

    def analyze_source(self, source_code: str, filename: str = '<string>') -> Dict[str, Any]:

        try:
            tree = ast.parse(source_code, filename=filename)

            visitor = ASTVisitor(self.detectors)
            visitor.visit(tree)

            for detector in self.detectors:
                if hasattr(detector, 'finalize'):
                    detector.finalize()

            findings = []
            for detector in self.detectors:
                findings.extend(detector.report())

            findings.sort(key=lambda x: x['line'])

            risk_score = self._calculate_risk_score(findings)

            return {
                'filename': filename,
                'findings': findings,
                'risk_score': risk_score,
                'status': 'success'
            }

        except SyntaxError as e:
            return self._fallback_token_analysis(source_code, filename, str(e))

    def _calculate_risk_score(self, findings: List[Dict]) -> float:

        severity_weights = {
            'LOW': 1,
            'MEDIUM': 3,
            'HIGH': 7,
            'CRITICAL': 10
        }

        if not findings:
            return 0.0

        total_score = sum(severity_weights.get(f['severity'], 1) for f in findings)
        normalized_score = min(10.0, total_score / 5.0)  # Нормализуем до 10

        return round(normalized_score, 2)

    def _fallback_token_analysis(self, source_code: str, filename: str, error_msg: str) -> Dict[str, Any]:

        findings = []

        try:
            tokens = list(tokenize.generate_tokens(StringIO(source_code).readline))

            for tok in tokens:
                if tok.type == tokenize.NAME and tok.string in ['eval', 'exec', '__import__']:
                    findings.append({
                        'detector': 'TokenAnalyzer',
                        'severity': 'HIGH',
                        'description': f'Найден опасный идентификатор: {tok.string} (синтаксическая ошибка в файле)',
                        'line': tok.start[0],
                        'col': tok.start[1],
                        'pattern': tok.string
                    })
        except:
            pass

        return {
            'filename': filename,
            'findings': findings,
            'risk_score': self._calculate_risk_score(findings),
            'status': 'error',
            'error': error_msg
        }