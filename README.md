# 📊 File Sharing Platform

Простая платформа для обмена файлами в классе. Поддерживает презентации (PPTX), документы (PDF, DOCX) и изображения.

## 🚀 Запуск

### Установка зависимостей

```bash
pip install flask werkzeug Pillow
# Опционально для превью PDF:
pip install pdf2image pypdf
```

Для работы PDF превью также нужен **poppler**:
- Ubuntu/Debian: `sudo apt-get install poppler-utils`
- macOS: `brew install poppler`
- Windows: скачать с https://github.com/osber/poppler-windows

### Запуск сервера

```bash
python main.py
```

Сервер запустится на http://localhost:5000

## 📁 Структура проекта

```
project/
├── main.py              # Основной код приложения
├── data.json            # "База данных" (создаётся автоматически)
├── pyproject.toml       # Зависимости
├── templates/
│   ├── index.html       # Главная страница
│   ├── room.html        # Страница комнаты с портфолио
│   └── admin.html       # Админ-панель
├── static/
│   ├── style.css        # Стили
│   └── previews/        # Превью файлов (создаётся автоматически)
└── uploads/             # Загруженные файлы (создаётся автоматически)
```

## 🔐 Коды доступа

- **Админ**: `10122025Ad` — полный доступ ко всем комнатам
- **Учитель**: `10122025` — управление только текущей комнатой

## 🌐 Языки

Поддерживаются: 🇮🇩 Индонезийский, 🇷🇺 Русский, 🇬🇧 Английский, 🇪🇸 Испанский

## 📝 Поддерживаемые форматы

- **Презентации**: PPTX
- **Документы**: PDF, DOCX
- **Изображения**: PNG, JPG, JPEG, GIF, BMP, WEBP
