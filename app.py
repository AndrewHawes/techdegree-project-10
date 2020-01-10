import json

from flask import Flask, g, render_template

import config, models
from resources.todos import todos_api

app = Flask(__name__)
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.before_request
def before_request():
    g.db = models.DATABASE
    g.db.connect()


@app.after_request
def after_request(response):
    g.db.close()
    return response


@app.route('/')
def my_todos():
    return render_template('index.html')


if __name__ == '__main__':  # pragma: no cover
    models.initialize()
    if not models.Todo.select():
        with open('./mock/todos.json', 'r') as f:
            data = json.load(f)
        for todo in data:
            models.Todo.create(name=todo['name'])

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)
