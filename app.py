from flask import Flask, render_template
from helpers import *


app = Flask(__name__)


data_for_index_page = read_csv('data/cookbook.csv')


@app.route('/')
def index():
    return render_template('index.html', data=data_for_index_page)


@app.route('/<string:name>')
def not_implemented(name):
    return f'''<h1>The page for {name.capitalize()} is not yet ready!</h1>
<h2>Click <a href="/"> here</a> to come back</h2>'''


if __name__ == '__main__':
    app.run()
