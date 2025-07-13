import logging
from flask import Flask, Response, Request
import random
import os
import sqlite3

app = Flask(__name__)

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
logging.basicConfig(
    filename='error.log',
    level=logging.ERROR,
    format='[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
)

# Общий стиль
STYLE = '''
    <style>
        body {
            background-color: #e0f7ff;
            font-family: Arial, sans-serif;
            text-align: center;
            padding-top: 50px;
        }
        h1 {
            color: #006699;
        }
        p {
            font-size: 20px;
        }
        a {
            margin: 10px;
            font-size: 18px;
            color: #004466;
            text-decoration: none;
        }
        .counter {
            position: fixed;
            bottom: 10px;
            right: 10px;
            font-size: 14px;
            color: gray;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            background-color: #006699;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
    </style>
'''

# Счётчик посещений
def update_counter():
    filename = "counter.txt"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("0")
    with open(filename, "r+") as f:
        count = int(f.read())
        count += 1
        f.seek(0)
        f.write(str(count))
        f.truncate()
    return count

# Главная страница
@app.route('/')
def home():
    count = update_counter()
    return f'''
    <html>
    <head>{STYLE}
    <script>
        async function getJoke() {{
            const response = await fetch('/random');
            const joke = await response.text();
            document.getElementById('joke-text').innerText = joke;
        }}
    </script>
    </head>
    <body>
        <h1>Анекдот дня</h1>
        <p id="joke-text">Нажми кнопку, чтобы увидеть анекдот!</p>
        <button onclick="getJoke()">Сгенерировать анекдот</button>
        <br><br>
        <a href="/about">О нас</a> | <a href="/contacts">Контакты</a>
        <div class="counter">👁️ Посещения: {count}</div>
    </body>
    </html>
    '''

# Отдаёт случайный анекдот из базы
@app.route('/random')
def random_joke():
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute('SELECT text FROM jokes')
    jokes = [row[0] for row in cursor.fetchall()]
    conn.close()

    if jokes:
        return Response(random.choice(jokes), content_type='text/plain; charset=utf-8')
    else:
        return Response("Анекдотов пока нет.", content_type='text/plain; charset=utf-8')

@app.route('/about')
def about():
    return f'''
    <html>
    <head>{STYLE}</head>
    <body>
        <h1>О проекте</h1>
        <p>Этот сайт показывает случайные анекдоты, а также используется для улучшения навыков в написании кода на Python</p>
        <a href="/">Главная</a> | <a href="/contacts">Контакты</a>
    </body>
    </html>
    '''

@app.route('/contacts')
def contacts():
    return '''
    <html>
    <head>
        <style>
            body {
                margin: 0;
                padding: 0;
                background-image: url('/static/me.jpg');
                background-size: cover;
                background-position: center;
                font-family: Arial, sans-serif;
                height: 100vh;
            }
            .overlay {
                background-color: rgba(0, 0, 0, 0.5);
                color: white;
                height: 100%;
                width: 100%;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                text-shadow: 0 0 5px black;
            }
            a {
                color: #ffcc00;
                text-decoration: none;
                font-size: 18px;
                margin-top: 20px;
            }
        </style>
    </head>
    <body>
        <div class="overlay">
            <h1>Контакты</h1>
            <p>Связаться со мной можно по почте: Danila.Isaev.com</p>
            <a href="/">На главную</a> | <a href="/about">О нас</a>
        </div>
    </body>
    </html>
    '''
# Обработка 404 — Страница не найдена
@app.errorhandler(404)
def page_not_found(e):
    app.logger.error(f"Ошибка 404: {request.path} не найдена.")
    return '''
    <html><head><title>Ошибка 404</title></head>
    <body style="text-align:center;padding-top:50px;">
        <h1 style="color:red;">Упс! Страница не найдена (404)</h1>
        <p>Похоже, вы забрели не туда.</p>
        <img src="/static/404.jpg" alt="404" width="300">
        <br><br><a href="/">Вернуться на главную</a>
    </body></html>
    ''', 404

# Обработка 500 — Внутренняя ошибка сервера
@app.errorhandler(500)
def internal_error(e):
    app.logger.error(f"Ошибка 500: {e}", exc_info=True)
    return '''
    <html><head><title>Ошибка 500</title></head>
    <body style="text-align:center;padding-top:50px;">
        <h1 style="color:red;">Ошибка сервера (500)</h1>
        <p>Что-то пошло не так. Мы уже работаем над этим!</p>
        <br><a href="/">Вернуться на главную</a>
    </body></html>
    ''', 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)