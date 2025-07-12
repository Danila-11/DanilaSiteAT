from flask import Flask
app = Flask(__name__)
import os

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

@app.route('/')
def home():
    count = update_counter()
    return f'''
    <html>
    <head>
STYLE = '''
        <style>
            body {{
                background-color: #e0f7ff;
                font-family: Arial, sans-serif;
                text-align: center;
                padding-top: 50px;
            }}
            h1 {{
                color: #006699;
            }}
            p {{
                font-size: 20px;
            }}
            .counter {{
                position: fixed;
                bottom: 10px;
                right: 10px;
                font-size: 14px;
                color: gray;
            }}
        </style>
'''
    </head>
    <body>
        <h1>Анекдот дня</h1>
        <p>Программист — это машина для преобразования кофе в код.</p>
        <a href="/about">О нас</a> | <a href="/contact">Контакты</a>
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
                background-color: rgba(0, 0, 0, 0.5); /* затемнение: чёрный, 50% прозрачности */
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
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
