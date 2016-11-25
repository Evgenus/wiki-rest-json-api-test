import unittest
import json
from wikiapi.app import app

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()

    def tearDown(self):
        pass

    def test_add_page_no_body(self):
        rv = self.app.post("/pages")
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidRequestBody")

    def test_add_page_no_title(self):
        payload = json.dumps({
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "RequiredArgument")

if __name__ == '__main__':
    unittest.main()