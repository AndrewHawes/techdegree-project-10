from flask import Blueprint

from flask_restful import (
    Api, fields, inputs, marshal, marshal_with, reqparse, Resource,
)

import models

todo_fields = {
    'id': fields.Integer,
    'name': fields.String,
    'completed': fields.Boolean
}

parser = reqparse.RequestParser()
parser.add_argument(
    'name',
    required=True,
    help='No todo name provided.',
    location=['form', 'json']
)
parser.add_argument(
    'completed',
    type=inputs.boolean,
    default=False,
    location=['form', 'json']
)


class TodoList(Resource):
    def get(self):
        todos = [marshal(todo, todo_fields) for todo in models.Todo.select()]
        return todos

    @marshal_with(todo_fields)
    def post(self):
        args = parser.parse_args()
        todo = models.Todo.create(**args)
        return todo, 201


class Todo(Resource):
    @marshal_with(todo_fields)
    def get(self, id):
        return models.Todo.get(models.Todo.id == id), 200

    @marshal_with(todo_fields)
    def put(self, id):
        args = parser.parse_args()
        query = models.Todo.update(**args).where(models.Todo.id == id)
        query.execute()
        return models.Todo.get(models.Todo.id == id), 200

    def delete(self, id):
        query = models.Todo.delete().where(models.Todo.id == id)
        query.execute()
        return '', 204


todos_api = Blueprint('resources.todos', __name__)
api = Api(todos_api)

api.add_resource(
    TodoList,
    '/todos',
    endpoint='todos'
)
api.add_resource(
    Todo,
    '/todos/<int:id>',
    endpoint='todo'
)