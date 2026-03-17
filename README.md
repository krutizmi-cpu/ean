# Генератор этикеток (боевой MVP)

Сервис на Streamlit для генерации этикеток с EAN-13.

## Возможности

- Пакетная загрузка Excel по шаблону.
- Ручное добавление товара.
- Проверка и генерация EAN-13 (при пустом EAN13).
- Форматы этикеток: 56x40 мм и A6.
- Итоговый Excel, CSV и PDF.
- ZIP-архив с полным комплектом.
- Журнал ошибок импорта (CSV).

## Установка и запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows

pip install -r requirements.txt
streamlit run app.py
```

## Формат входного Excel

Обязательные колонки:

- Артикул
- Наименование
- EAN13
- Количество

Если `EAN13` пустой, система генерирует внутренний EAN-13 с префиксом `20`.

## ZIP-архив результата

Архив содержит:

- result.xlsx
- result.csv
- labels_56x40.pdf
- labels_A6.pdf
- README_RESULT.txt

Также можно скачать отдельный CSV с ошибками импорта.

## Деплой на Streamlit Community Cloud

1. Форкните репозиторий.
2. Перейдите на share.streamlit.io.
3. Укажите `app.py` как точку входа.
4. Нажмите Deploy.
