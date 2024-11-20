import json
import random
from datetime import datetime, timedelta

def generate_data(file_path, count=1000000):
    names = []
    with open("names.txt", "r") as file:
        names = [line.strip() for line in file]

    today = datetime(2024, 11, 20)  
    data = []
    for i in range(count):
        record = {
            "id": i + 1,
            "name": random.choice(names),
            "value": random.randint(1, 1000000),
            "timestamp": (today - timedelta(days=random.randint(0, 365))).isoformat()
        }
        data.append(record)

    with open(file_path, "w") as json_file:
        json.dump(data, json_file)

if __name__ == "__main__":
    file_path = "data.json"
    print(f"Генерируются случайные данные в {file_path}...")
    generate_data(file_path)
    print(f"Генерация закончена")
