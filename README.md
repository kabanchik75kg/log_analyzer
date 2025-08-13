# Log Analyzer

## Описание
Консольная утилита для анализа логов веб-сервера. Генерирует отчеты на основе JSON-логов, поддерживает фильтрацию по дате и расширяемую систему отчетов.

## Установка
pip install -r requirements.txt

## Использование (для Linux):
  ```python
  python3 main.py --file <лог-файлы(один или несколько)> --report <тип_отчета> [--date <дата в формате '%Y-%m-%d'>]
  ```

 ## Примеры:
  1. **Анализ одного лог-файла.**
  <img width="1092" height="155" alt="image" src="https://github.com/user-attachments/assets/50ceaa7d-ae01-4ce4-a228-a1f52ea4bf93" />
  
  2. **Анализ нескольких лог-файлов.**
  <img width="1040" height="144" alt="image" src="https://github.com/user-attachments/assets/8aff906d-414e-4d83-934e-a73674115eed" />
  
  3. **Анализ двух лог-файла с указанной датой.**
  <img width="1180" height="145" alt="image" src="https://github.com/user-attachments/assets/ffa07627-8024-4f04-8b57-bffa42032eee" />

## Тесты:
  <img width="1262" height="861" alt="image" src="https://github.com/user-attachments/assets/51c2ac6c-e5d9-49a2-b448-80b193a967cf" />
