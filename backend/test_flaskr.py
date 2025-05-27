import os
import unittest
import json 

from flaskr import create_app
from flask_sqlalchemy import SQLAlchemy
from models import db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.database_name = "trivia_test"
        self.database_user = "postgres"
        self.database_password = "bais8170405"
        self.database_host = "localhost:5432"
        self.database_path = f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}/{self.database_name}"

        # Create app with the test configuration
        self.app = create_app({
            "SQLALCHEMY_DATABASE_URI": self.database_path,
            "SQLALCHEMY_TRACK_MODIFICATIONS": False,
            "TESTING": True
        })
        self.client = self.app.test_client
        self.new_question = {
            'question': 'What is the capital of Taiwan?',
            'answer': 'Taipei',
            'difficulty': 1,
            'category': 3
        }

        # Bind the app to the current context and create all tables
        with self.app.app_context():
            db.create_all()

    def test_get_categories_success(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['categories'])

    def test_get_questions_success(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)

    def test_get_questions_not_found(self):
        res = self.client().get('/questions?page=1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_delete_question_success(self):
        question = Question(question='Temp?', answer='Yes', difficulty=1, category=1)
        question.insert()
        res = self.client().delete(f'/questions/{question.id}')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_delete_question_not_found(self):
        res = self.client().delete('/questions/99999')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_post_question_success(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])

    def test_post_question_bad_request(self):
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

    def test_search_question_success(self):
        res = self.client().post('/questions', json={'searchTerm': 'capital'})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('questions', data)

    def test_get_questions_by_category_success(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['current_category'], 1)

    def test_get_questions_by_category_not_found(self):
        res = self.client().get('/categories/999/questions')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)

    def test_post_quiz_success(self):
        res = self.client().post('/quizzes', json={
            'previous_questions': [],
            'quiz_category': {'type': 'History', 'id': 1}
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertIn('question', data)

    def test_post_quiz_bad_request(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 400)

    def tearDown(self):
        """Executed after each test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
