# Тайга

Статический анализатор Python-скриптов на предмет вредоносных паттернов и обфускации.

Подобно тому, как глубока тайга, глубок анализ Python-кода через Taiga.
## Установка

```bash
git clone https://github.com/Fderios/Taiga-analyzer.git
cd Taiga-analyzer
python setup.py
```

## Использование
```bash
taiga example.py      # Анализ файла"
taiga . -v               # Анализ директории"
```

## Примеры
Пример кода с обфускациями и паттернами находится по пути **taiga_analyzer/tests/test_malicious.py**

## Удаление
```bash
cd ~/Taiga-analyzer
python unsetup.py
```

