from flask import Flask
import random
import os

app = Flask(__name__)

# Общий стиль сайта
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
    </style>
'''

# Функция счётчика
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

JOKES = [
    "Программист — это машина для преобразования кофе в код.",
    "На 101% программист состоит из кофе и переменных.",
    "Сломался Wi-Fi — пришлось общаться с семьёй. Оказывается, милые люди!",
    "Программист не пьёт чай — он его компилирует.",
    "Говорят, сон полезен… но код ночью пишетcя лучше!",
    "Почему программисту не нужны очки? Потому что он всегда видит баги.",
    "Как зовут программиста, когда он в отпуске? Рест-программист.",
    "Сколько программистов нужно, чтобы вкрутить лампочку? Ни одного — это аппаратная проблема!",
    "Программисты не уходят — они просто выходят из цикла.",
    "Ошибка 404: шутка не найдена.",
    "Раньше я думал, что рекурсия — это сложно. А потом я понял, что рекурсия — это сложно.",
    "Git commit -am 'починил всё'. Надеюсь, правда.",
    "Программист заходит в бар. Бар не найден. Abort.",
    "Мама программиста говорит: 'Убери за собой!' Он пишет: rm -rf /home/",
    "Почему у программиста никогда не бывает личной жизни? Потому что у него всё — публичное.",
    "Рабочий день программиста: пить кофе, гуглить ошибки, дебажить гугленные ошибки.",
    "Тестировщик заходит в бар: заказывает 0 пива, -1 пива, 99999999 пива, кошку, %$@#.",
    "— Почему ты плачешь? — У меня null pointer exception...",
    "Любовь программиста: if (люблю) {{ женюсь(); }} else {{ continue; }}",
    "Программисты тоже люди. Просто странные.",
    "Самый страшный звук — это тишина после запуска кода.",
    "Почему программисты любят тёмную тему? Потому что свет — это баг.",
    "Код без комментариев — как книга без заголовков: вроде красиво, но непонятно.",
    "Debug — как охота на призраков: ты знаешь, что они есть, но где?",
    "Ctrl+C, Ctrl+V — главный инструмент современного гения.",
    "Сказал себе: «Ща 5 минут пофиксю», — и на следующее утро проснулся в 6:00.",
    "Почему программисты не идут в спортзал? Потому что у них уже есть класс Body.",
    "Идеальный код — это как единорог: все о нём говорят, но никто не видел.",
    "Код работает? Не трогай. Не работает? Всё равно не трогай — станет хуже.",
    "Пишу код: 10% мышление, 90% борьба с собой."
]

@app.route('/random')
def random_joke():
    return random.choice(JOKES)

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)