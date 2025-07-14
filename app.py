import logging
from flask import Flask, request, render_template_string, redirect, url_for, Response, session
import random
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'simon'

def get_random_joke_id(exclude_id=None):
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    if exclude_id:
        cursor.execute("SELECT id FROM jokes WHERE id != ? ORDER BY RANDOM() LIMIT 1", (exclude_id,))
    else:
        cursor.execute("SELECT id FROM jokes ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def get_joke_text_by_id(joke_id):
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM jokes WHERE id = ?", (joke_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "Анекдот не найден"

# === ЛОГИРОВАНИЕ ===
logging.basicConfig(
    filename='error.log',
    level=logging.WARNING,
    format='%(asctime)s [%(levelname)s] %(message)s',
    encoding='utf-8'
)

# === ФУНКЦИИ ===

def get_random_joke_from_db(exclude_text=None):
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()

    if exclude_text:
        cursor.execute("SELECT text FROM jokes WHERE text != ? ORDER BY RANDOM() LIMIT 1", (exclude_text,))
    else:
        cursor.execute("SELECT text FROM jokes ORDER BY RANDOM() LIMIT 1")

    result = cursor.fetchone()
    conn.close()

    return result[0] if result else None

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

# === РОУТЫ ===

@app.route('/')
def home():
    count = update_counter()
    return f'''
    <html>
    <head>{STYLE}</head>
    <body>
        <h1>Добро пожаловать!</h1>
        <p>Нажмите на кнопку ниже, чтобы получить случайный анекдот 👇</p>
        <form action="/generate" method="post">
            <button type="submit">🔁 Сгенерировать анекдот</button>
        </form>
        <br><br>
        <a href="/about">О нас</a> | <a href="/contacts">Контакты</a> | <a href="/battle">Битва анекдотов</a>
        <div class="counter">👁️ Посещения: {count}</div>
    </body>
    </html>
    '''

@app.route('/generate', methods=['POST'])
def generate_joke():
    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM jokes ORDER BY RANDOM() LIMIT 1")
    result = cursor.fetchone()
    conn.close()

    if result:
        joke_id = result[0]
        return redirect(f'/joke/{joke_id}')
    else:
        return "<h1>Анекдотов пока нет</h1>"

@app.route('/joke/<int:joke_id>')
def show_joke(joke_id):
    with open("counter.txt", "r") as f:
        count = int(f.read())

    conn = sqlite3.connect('jokes.db')
    cursor = conn.cursor()
    cursor.execute("SELECT text, likes FROM jokes WHERE id = ?", (joke_id,))
    result = cursor.fetchone()
    conn.close()

    if result:
        text, likes = result
    else:
        text = "Анекдот не найден"
        likes = 0

    liked = joke_id in session.get('liked_jokes', [])

    return f'''
    <html>
    <head>{STYLE}
    <script>
        async function likeJoke(jokeId) {{
            const response = await fetch('/like/' + jokeId, {{
                method: 'POST'
            }});
            const result = await response.text();
            if (result === 'ok') {{
                const countElem = document.getElementById('like-count');
                countElem.innerText = parseInt(countElem.innerText) + 1;
                document.getElementById('like-btn').disabled = true;
            }} else if (result === 'already liked') {{
                alert("Вы уже поставили лайк этому анекдоту.");
            }}
        }}
    </script>
    </head>
    <body>
        <h1>Анекдот дня</h1>
        <p>{text}</p>
        <button id="like-btn" onclick="likeJoke({joke_id})" {'disabled' if liked else ''}>❤️ Лайк (<span id='like-count'>{likes}</span>)</button>
        <form action="/generate" method="post" style="display:inline; margin-left: 10px;">
            <button type="submit">🔁 Сгенерировать анекдот</button>
        </form>
        <br><br>
        <a href="/about">О нас</a> | <a href="/contacts">Контакты</a> | <a href="/battle">Битва анекдотов</a>
        <div class="counter">👁️ Посещения: {count}</div>
    </body>
    </html>
    '''

@app.route('/like/<int:joke_id>', methods=['POST'])
def like(joke_id):
    liked_jokes = session.get('liked_jokes', [])
    if joke_id in liked_jokes:
        return 'already liked', 200

    conn = sqlite3.connect('jokes.db')
    c = conn.cursor()
    c.execute('UPDATE jokes SET likes = likes + 1 WHERE id = ?', (joke_id,))
    conn.commit()
    conn.close()

    liked_jokes.append(joke_id)
    session['liked_jokes'] = liked_jokes

    return 'ok', 200

@app.route('/battle')
def battle():
    battle_count = session.get('battle_count', 0)
    winner_id = session.get('winner_id')

    if battle_count >= 30 and winner_id:
        conn = sqlite3.connect('jokes.db')
        cursor = conn.cursor()
        cursor.execute("SELECT text FROM jokes WHERE id = ?", (winner_id,))
        winner_text = cursor.fetchone()
        conn.close()

        return render_template_string('''
        <html><head>
        <style>
        body { background-color: #cceeff; font-family: sans-serif; text-align: center; padding: 50px; }
        h1 { color: #003366; }
        .joke-box { background: white; border-radius: 10px; padding: 30px; font-size: 20px; margin: 30px auto; width: 60%; }
        .button { margin-top: 30px; font-size: 18px; text-decoration: none; background: #003366; color: white; padding: 10px 20px; border-radius: 5px; }
        </style></head>
        <body>
            <h1>Это самый лучший анекдот на этом сайте, по твоему мнению</h1>
            <div class="joke-box">{{ winner }}</div>
            <a href="/battle/reset" class="button">Начать заново</a>
        </body>
        </html>
        ''', winner=winner_text[0] if winner_text else "Ошибка загрузки анекдота")

    left_id = session.get('current_left_id')
    right_id = session.get('current_right_id')

    if not left_id:
        left_id = get_random_joke_id()
    if not right_id or right_id == left_id:
        right_id = get_random_joke_id(exclude_id=left_id)

    session['current_left_id'] = left_id
    session['current_right_id'] = right_id

    left_text = get_joke_text_by_id(left_id)
    right_text = get_joke_text_by_id(right_id)

    return render_template_string('''
    <html><head>
    <style>
    body { margin: 0; font-family: sans-serif; overflow-x: hidden; }
    h1 {
        text-align: center;
        margin: 20px 0 5px;
        font-size: 32px;
    }
    .counter {
        text-align: center;
        font-size: 20px;
        margin-bottom: 10px;
    }
    .split { width: 50%; height: 100vh; position: fixed; top: 100px; display: flex; flex-direction: column; justify-content: center; padding: 50px; box-sizing: border-box; }
    .left { left: 0; background: #d0eaff; }
    .right { right: 0; background: #ffe0f0; }
    .joke { font-size: 20px; padding: 20px; background: white; border-radius: 10px; cursor: pointer; margin: auto; }
    .line { position: fixed; top: 100px; bottom: 90px; left: 50%; width: 2px; background: black; z-index: 0; }
    .bottom-button { position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); z-index: 2; }
    .button { font-size: 18px; text-decoration: none; background: #003366; color: white; padding: 10px 20px; border-radius: 5px; }
    </style>
    <script>
    function vote(joke_id) {
        fetch("/vote", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: "winner_id=" + encodeURIComponent(joke_id)
        }).then(() => {
            location.reload();
        });
    }
    </script>
    </head>
    <body>
        <h1>Выбери лучший анекдот</h1>
        <div class="counter">Батл {{ battle_count + 1 }} из 30</div>
        <div class="split left"><div class="joke" onclick="vote({{ left_id }})">{{ left_text }}</div></div>
        <div class="split right"><div class="joke" onclick="vote({{ right_id }})">{{ right_text }}</div></div>
        <div class="line"></div>
        <div class="bottom-button"><a href="/" class="button">На главную</a></div>
    </body></html>
    ''', left_text=left_text, right_text=right_text, left_id=left_id, right_id=right_id, battle_count=battle_count)

@app.route('/vote', methods=['POST'])
def vote():
    winner_id = int(request.form.get('winner_id'))
    left_id = session.get('current_left_id')
    right_id = session.get('current_right_id')
    battle_count = session.get('battle_count', 0)

    session['winner_id'] = winner_id
    session['battle_count'] = battle_count + 1

    if winner_id == left_id:
        # обновляем правого (проигравшего)
        session['current_right_id'] = get_random_joke_id(exclude_id=winner_id)
    else:
        # обновляем левого (проигравшего)
        session['current_left_id'] = get_random_joke_id(exclude_id=winner_id)

    return '', 204

@app.route('/battle/reset')
def reset_battle():
    for key in ['battle_count', 'winner_id', 'current_left_id', 'current_right_id']:
        session.pop(key, None)
    return redirect('/battle')

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
            body {{
                margin: 0;
                padding: 0;
                background-image: url('/static/me.jpg');
                background-size: cover;
                background-position: center;
                font-family: Arial, sans-serif;
                height: 100vh;
            }}
            .overlay {{
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
            }}
            a {{
                color: #ffcc00;
                text-decoration: none;
                font-size: 18px;
                margin-top: 20px;
            }}
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