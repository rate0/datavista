import os
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, UserMixin, current_user
from flask_caching import Cache
import subprocess
import json
from dotenv import load_dotenv
import logging
from werkzeug.security import generate_password_hash, check_password_hash
from math import ceil
import threading

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'D3f4Ult') 

# Определение базового каталога
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Пути к директориям logs и data
LOGS_DIR = os.path.join(BASE_DIR, '../logs')
DATA_DIR = os.path.join(BASE_DIR, '../data')

# Создание директорий logs и data, если они не существуют
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Настройка логирования
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(os.path.join(LOGS_DIR, 'app.log'), encoding='utf-8')
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Настройка Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Настройка кэширования
cache = Cache(app, config={'CACHE_TYPE': 'simple'}) 

# Класс пользователя
class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# Пользователи
users = {
    'admin': User(id=1, username='admin', password_hash=generate_password_hash('password'))
}

# Загрузка пользователя
@login_manager.user_loader
def load_user(user_id):
    for user in users.values():
        if user.id == int(user_id):
            return user
    return None

# Пути к файлам и скриптам
DATA_FILE = os.path.join(DATA_DIR, 'sorted_data.json')
DATA_GENERATION_SCRIPT = os.path.join(BASE_DIR, '../data_generation/generate_data.py')
DATA_SORTING_EXECUTABLE_WINDOWS = os.path.join(BASE_DIR, '../data_processing/sort_data.exe')
DATA_SORTING_EXECUTABLE_UNIX = os.path.join(BASE_DIR, '../data_processing/sort_data')

# Функция загрузки отсортированных данных
def load_sorted_data():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Загружено {len(data)} записей из sorted_data.json.")
        return data
    except Exception as e:
        logger.error(f"Ошибка при загрузке данных: {e}")
        return []

sorted_data = []

# Блокировки для потоков
data_lock = threading.Lock()
update_in_progress = False
update_lock = threading.Lock()

# Функция обеспечения наличия данных
def ensure_data():
    global sorted_data
    data_exists = os.path.exists(DATA_FILE)
    if not data_exists:
        generate_and_sort_data(initial=True)
    with data_lock:
        sorted_data = load_sorted_data()

# Функция генерации и сортировки данных
def generate_and_sort_data(initial=False):
    global update_in_progress
    try:
        if not initial:
            logger.info("Запуск генерации данных.")
        data_gen_dir = os.path.join(BASE_DIR, '../data_generation')
        subprocess.run(['python', DATA_GENERATION_SCRIPT], check=True, cwd=data_gen_dir)
        if not initial:
            logger.info("Генерация данных завершена.")
        
        if os.name == 'nt':
            sort_executable = DATA_SORTING_EXECUTABLE_WINDOWS
        else:
            sort_executable = DATA_SORTING_EXECUTABLE_UNIX
        
        if not os.path.exists(sort_executable):
            if not initial:
                logger.error(f"Файл сортировки {sort_executable} не найден.")
            return
        
        if not initial:
            logger.info("Запуск сортировки данных.")
        data_proc_dir = os.path.join(BASE_DIR, '../data_processing')
        subprocess.run([sort_executable], check=True, cwd=data_proc_dir)
        if not initial:
            logger.info("Сортировка данных завершена.")
    except subprocess.CalledProcessError as e:
        if not initial:
            logger.error(f"Ошибка при генерации или сортировке данных: {e}")
    finally:
        with update_lock:
            update_in_progress = False

# Маршруты приложения

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = users.get(username)
        if user and user.verify_password(password):
            login_user(user)
            flash("Вы вошли в систему.", "success")
            logger.info(f"Пользователь {username} вошел в систему.")
            return redirect(url_for('index'))
        else:
            flash("Неверные учетные данные.", "danger")
            logger.warning(f"Неудачная попытка входа пользователя {username}.")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash("Вы вышли из системы.", "info")
    logger.info(f"Пользователь {username} вышел из системы.")
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/top10')
@login_required
@cache.cached(timeout=300, key_prefix='top10')
def top10():
    try:
        with data_lock:
            top_records = sorted_data[:10]
        logger.info("Отображение топ-10 записей.")
        return render_template('top10.html', records=top_records)
    except Exception as e:
        flash("Ошибка при получении топ-10 записей.", "danger")
        logger.error(f"Ошибка при получении топ-10 записей: {e}")
        return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
@login_required
def update():
    global update_in_progress
    with update_lock:
        if update_in_progress:
            return jsonify({'status': 'already_in_progress'}), 200
        update_in_progress = True
    def run_update():
        generate_and_sort_data()
        with data_lock:
            global sorted_data
            sorted_data = load_sorted_data()
        cache.delete('top10')
        logger.info("Данные обновлены успешно.")
    thread = threading.Thread(target=run_update)
    thread.start()
    return jsonify({'status': 'started'}), 200

@app.route('/check_update', methods=['GET'])
@login_required
def check_update():
    with update_lock:
        if update_in_progress:
            return jsonify({'status': 'in_progress'}), 200
        else:
            return jsonify({'status': 'completed'}), 200

@app.route('/search', methods=['GET'])
@login_required
def search():
    results = []
    page = request.args.get('page', 1, type=int)
    per_page = 50
    total_pages = 1

    query_param = request.args.get('query', '').strip()
    min_value = request.args.get('min_value', type=int)
    max_value = request.args.get('max_value', type=int)
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    if query_param or min_value is not None or max_value is not None or start_date or end_date:
        try:
            with data_lock:
                filtered_data = sorted_data

                if query_param:
                    if query_param.isdigit():
                        filtered_data = [record for record in filtered_data if record['id'] == int(query_param)]
                    else:
                        filtered_data = [record for record in filtered_data if query_param.lower() in record['name'].lower()]
                
                if min_value is not None:
                    filtered_data = [record for record in filtered_data if record['value'] >= min_value]
                
                if max_value is not None:
                    filtered_data = [record for record in filtered_data if record['value'] <= max_value]
                
                if start_date:
                    filtered_data = [record for record in filtered_data if record['timestamp'] >= start_date]
                
                if end_date:
                    filtered_data = [record for record in filtered_data if record['timestamp'] <= end_date]
        
            total_records = len(filtered_data)
            total_pages = ceil(total_records / per_page) if total_records > 0 else 1

            if page < 1 or page > total_pages:
                flash("Неверный номер страницы.", "warning")
                logger.warning(f"Пользователь попытался перейти на неверную страницу: {page}")
                return redirect(url_for('search', page=1, query=query_param, min_value=min_value, max_value=max_value, start_date=start_date, end_date=end_date))
            
            offset = (page - 1) * per_page
            results = filtered_data[offset:offset + per_page]

            if not results:
                flash("Записи не найдены.", "info")
                logger.info("Поиск не дал результатов.")
            else:
                logger.info(f"Поиск вернул {len(results)} записей на странице {page}.")

        except Exception as e:
            flash("Ошибка при поиске данных.", "danger")
            logger.error(f"Ошибка при поиске данных: {e}")
            return redirect(url_for('index'))
    else:
        flash("Пожалуйста, введите критерии для поиска.", "info")
        logger.info("Пользователь посетил страницу поиска без критериев.")

    return render_template('search.html', results=results, page=page, total_pages=total_pages, query=query_param, min_value=min_value, max_value=max_value, start_date=start_date, end_date=end_date)

if __name__ == '__main__':
    try:
        ensure_data()
    except RuntimeError as e:
        print(f"Критическая ошибка при инициализации данных: {e}")
        exit(1)
    app.run(debug=True)
