# DataVista

DataVista — это веб-приложение на базе Flask, предназначенное для генерации, сортировки и отображения данных. Приложение включает аутентификацию пользователей, визуализацию данных с помощью Chart.js, функционал поиска с пагинацией и асинхронное обновление данных.

## Особенности

- **Аутентификация пользователей:** Безопасный вход и выход из системы с использованием Flask-Login.
- **Генерация и сортировка данных:** Автоматизированные процессы генерации и сортировки данных.
- **Топ-10 записей:** Отображение топ-10 записей с интерактивными графиками.
- **Поиск с пагинацией:** Фильтрация и навигация по данным с удобной разбивкой на страницы.
- **Асинхронное обновление данных:** Обновление данных без перезагрузки страницы с использованием AJAX и модальных окон.

## Технологии

- **Backend:** Python, Flask, Flask-Login, Flask-Caching
- **Frontend:** HTML, CSS, Bootstrap, JavaScript, Chart.js
- **Прочее:** Git, C++ (для сортировочного исполняемого файла)

## Установка

1. **Клонирование репозитория:**

    ```bash
    git clone https://github.com/ваш_пользователь/datavista.git
    cd datavista
    ```

2. **Создание и активация виртуального окружения:**

    ```bash
    python -m venv venv
    ```

    - **Windows:**
      ```bash
      venv\Scripts\activate
      ```
    - **Unix/Linux/MacOS:**
      ```bash
      source venv/bin/activate
      ```

3. **Установка зависимостей:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Настройка переменных окружения:**

    Создайте файл `.env` в корневой директории проекта и добавьте:

    ```
    SECRET_KEY=ваш_секретный_ключ
    ```

5. **Создание необходимых директорий:**

    Убедитесь, что директории `../logs/` и `../data/` существуют:

    ```bash
    mkdir ../logs
    mkdir ../data
    ```

6. **Размещение сортировочного исполняемого файла:**

    Убедитесь, что `sort_data.exe` (для Windows) или `sort_data` (для Unix/Linux) находится в директории `../data_processing/`.

## Использование

1. **Запуск приложения:**

    ```bash
    python app.py
    ```

2. **Доступ в браузере:**

    Перейдите по адресу [http://127.0.0.1:5000/](http://127.0.0.1:5000/).

3. **Стандартные четные данные для входа:**

    - **Имя пользователя:** admin
    - **Пароль:** password

## Контакты

Если у вас возникли вопросы или предложения, пожалуйста, свяжитесь с [drabchuk_04@mail.ru](mailto:drabchuk_04@mail.ru).
=======
# Kandidate Task

## Описание
Приложение для генерации, сортировки и анализа данных с веб-интерфейсом. Реализовано на Python и C++.

## Функциональность
- Генерация JSON-файла с миллионом записей.
- Сортировка данных по убыванию поля `value` (C++).
- Веб-приложение на Flask для отображения данных:
  - Топ-10 записей.
  - Поиск по имени или ID.
  - Обновление данных.

## Установка

### Python
1. Установите зависимости:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install flask
>>>>>>> eb620e270ebb58ea89952c9de0f87e04c2334633
