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
        self.assertEqual(data.get("arg_name"), "title")

    def test_add_page_no_text(self):
        payload = json.dumps({
            "title": "title"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "RequiredArgument")
        self.assertEqual(data.get("arg_name"), "text")

    def test_add_page_invalid_title_type(self):
        payload = json.dumps({
            "title": 0,
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidArgumentType")
        self.assertEqual(data.get("arg_name"), "title")
        self.assertEqual(data.get("type_name"), "str")

    def test_add_page_invalid_text_type(self):
        payload = json.dumps({
            "title": "title",
            "text": 0
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidArgumentType")
        self.assertEqual(data.get("arg_name"), "text")
        self.assertEqual(data.get("type_name"), "str")

if __name__ == '__main__':
    unittest.main()