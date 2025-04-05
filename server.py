from flask import Flask, render_template
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    return 'Willkommen zu meiner schönen App!'

@app.route('/zeit')
def zeit():
    current_time = datetime.now().strftime('%H:%M:%S')
    return f'Aktuelle Zeit: {current_time}'

@app.route('/hallo/<name>')
def hallo(name):
    return f'Hallo {name}!'

if __name__ == '__main__':
    app.run(debug=True)