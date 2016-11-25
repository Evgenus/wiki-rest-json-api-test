import unittest
from wikiapi.app import app

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        with app.app_context():
            flaskr.init_db()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()