#!/usr/bin/env python3
import os
import sys
import shutil
import subprocess
from pathlib import Path


def get_user_site_packages():
    import site
    site_packages = site.getusersitepackages()

    if site_packages:
        return Path(site_packages)

    home = Path.home()
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    user_site_packages = home / '.local' / 'lib' / f'python{python_version}' / 'site-packages'

    user_site_packages.mkdir(parents=True, exist_ok=True)
    return user_site_packages


def install_taiga():
    print("=" * 50)
    print("Установка Taiga - статического анализатора Python кода")
    print("=" * 50)

    project_dir = Path(__file__).parent
    source_dir = project_dir / "taiga"

    if not source_dir.exists():
        print(f"❌ Ошибка: Не найден исходный код в {source_dir}")
        return False

    target_dir = get_user_site_packages() / "taiga"

    print(f"Устанавливаем в: {target_dir}")

    target_dir.mkdir(parents=True, exist_ok=True)

    files_copied = 0
    for py_file in source_dir.rglob("*.py"):
        rel_path = py_file.relative_to(source_dir)
        target_file = target_dir / rel_path

        target_file.parent.mkdir(parents=True, exist_ok=True)

        shutil.copy2(py_file, target_file)
        files_copied += 1
        print(f"   {rel_path}")

    print(f"✅ Скопировано файлов: {files_copied}")

    create_entry_point(target_dir)

    install_dependencies()

    return True


def create_entry_point(taiga_dir):

    home = Path.home()
    bin_dir = home / '.local' / 'bin'

    bin_dir.mkdir(parents=True, exist_ok=True)

    script_content = f'''#!/usr/bin/env python3
import sys
import os

import site
user_site = site.getusersitepackages()
if user_site and os.path.exists(user_site):
    sys.path.insert(0, user_site)

from taiga.cli import main

if __name__ == "__main__":
    sys.exit(main())
'''

    script_path = bin_dir / "taiga"

    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    script_path.chmod(0o755)

    print(f"   Создан исполняемый файл: {script_path}")

    current_path = os.environ.get("PATH", "")
    if str(bin_dir) not in current_path:
        print(f"     Добавьте в PATH: {bin_dir}")
        print(f"     Выполните: export PATH=\"$HOME/.local/bin:$PATH\"")
        print(f"     Или добавьте в ~/.bashrc")


def install_dependencies():
    print("\nУстанавливаем зависимости...")

    try:
        import colorama
        print("  ✅ colorama уже установлен")
    except ImportError:
        print("Устанавливаем colorama...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "colorama"])
            print("  ✅ colorama установлен")
        except Exception as e:
            print(f"    Не удалось установить: {e}")
            print("    Установите вручную: pip install --user colorama")


def main():
    print("Установить Taiga в домашнюю директорию? [Y/n]: ", end='')
    response = input().strip().lower()

    if response in ['', 'y', 'yes', 'д', 'да']:
        if install_taiga():
            print("\n" + "=" * 50)
            print("✅ Установка завершена успешно!")
            print("\n Использование:")
            print("  taiga suspicious.py          # Анализ файла")
            print("  taiga . -v                   # Анализ директории")
            print("\n Если команда 'taiga' не работает:")
            print("  1. Обновите PATH: export PATH=\"$HOME/.local/bin:$PATH\"")
            print("  2. Или перезапустите терминал")
            print("=" * 50)
            return 0
        else:
            print("\n❌ Установка не удалась")
            return 1
    else:
        print("Установка отменена")
        return 0


if __name__ == "__main__":
    sys.exit(main())