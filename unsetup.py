#!/usr/bin/env python3
import os
import sys
import shutil
from pathlib import Path


def uninstall_taiga():
    print("=" * 50)
    print("Удаление Taiga")
    print("=" * 50)

    home = Path.home()
    removed = []

    script_path = home / ".local" / "bin" / "taiga"
    git_path = Path.home() / "Taiga-analyzer"
    if script_path.exists():
        try:
            script_path.unlink()
            removed.append(f"Скрипт: {script_path}")
            print(f" Удален скрипт: {script_path}")
        except Exception as e:
            print(f" Не удалось удалить скрипт: {e}")

    possible_paths = [
        home / ".local" / "lib" / f"python{sys.version_info.major}.{sys.version_info.minor}" / "site-packages" / "taiga",
        home / ".local" / "lib" / "python3" / "site-packages" / "taiga",
    ]

    try:
        import site
        user_site = site.getusersitepackages()
        if user_site:
            possible_paths.insert(0, Path(user_site) / "taiga")
    except:
        pass

    for taiga_dir in possible_paths:
        if taiga_dir.exists() and taiga_dir.is_dir():
            try:
                shutil.rmtree(taiga_dir)
                removed.append(f"Пакет: {taiga_dir}")
                print(f"️ Удален пакет: {taiga_dir}")
            except Exception as e:
                print(f"️ Не удалось удалить пакет {taiga_dir}: {e}")

    if os.geteuid() == 0:
        system_paths = [
            Path("/usr/local/bin/taiga"),
            Path("/usr/bin/taiga"),
            Path("/usr/local/lib/python3.12/site-packages/taiga"),
            Path("/usr/lib/python3.12/site-packages/taiga"),
        ]

        for path in system_paths:
            if path.exists():
                try:
                    if path.is_file():
                        path.unlink()
                    else:
                        shutil.rmtree(path)
                    removed.append(f"Системный: {path}")
                    print(f"🗑️ Удален системный: {path}")
                except Exception as e:
                    print(f"️ Не удалось удалить системный {path}: {e}")

    if removed:
        try:
            os.system("hash -r 2>/dev/null")
            os.system("rehash 2>/dev/null")
        except:
            pass

    print("\n" + "=" * 50)
    if removed:
        print(f" Удалено {len(removed)} элементов")

        print("\n🔍 Проверка удаления:")
        try:
            result = os.system("which taiga 2>/dev/null")
            if result == 0:
                print("⚠️ Команда 'taiga' все еще может быть доступна")
                print("   Перезапустите терминал")
            else:
                print("✅ Команда 'taiga' не найдена")
        except:
            pass
    else:
        print("️ Taiga не найден в домашней директории")

    shutil.rmtree(git_path)



def main():
    print("Удалить Taiga из домашней директории? [y/N]: ", end='')
    response = input().strip().lower()

    if response in ['y', 'yes', 'д', 'да', 'Y', 'Д']:
        uninstall_taiga()
    else:
        print("Удаление отменено")


if __name__ == "__main__":
    if os.geteuid() == 0:
        print(" Не запускайте удаление с sudo!")
        print("   Taiga установлен в домашней директории пользователя")
        print("   Запустите без sudo: python unsetup.py")
        sys.exit(1)

    main()
