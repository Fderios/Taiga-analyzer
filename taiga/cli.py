import argparse
import json
import sys
from pathlib import Path
from typing import List

from colorama import init, Fore, Back, Style
from .core import TaigaAnalyzer

init(autoreset=True)

TAIGA_ASCII_ART = r"""
████████╗ █████╗ ██╗ ██████╗  █████╗ 
╚══██╔══╝██╔══██╗██║██╔════╝ ██╔══██╗
   ██║   ███████║██║██║  ███╗███████║
   ██║   ██╔══██║██║██║   ██║██╔══██║
   ██║   ██║  ██║██║╚██████╔╝██║  ██║
   ╚═╝   ╚═╝  ╚═╝╚═╝ ╚═════╝ ╚═╝  ╚═╝

    ╔══════════════════════════════╗
    ║    Статический анализатор    ║
    ║       Python-кода v0.1.0     ║
    ╚══════════════════════════════╝
"""


def print_colored(text: str, color: str = '', bg_color: str = '',
                  style: str = '', end: str = '\n') -> None:
    output = ''

    if style == 'bright':
        output += Style.BRIGHT
    elif style == 'dim':
        output += Style.DIM

    if color:
        output += getattr(Fore, color.upper(), '')

    if bg_color:
        output += getattr(Back, bg_color.upper(), '')

    output += text + Style.RESET_ALL
    print(output, end=end)


def print_taiga_header():
    lines = TAIGA_ASCII_ART.strip().split('\n')

    for line in lines[:3]:
        print_colored(line, 'green', style='bright')

    for line in lines[3:]:
        print_colored(line, 'blue', style='dim')

    print()


def print_report(result: dict, verbose: bool = False) -> None:

    filename = result['filename']
    findings = result['findings']
    risk_score = result['risk_score']

    print_colored(f"\n{'=' * 70}", 'blue', style='bright')
    print_colored(f" Анализ файла: {filename}", 'blue', style='bright')
    print_colored(f"{'=' * 70}", 'blue', style='bright')

    if result.get('status') == 'error':
        print_colored(f" Ошибка синтаксиса: {result.get('error', 'неизвестно')}", 'red', style='bright')
        return

    if risk_score == 0:
        risk_color = 'green'
        risk_icon = '✅'
        risk_text = "НИЗКИЙ"
        risk_emoji = "🟢"
    elif risk_score < 5:
        risk_color = 'yellow'
        risk_icon = '⚠️'
        risk_text = "СРЕДНИЙ"
        risk_emoji = "🟡"
    else:
        risk_color = 'red'
        risk_icon = '🚨'
        risk_text = "ВЫСОКИЙ"
        risk_emoji = "🔴"

    print_colored(f"\n{risk_emoji} Общая оценка риска", risk_color, style='bright')
    print_colored(f"   Балл: {risk_score}/10", risk_color)
    print_colored(f"   Уровень: {risk_text} {risk_icon}", risk_color)

    print_colored(f"\n Статистика", 'blue', style='bright')
    print_colored(f"   Найдено паттернов: {len(findings)}", 'blue')

    severity_counts = {}
    for finding in findings:
        sev = finding['severity']
        severity_counts[sev] = severity_counts.get(sev, 0) + 1

    if severity_counts:
        print_colored("   Распределение:", 'blue')
        for severity, count in severity_counts.items():
            if severity == 'HIGH':
                color = 'red'
                icon = '🔴'
            elif severity == 'MEDIUM':
                color = 'yellow'
                icon = '🟡'
            elif severity == 'LOW':
                color = 'green'
                icon = '🟢'
            else:
                color = 'white'
                icon = '⚪'

            print_colored(f"     {icon} {severity}: {count}", color)

    if findings:
        print_colored(f"\n Обнаруженные паттерны:", 'blue', style='bright')

        for i, finding in enumerate(findings, 1):
            severity = finding['severity']
            line = finding['line']

            if severity == 'HIGH':
                severity_color = 'red'
                severity_icon = '🚨'
                box_color = Back.RED + Fore.WHITE + Style.BRIGHT
            elif severity == 'MEDIUM':
                severity_color = 'yellow'
                severity_icon = '⚠️'
                box_color = Back.YELLOW + Fore.BLACK + Style.BRIGHT
            else:
                severity_color = 'green'
                severity_icon = 'ℹ️'
                box_color = Back.GREEN + Fore.BLACK + Style.BRIGHT

            print_colored(f"\n{i:>3}. ", end='')
            print(box_color + f" {severity} " + Style.RESET_ALL + " ", end='')
            print_colored(f"{severity_icon} {finding['description']}", severity_color)

            location_info = f"    Строка {line}"
            if finding.get('col'):
                location_info += f", столбец {finding['col']}"
            print_colored(location_info, 'white', style='dim')

            if finding.get('detector'):
                print_colored(f"    Детектор: {finding['detector']}", 'cyan', style='dim')

            if verbose and finding.get('pattern'):
                print_colored(f"    Паттерн: {finding['pattern']}", 'white', style='dim')

    else:
        print_colored(f"\n Отличные новости!", 'green', style='bright')
        print_colored("    Вредоносных паттернов не обнаружено", 'green')
        print_colored("    Файл выглядит безопасно", 'green')

    print_colored(f"\n{'=' * 70}", 'blue', style='bright')


