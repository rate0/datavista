# data_generation/generate_data.py

import json
import random
from datetime import datetime, timedelta
import os
import logging

def setup_logging(log_file_path):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def load_names(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)
    
    if not os.path.exists(filepath):
        logging.error(f"Файл {filepath} не найден.")
        return []
    
    with open(filepath, 'r', encoding='utf-8') as f:
        names = [line.strip() for line in f if line.strip()]
    return names

def generate_data(num_records, names):
    data = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(1, num_records + 1):
        name = random.choice(names)
        value = random.randint(1, 1000000) 
        timestamp = (start_date + timedelta(seconds=random.randint(0, 365*24*60*60))).strftime('%Y-%m-%d %H:%M:%S')
        data.append({
            "id": i,
            "name": name,
            "value": value,
            "timestamp": timestamp
        })
        if i % 100000 == 0:
            logging.info(f"{i} записей сгенерировано.")
    return data

def main():
    log_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../logs/app.log')
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    setup_logging(log_file_path)
    
    names = load_names('names.txt')
    if not names:
        logging.error("Список имен пуст или файл names.txt не найден.")
        return
    logging.info("Начинается генерация данных...")
    data = generate_data(1000000, names)
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data')
    os.makedirs(output_dir, exist_ok=True) 
    output_file = os.path.join(output_dir, 'data.json')
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Генерация данных завершена. Данные сохранены в {output_file}.")
    except Exception as e:
        logging.error(f"Ошибка при сохранении данных: {e}")

if __name__ == '__main__':
    main()
