from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
import os
import zipfile
import json
import uuid
import random
import shutil
from datetime import datetime
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'presentation-share-secret-key-2024'

# Конфигурация
UPLOAD_FOLDER = 'uploads'
# Расширенный список разрешённых форматов
ALLOWED_EXTENSIONS = {
    'pptx',           # Презентации
    'pdf',            # PDF документы
    'docx',           # Word документы
    'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'  # Изображения
}

# Категории файлов для отображения
FILE_CATEGORIES = {
    'presentation': {'pptx'},
    'document': {'pdf', 'docx'},
    'image': {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
}

ADMIN_CODE = '10122025Ad'  # Глобальный админ
TEACHER_CODE = '10122025'      # Учитель (только текущая комната)
DEFAULT_LANG = 'id'  # Индонезийский по умолчанию

# Переводы
TRANSLATIONS = {
    'id': {  # Индонезийский (по умолчанию)
        'site_title': 'Berbagi File',
        'site_subtitle': 'Unggah dan lihat karya teman sekelas',
        'create_room': 'Buat Ruangan',
        'create_room_desc': 'Untuk guru: buat ruangan untuk pelajaran',
        'lesson_name': 'Nama pelajaran',
        'create_room_btn': 'Buat Ruangan',
        'join_room': 'Masuk Ruangan',
        'join_room_desc': 'Masukkan kode 4 digit dari guru',
        'room_code': 'Kode ruangan',
        'join_btn': 'Masuk',
        'room_not_found': 'Ruangan tidak ditemukan',
        'admin_panel': 'Panel Admin',
        'upload_file': 'Unggah File',
        'your_name': 'Nama Anda',
        'choose_file': 'Pilih File',
        'file_not_selected': 'File belum dipilih',
        'upload_btn': 'Unggah',
        'class_works': 'Karya Kelas',
        'download': 'Unduh',
        'all_images': 'Semua Gambar',
        'delete': 'Hapus',
        'no_files': 'Belum ada file',
        'be_first': 'Jadilah yang pertama — unggah karya Anda!',
        'new_works': 'Ada karya baru!',
        'refresh': 'Perbarui',
        'teacher_mode': 'Mode Guru',
        'admin_mode': 'Admin',
        'panel': 'Panel',
        'exit': 'Keluar',
        'management_mode': 'Mode Pengelolaan',
        'enter_code': 'Masukkan kode untuk mengelola ruangan:',
        'wrong_code': 'Kode salah',
        'login': 'Masuk',
        'no_preview': 'Tidak ada gambar untuk pratinjau',
        'delete_confirm': 'Hapus file ini?',
        'rooms': 'Ruangan',
        'files': 'File',
        'open': 'Buka',
        'delete_room_confirm': 'Hapus ruangan dan semua file-nya?',
        'no_rooms': 'Tidak ada ruangan',
        'no_files_admin': 'Tidak ada file yang diunggah',
        'images': 'gambar',
        'pages': 'halaman',
        'back_to_main': '← Ke Halaman Utama',
        'logout_admin': 'Keluar dari Admin',
        'footer_text': 'Berbagi file sederhana untuk kelas',
        'language': 'Bahasa',
        'allowed_formats': 'Format yang didukung: PPTX, PDF, DOCX, gambar',
        'file_type_presentation': 'Presentasi',
        'file_type_document': 'Dokumen',
        'file_type_image': 'Gambar',
        'presentations': 'File',
    },
    'ru': {  # Русский
        'site_title': 'Обмен файлами',
        'site_subtitle': 'Загружайте и смотрите работы одноклассников',
        'create_room': 'Создать комнату',
        'create_room_desc': 'Для преподавателя: создайте комнату для урока',
        'lesson_name': 'Название урока',
        'create_room_btn': 'Создать комнату',
        'join_room': 'Войти в комнату',
        'join_room_desc': 'Введите 4-значный код от преподавателя',
        'room_code': 'Код комнаты',
        'join_btn': 'Войти',
        'room_not_found': 'Комната не найдена',
        'admin_panel': 'Админ-панель',
        'upload_file': 'Загрузить файл',
        'your_name': 'Твоё имя',
        'choose_file': 'Выбрать файл',
        'file_not_selected': 'Файл не выбран',
        'upload_btn': 'Загрузить',
        'class_works': 'Работы класса',
        'download': 'Скачать',
        'all_images': 'Все картинки',
        'delete': 'Удалить',
        'no_files': 'Пока нет файлов',
        'be_first': 'Будь первым — загрузи свою работу!',
        'new_works': 'Появились новые работы!',
        'refresh': 'Обновить',
        'teacher_mode': 'Режим учителя',
        'admin_mode': 'Админ',
        'panel': 'Панель',
        'exit': 'Выйти',
        'management_mode': 'Режим управления',
        'enter_code': 'Введите код для управления комнатой:',
        'wrong_code': 'Неверный код',
        'login': 'Войти',
        'no_preview': 'Нет картинок для предпросмотра',
        'delete_confirm': 'Удалить этот файл?',
        'rooms': 'Комнаты',
        'files': 'Файлы',
        'open': 'Открыть',
        'delete_room_confirm': 'Удалить комнату и все её файлы?',
        'no_rooms': 'Нет созданных комнат',
        'no_files_admin': 'Нет загруженных файлов',
        'images': 'картинок',
        'pages': 'страниц',
        'back_to_main': '← На главную',
        'logout_admin': 'Выйти из админки',
        'footer_text': 'Простой обмен файлами для класса',
        'language': 'Язык',
        'allowed_formats': 'Поддерживаемые форматы: PPTX, PDF, DOCX, изображения',
        'file_type_presentation': 'Презентация',
        'file_type_document': 'Документ',
        'file_type_image': 'Изображение',
        'presentations': 'Файлы',
    },
    'en': {  # Английский
        'site_title': 'File Sharing',
        'site_subtitle': 'Upload and view classmates\' works',
        'create_room': 'Create Room',
        'create_room_desc': 'For teachers: create a room for the lesson',
        'lesson_name': 'Lesson name',
        'create_room_btn': 'Create Room',
        'join_room': 'Join Room',
        'join_room_desc': 'Enter the 4-digit code from your teacher',
        'room_code': 'Room code',
        'join_btn': 'Join',
        'room_not_found': 'Room not found',
        'admin_panel': 'Admin Panel',
        'upload_file': 'Upload File',
        'your_name': 'Your name',
        'choose_file': 'Choose File',
        'file_not_selected': 'No file selected',
        'upload_btn': 'Upload',
        'class_works': 'Class Works',
        'download': 'Download',
        'all_images': 'All Images',
        'delete': 'Delete',
        'no_files': 'No files yet',
        'be_first': 'Be the first — upload your work!',
        'new_works': 'New works available!',
        'refresh': 'Refresh',
        'teacher_mode': 'Teacher Mode',
        'admin_mode': 'Admin',
        'panel': 'Panel',
        'exit': 'Exit',
        'management_mode': 'Management Mode',
        'enter_code': 'Enter code to manage the room:',
        'wrong_code': 'Wrong code',
        'login': 'Login',
        'no_preview': 'No images for preview',
        'delete_confirm': 'Delete this file?',
        'rooms': 'Rooms',
        'files': 'Files',
        'open': 'Open',
        'delete_room_confirm': 'Delete room and all its files?',
        'no_rooms': 'No rooms created',
        'no_files_admin': 'No files uploaded',
        'images': 'images',
        'pages': 'pages',
        'back_to_main': '← Back to Main',
        'logout_admin': 'Logout from Admin',
        'footer_text': 'Simple file sharing for classrooms',
        'language': 'Language',
        'allowed_formats': 'Supported formats: PPTX, PDF, DOCX, images',
        'file_type_presentation': 'Presentation',
        'file_type_document': 'Document',
        'file_type_image': 'Image',
        'presentations': 'Files',
    },
    'es': {  # Испанский
        'site_title': 'Compartir Archivos',
        'site_subtitle': 'Sube y mira los trabajos de tus compañeros',
        'create_room': 'Crear Sala',
        'create_room_desc': 'Para profesores: crea una sala para la clase',
        'lesson_name': 'Nombre de la clase',
        'create_room_btn': 'Crear Sala',
        'join_room': 'Entrar a la Sala',
        'join_room_desc': 'Ingresa el código de 4 dígitos del profesor',
        'room_code': 'Código de sala',
        'join_btn': 'Entrar',
        'room_not_found': 'Sala no encontrada',
        'admin_panel': 'Panel de Admin',
        'upload_file': 'Subir Archivo',
        'your_name': 'Tu nombre',
        'choose_file': 'Elegir Archivo',
        'file_not_selected': 'Archivo no seleccionado',
        'upload_btn': 'Subir',
        'class_works': 'Trabajos de la Clase',
        'download': 'Descargar',
        'all_images': 'Todas las Imágenes',
        'delete': 'Eliminar',
        'no_files': 'Aún no hay archivos',
        'be_first': '¡Sé el primero — sube tu trabajo!',
        'new_works': '¡Hay nuevos trabajos!',
        'refresh': 'Actualizar',
        'teacher_mode': 'Modo Profesor',
        'admin_mode': 'Admin',
        'panel': 'Panel',
        'exit': 'Salir',
        'management_mode': 'Modo de Gestión',
        'enter_code': 'Ingresa el código para gestionar la sala:',
        'wrong_code': 'Código incorrecto',
        'login': 'Entrar',
        'no_preview': 'Sin imágenes para vista previa',
        'delete_confirm': '¿Eliminar este archivo?',
        'rooms': 'Salas',
        'files': 'Archivos',
        'open': 'Abrir',
        'delete_room_confirm': '¿Eliminar sala y todos sus archivos?',
        'no_rooms': 'No hay salas creadas',
        'no_files_admin': 'No hay archivos subidos',
        'images': 'imágenes',
        'pages': 'páginas',
        'back_to_main': '← Volver al Inicio',
        'logout_admin': 'Salir del Admin',
        'footer_text': 'Compartir archivos simple para el aula',
        'language': 'Idioma',
        'allowed_formats': 'Formatos soportados: PPTX, PDF, DOCX, imágenes',
        'file_type_presentation': 'Presentación',
        'file_type_document': 'Documento',
        'file_type_image': 'Imagen',
        'presentations': 'Archivos',
    }
}

def get_lang():
    """Получить текущий язык из сессии"""
    return session.get('lang', DEFAULT_LANG)

def get_translations():
    """Получить переводы для текущего языка"""
    return TRANSLATIONS.get(get_lang(), TRANSLATIONS[DEFAULT_LANG])

# Создаём папки если их нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('static/previews', exist_ok=True)

# "База данных" в JSON файле
DATA_FILE = 'data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'rooms': {}, 'presentations': {}}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Получить расширение файла"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''

def get_file_type(filename):
    """Определить тип файла по расширению"""
    ext = get_file_extension(filename)
    for file_type, extensions in FILE_CATEGORIES.items():
        if ext in extensions:
            return file_type
    return 'unknown'

def generate_room_code():
    """Генерирует 4-значный код комнаты"""
    return str(random.randint(1000, 9999))

def extract_images_from_pptx(pptx_path, file_id):
    """Извлекает картинки из PPTX файла"""
    images = []
    preview_dir = f'static/previews/{file_id}'
    os.makedirs(preview_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(pptx_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.startswith('ppt/media/') and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_data = zip_ref.read(file_name)
                    image_name = os.path.basename(file_name)
                    image_path = os.path.join(preview_dir, image_name)

                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

                    images.append(f'previews/{file_id}/{image_name}')
    except Exception as e:
        print(f"Ошибка извлечения картинок из PPTX: {e}")

    return images

def extract_images_from_docx(docx_path, file_id):
    """Извлекает картинки из DOCX файла"""
    images = []
    preview_dir = f'static/previews/{file_id}'
    os.makedirs(preview_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(docx_path, 'r') as zip_ref:
            for file_name in zip_ref.namelist():
                if file_name.startswith('word/media/') and file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    image_data = zip_ref.read(file_name)
                    image_name = os.path.basename(file_name)
                    image_path = os.path.join(preview_dir, image_name)

                    with open(image_path, 'wb') as img_file:
                        img_file.write(image_data)

                    images.append(f'previews/{file_id}/{image_name}')
    except Exception as e:
        print(f"Ошибка извлечения картинок из DOCX: {e}")

    return images

def extract_images_from_pdf(pdf_path, file_id):
    """Извлекает превью страниц из PDF файла"""
    images = []
    preview_dir = f'static/previews/{file_id}'
    os.makedirs(preview_dir, exist_ok=True)

    try:
        # Пытаемся использовать pdf2image (требует poppler)
        from pdf2image import convert_from_path

        # Конвертируем первые 10 страниц (чтобы не перегружать)
        pages = convert_from_path(pdf_path, first_page=1, last_page=10, dpi=150)

        for i, page in enumerate(pages):
            image_name = f'page_{i+1}.jpg'
            image_path = os.path.join(preview_dir, image_name)
            page.save(image_path, 'JPEG')
            images.append(f'previews/{file_id}/{image_name}')

    except ImportError:
        print("pdf2image не установлен. Установите: pip install pdf2image")
    except Exception as e:
        print(f"Ошибка конвертации PDF: {e}")

    return images

def process_image_file(image_path, file_id):
    """Обрабатывает загруженное изображение (копирует как превью)"""
    images = []
    preview_dir = f'static/previews/{file_id}'
    os.makedirs(preview_dir, exist_ok=True)

    try:
        # Копируем изображение в папку превью
        image_name = os.path.basename(image_path)
        preview_path = os.path.join(preview_dir, image_name)
        shutil.copy2(image_path, preview_path)
        images.append(f'previews/{file_id}/{image_name}')
    except Exception as e:
        print(f"Ошибка обработки изображения: {e}")

    return images

def extract_previews(file_path, file_id):
    """Универсальная функция извлечения превью для разных типов файлов"""
    ext = get_file_extension(file_path)

    if ext == 'pptx':
        return extract_images_from_pptx(file_path, file_id)
    elif ext == 'docx':
        return extract_images_from_docx(file_path, file_id)
    elif ext == 'pdf':
        return extract_images_from_pdf(file_path, file_id)
    elif ext in FILE_CATEGORIES['image']:
        return process_image_file(file_path, file_id)

    return []

# Главная страница
@app.route('/')
def index():
    is_admin = session.get('is_admin', False)
    return render_template('index.html', is_admin=is_admin, t=get_translations(), lang=get_lang(), languages=['id', 'ru', 'en', 'es'])

# Смена языка
@app.route('/set-lang/<lang>')
def set_lang(lang):
    if lang in TRANSLATIONS:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))

# Создание комнаты
@app.route('/create-room', methods=['POST'])
def create_room():
    data = load_data()

    room_code = generate_room_code()
    while room_code in data['rooms']:
        room_code = generate_room_code()

    room_name = request.form.get('room_name', 'Урок')

    data['rooms'][room_code] = {
        'name': room_name,
        'created_at': datetime.now().isoformat(),
        'presentations': []
    }

    save_data(data)
    return redirect(url_for('room', code=room_code))

# Вход в комнату
@app.route('/join-room', methods=['POST'])
def join_room():
    code = request.form.get('room_code', '').strip()

    if code == ADMIN_CODE:
        session['is_admin'] = True
        return redirect(url_for('admin_panel'))

    data = load_data()
    if code in data['rooms']:
        return redirect(url_for('room', code=code))
    else:
        t = get_translations()
        return render_template('index.html', error=t['room_not_found'], is_admin=session.get('is_admin', False), t=t, lang=get_lang(), languages=['id', 'ru', 'en', 'es'])

# Страница комнаты
@app.route('/room/<code>')
def room(code):
    data = load_data()
    if code not in data['rooms']:
        return redirect(url_for('index'))

    room_data = data['rooms'][code]
    files = []

    for file_id in room_data['presentations']:
        if file_id in data['presentations']:
            file_data = data['presentations'][file_id]
            files.append({
                'id': file_id,
                'file_type': get_file_type(file_data['filename']),
                **file_data
            })

    # Группируем файлы по авторам для портфолио
    portfolios = {}
    for file in files:
        author = file.get('author', 'Аноним')
        if author not in portfolios:
            portfolios[author] = []
        portfolios[author].append(file)

    # Сортируем авторов по количеству работ (больше работ = выше)
    portfolios = dict(sorted(portfolios.items(), key=lambda x: len(x[1]), reverse=True))

    is_admin = session.get('is_admin', False)
    teacher_room = session.get('teacher_room', None)
    is_teacher = (teacher_room == code)
    can_edit = is_admin or is_teacher

    return render_template('room.html', 
                         room=room_data, 
                         room_code=code, 
                         presentations=files,
                         portfolios=portfolios,
                         is_admin=is_admin,
                         is_teacher=is_teacher,
                         can_edit=can_edit,
                         t=get_translations(),
                         lang=get_lang(),
                         languages=['id', 'ru', 'en', 'es'])

# Загрузка файла
@app.route('/upload/<room_code>', methods=['POST'])
def upload(room_code):
    data = load_data()

    if room_code not in data['rooms']:
        return jsonify({'error': 'Комната не найдена'}), 404

    if 'file' not in request.files:
        return jsonify({'error': 'Файл не выбран'}), 400

    file = request.files['file']
    author = request.form.get('author', 'Аноним').strip()

    if not author:
        author = 'Аноним'

    if file.filename == '':
        return jsonify({'error': 'Файл не выбран'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': 'Неподдерживаемый формат файла'}), 400

    file_id = str(uuid.uuid4())[:8]

    filename = secure_filename(file.filename)
    file_path = os.path.join(UPLOAD_FOLDER, f'{file_id}_{filename}')
    file.save(file_path)

    # Извлекаем превью в зависимости от типа файла
    images = extract_previews(file_path, file_id)

    data['presentations'][file_id] = {
        'filename': filename,
        'author': author,
        'file_path': file_path,
        'images': images,
        'file_type': get_file_type(filename),
        'uploaded_at': datetime.now().isoformat()
    }

    data['rooms'][room_code]['presentations'].append(file_id)
    save_data(data)

    return redirect(url_for('room', code=room_code))

# Скачивание файла
@app.route('/download/<file_id>')
def download(file_id):
    data = load_data()

    if file_id not in data['presentations']:
        return "Файл не найден", 404

    file_data = data['presentations'][file_id]
    return send_file(file_data['file_path'], 
                    as_attachment=True, 
                    download_name=file_data['filename'])

# Админ-панель
@app.route('/admin')
def admin_panel():
    if not session.get('is_admin'):
        return redirect(url_for('index'))

    data = load_data()

    # Добавляем информацию о типе файла
    for file_id, file_data in data['presentations'].items():
        file_data['file_type'] = get_file_type(file_data['filename'])

    return render_template('admin.html', data=data, t=get_translations(), lang=get_lang(), languages=['id', 'ru', 'en', 'es'])

# Удаление файла (админ)
@app.route('/admin/delete-presentation/<file_id>', methods=['POST'])
def delete_presentation(file_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()

    if file_id in data['presentations']:
        file_data = data['presentations'][file_id]

        if os.path.exists(file_data['file_path']):
            os.remove(file_data['file_path'])

        preview_dir = f'static/previews/{file_id}'
        if os.path.exists(preview_dir):
            shutil.rmtree(preview_dir)

        for room_code, room in data['rooms'].items():
            if file_id in room['presentations']:
                room['presentations'].remove(file_id)

        del data['presentations'][file_id]
        save_data(data)

    return redirect(url_for('admin_panel'))

# Удаление комнаты (админ)
@app.route('/admin/delete-room/<room_code>', methods=['POST'])
def delete_room(room_code):
    if not session.get('is_admin'):
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()

    if room_code in data['rooms']:
        for file_id in data['rooms'][room_code]['presentations']:
            if file_id in data['presentations']:
                file_data = data['presentations'][file_id]
                if os.path.exists(file_data['file_path']):
                    os.remove(file_data['file_path'])
                preview_dir = f'static/previews/{file_id}'
                if os.path.exists(preview_dir):
                    shutil.rmtree(preview_dir)
                del data['presentations'][file_id]

        del data['rooms'][room_code]
        save_data(data)

    return redirect(url_for('admin_panel'))

# Редактирование имени автора (админ)
@app.route('/admin/edit-author/<file_id>', methods=['POST'])
def edit_author(file_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()
    new_author = request.form.get('author', '').strip()

    if file_id in data['presentations'] and new_author:
        data['presentations'][file_id]['author'] = new_author
        save_data(data)

    return redirect(url_for('admin_panel'))

# Выход из админки
@app.route('/admin/logout')
def admin_logout():
    session.pop('is_admin', None)
    return redirect(url_for('index'))

# ============ API ============

# API: получить количество файлов в комнате (для автообновления)
@app.route('/api/room/<code>/count')
def room_count(code):
    data = load_data()
    if code not in data['rooms']:
        return jsonify({'count': 0, 'ids': []})
    return jsonify({
        'count': len(data['rooms'][code]['presentations']),
        'ids': data['rooms'][code]['presentations']
    })

# API: проверка админ-кода
@app.route('/api/check-admin', methods=['POST'])
def check_admin_code():
    code = request.json.get('code', '')
    room_code = request.json.get('room_code', '')

    if code == ADMIN_CODE:
        session['is_admin'] = True
        return jsonify({'success': True, 'role': 'admin'})

    if code == TEACHER_CODE and room_code:
        session['teacher_room'] = room_code
        return jsonify({'success': True, 'role': 'teacher'})

    return jsonify({'success': False})

# API: выход из админки/режима учителя (AJAX)
@app.route('/api/admin-logout', methods=['POST'])
def api_admin_logout():
    session.pop('is_admin', None)
    session.pop('teacher_room', None)
    return jsonify({'success': True})

# Удаление файла из комнаты (inline)
@app.route('/room/<room_code>/delete/<file_id>', methods=['POST'])
def delete_presentation_from_room(room_code, file_id):
    is_admin = session.get('is_admin', False)
    teacher_room = session.get('teacher_room', None)

    if not is_admin and teacher_room != room_code:
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()

    if file_id in data['presentations']:
        file_data = data['presentations'][file_id]

        if os.path.exists(file_data['file_path']):
            os.remove(file_data['file_path'])

        preview_dir = f'static/previews/{file_id}'
        if os.path.exists(preview_dir):
            shutil.rmtree(preview_dir)

        if room_code in data['rooms'] and file_id in data['rooms'][room_code]['presentations']:
            data['rooms'][room_code]['presentations'].remove(file_id)

        del data['presentations'][file_id]
        save_data(data)

    return redirect(url_for('room', code=room_code))

# Редактирование имени автора из комнаты
@app.route('/room/<room_code>/edit-author/<file_id>', methods=['POST'])
def edit_author_from_room(room_code, file_id):
    is_admin = session.get('is_admin', False)
    teacher_room = session.get('teacher_room', None)

    if not is_admin and teacher_room != room_code:
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()
    new_author = request.form.get('author', '').strip()

    if file_id in data['presentations'] and new_author:
        data['presentations'][file_id]['author'] = new_author
        save_data(data)

    return redirect(url_for('room', code=room_code))

# Переименование автора (все файлы автора в комнате)
@app.route('/room/<room_code>/rename-author', methods=['POST'])
def rename_author_in_room(room_code):
    is_admin = session.get('is_admin', False)
    teacher_room = session.get('teacher_room', None)

    if not is_admin and teacher_room != room_code:
        return jsonify({'error': 'Нет доступа'}), 403

    data = load_data()
    old_author = request.form.get('old_author', '').strip()
    new_author = request.form.get('new_author', '').strip()

    if not new_author or room_code not in data['rooms']:
        return redirect(url_for('room', code=room_code))

    # Переименовываем все файлы этого автора в комнате
    for file_id in data['rooms'][room_code]['presentations']:
        if file_id in data['presentations']:
            if data['presentations'][file_id].get('author') == old_author:
                data['presentations'][file_id]['author'] = new_author

    save_data(data)
    return redirect(url_for('room', code=room_code))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