def main():
    print_taiga_header()

    parser = argparse.ArgumentParser(
        description='Тайга - статический анализатор Python-кода на вредоносные паттерны',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  taiga suspicious.py          # Анализ одного файла
  taiga script.py -v           # Подробный вывод
  taiga . -o report.json       # Анализ всех .py файлов в директории
  taiga file.py --no-color     # Без цветного вывода

Доступные цвета: BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE
        """
    )

    parser.add_argument(
        'target',
        help='Путь к файлу .py или директории для анализа'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Подробный вывод с дополнительной информацией'
    )

    parser.add_argument(
        '-o', '--output',
        help='Сохранить отчет в JSON файл'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Отключить цветной вывод'
    )

    parser.add_argument(
        '--min-severity',
        choices=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'],
        default='LOW',
        help='Минимальный уровень серьезности для отображения (по умолчанию: LOW)'
    )

    parser.add_argument(
        '--format',
        choices=['text', 'json', 'compact'],
        default='text',
        help='Формат вывода (по умолчанию: text)'
    )

    args = parser.parse_args()

    if args.no_color:
        global Fore, Back, Style
        Fore = type('Fore', (), {k: '' for k in dir(Fore) if not k.startswith('_')})()
        Back = type('Back', (), {k: '' for k in dir(Back) if not k.startswith('_')})()
        Style = type('Style', (), {k: '' for k in dir(Style) if not k.startswith('_')})()

    analyzer = TaigaAnalyzer()
    target_path = Path(args.target)

    all_results = []

    if target_path.is_file() and target_path.suffix == '.py':
        files_to_analyze = [target_path]
    elif target_path.is_dir():
        files_to_analyze = list(target_path.rglob('*.py'))
        if not files_to_analyze:
            print_colored(" Не найдено .py файлов для анализа", 'red')
            return 1
        print_colored(f" Найдено {len(files_to_analyze)} Python файлов для анализа...", 'blue')
    else:
        print_colored(f" Ошибка: {args.target} не является .py файлом или директорией", 'red')
        return 1

    severity_order = {'LOW': 1, 'MEDIUM': 2, 'HIGH': 3, 'CRITICAL': 4}
    min_severity_level = severity_order.get(args.min_severity, 1)

    for i, file_path in enumerate(files_to_analyze, 1):
        if len(files_to_analyze) > 1:
            print_colored(f"\n[{i}/{len(files_to_analyze)}] Анализ: {file_path}", 'cyan', style='bright')

        result = analyzer.analyze_file(str(file_path))

        if args.min_severity != 'LOW':
            filtered_findings = [
                f for f in result.get('findings', [])
                if severity_order.get(f.get('severity', 'LOW'), 1) >= min_severity_level
            ]
            result['findings'] = filtered_findings

        all_results.append(result)

        if args.format == 'compact' and len(files_to_analyze) > 1:
            icon = "✅" if not result['findings'] else "⚠️" if result['risk_score'] < 5 else "🚨"
            print_colored(
                f"   {icon} {file_path.name}: {len(result['findings'])} паттернов, риск: {result['risk_score']}/10",
                'green' if not result['findings'] else 'yellow' if result['risk_score'] < 5 else 'red')
        elif args.format == 'text':
            if len(files_to_analyze) == 1 or (len(files_to_analyze) > 1 and result['findings']):
                print_report(result, args.verbose)

    if len(files_to_analyze) > 1 and args.format != 'compact':
        print_colored(f"\n{'=' * 70}", 'magenta', style='bright')
        print_colored(" СВОДКА ПО ВСЕМ ФАЙЛАМ", 'magenta', style='bright')
        print_colored(f"{'=' * 70}", 'magenta', style='bright')

        total_findings = sum(len(r['findings']) for r in all_results)
        total_risk = sum(r['risk_score'] for r in all_results)
        avg_risk = total_risk / len(all_results) if all_results else 0

        files_with_findings = sum(1 for r in all_results if r['findings'])

        print_colored(f" Проанализировано файлов: {len(all_results)}", 'cyan')
        print_colored(f" Всего паттернов: {total_findings}", 'cyan')
        print_colored(f" Файлов с находками: {files_with_findings}", 'cyan')
        print_colored(f" Средний балл риска: {avg_risk:.1f}/10", 'cyan')

        if files_with_findings > 0:
            print_colored(f"\n Файлы с наибольшим риском:", 'red', style='bright')
            risky_files = sorted(all_results, key=lambda x: x['risk_score'], reverse=True)[:3]
            for r in risky_files:
                if r['risk_score'] > 0:
                    risk_color = 'red' if r['risk_score'] >= 5 else 'yellow'
                    print_colored(
                        f"   • {Path(r['filename']).name}: {r['risk_score']}/10 ({len(r['findings'])} паттернов)",
                        risk_color)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print_colored(f"\nОтчет сохранен в {args.output}", 'green', style='bright')

    exit_code = 0
    for result in all_results:
        for finding in result.get('findings', []):
            if finding['severity'] in ['HIGH', 'CRITICAL']:
                exit_code = 1
                break
        if exit_code == 1:
            break

    if exit_code == 0:
        print_colored("Анализ завершен успешно!", 'green', style='bright')
        print_colored("Все файлы прошли проверку безопасности", 'green')
    else:
        print_colored("Обнаружены критические угрозы!", 'red', style='bright')
        print_colored("Рекомендуется провести дополнительный анализ", 'red')

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
