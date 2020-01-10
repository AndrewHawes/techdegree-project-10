from contextlib import contextmanager
import json
import unittest

from flask import template_rendered
from peewee import SqliteDatabase, IntegrityError

from app import app
from models import Todo

MODELS = [Todo]

test_db = SqliteDatabase(":memory:")


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)
        Todo.create(name='Test me!')
        self.client = app.test_client()

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()


class TodoApiTestCase(BaseTestCase):
    def test_todolist_get(self):
        response = self.client.get('/api/v1/todos')
        print(response.json[0]['name'])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), list)
        self.assertEqual(response.json[0]['name'], 'Test me!')

    def test_todolist_post(self):
        response = self.client.post(
            '/api/v1/todos',
            data=json.dumps({'name': 'Test post!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(type(response.json), dict)
        self.assertEqual(response.json['name'], 'Test post!')
        self.assertEqual(Todo.get(Todo.id == 2).name, 'Test post!')
        self.assertNotEqual(Todo.get(Todo.id == 2).name, "I'm a potato.")

    def test_todo_get(self):
        response = self.client.get('/api/v1/todos/1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), dict)
        self.assertEqual(response.json['name'], 'Test me!')
        self.assertEqual(Todo.get(Todo.id == 1).name, 'Test me!')
        self.assertNotEqual(Todo.get(Todo.id == 1).name, 'Socks? No, I’m okay.')

    def test_todo_put(self):
        response = self.client.put(
            '/api/v1/todos/1',
            data=json.dumps({'name': 'Keep testing me!'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(type(response.json), dict)
        self.assertEqual(response.json['name'], 'Keep testing me!')
        self.assertEqual(Todo.get(Todo.id == 1).name, 'Keep testing me!')
        self.assertNotEqual(Todo.get(Todo.id == 1).name, 'Buy fish sticks.')

    def test_todo_delete(self):
        response = self.client.delete('api/v1/todos/1')
        self.assertEqual(response.status_code, 204)
        with self.assertRaises(Todo.DoesNotExist):
            Todo.get(Todo.id == 1)


class TodoViewTestCase(BaseTestCase):
    def test_index(self):
        with captured_templates(app) as templates:
            response = self.client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(len(templates), 1)
            template, context = templates[0]
            self.assertEqual(template.name, 'index.html')


class TodoModelTestCase(BaseTestCase):
    def test_create(self):
        todo = Todo.create(name='Create a todo', completed=True)
        self.assertEqual(todo.name, 'Create a todo')

    def test_retrieve(self):
        todo = Todo.get(id=1)
        self.assertEqual(todo.name, 'Test me!')

    def test_enforces_constraints(self):
        with self.assertRaises(IntegrityError):
            Todo.create(name=None)


if __name__ == '__main__':
    unittest.main()
