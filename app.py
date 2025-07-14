import logging
from flask import Flask, request, render_template, redirect, url_for, Response, redirect
import random
import os
import sqlite3

app = Flask(__name__)

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
import logging
from flask import Flask, request

logging.basicConfig(
    filename='error.log',
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

app_logger = logging.getLogger(__name__)

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
import sqlite3

@app.route('/')
def home():
    count = update_counter()

    # Получаем случайный анекдот из базы
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id, text, likes FROM jokes ORDER BY RANDOM() LIMIT 1")
    joke = cursor.fetchone()
    conn.close()

    if joke:
        joke_id, text, likes = joke
    else:
        text = "Анекдотов нет :("
        joke_id = 0
        likes = 0

    return f'''
    <html>
    <head>{STYLE}</head>
    <body>
        <h1>Анекдот дня</h1>
        <p>{text}</p>

        <form action="/like/{joke_id}" method="post" style="display:inline;">
            <button type="submit">❤️ Лайк ({likes})</button>
        </form>

        <form action="/" method="get" style="display:inline; margin-left: 10px;">
            <button type="submit">🔁 Сгенерировать анекдот</button>
        </form>

        <br><br>
        <a href="/about">О нас</a> | <a href="/contacts">Контакты</a>
        <div class="counter">👁️ Посещения: {count}</div>
    </body>
    </html>
    '''

#Обработчик лайков
@app.route('/like/<int:joke_id>', methods=['POST'])
def like_joke(joke_id):
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE jokes SET likes = likes + 1 WHERE id = ?", (joke_id,))
    conn.commit()
    conn.close()
    return redirect('/')

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