import unittest
import json
from wikiapi.app import app, db
from wikiapi.models import Page, PageVersion

class AppTestCase(unittest.TestCase):

    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()

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

    def test_add_page_success_simple(self):
        payload = json.dumps({
            "title": "title",
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(Page.query.count(), 1)
        self.assertEqual(PageVersion.query.count(), 1)
        self.assertIn("page", data)
        self.assertIn("version", data)

    def test_add_page_success_double(self):
        payload = json.dumps({
            "title": "title",
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(Page.query.count(), 2)
        self.assertEqual(PageVersion.query.count(), 2)
        page1, page2 = Page.query.all()
        self.assertNotEqual(page1.id, page2.id)
        self.assertNotEqual(page1.current_id, page2.current_id)

    def test_list_pages(self):
        payload = json.dumps({
            "title": "title",
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        rv = self.app.get("/pages")
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.get_data(as_text=True))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertIn("title", data[0])
        self.assertIn("id", data[0])
        self.assertIn("version", data[0])

    def test_page_versions_simple(self):
        payload = json.dumps({
            "title": "title",
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        version_id = data["version"]
        page_id = data["page"]

        rv = self.app.get("/pages/{0}/versions".format(page_id))
        data = json.loads(rv.get_data(as_text=True))

        self.assertSequenceEqual(data, [version_id])

    def test_page_version_simple(self):
        payload = json.dumps({
            "title": "title",
            "text": "text"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        version_id = data["version"]
        page_id = data["page"]

        rv = self.app.get("/versions/{0}".format(version_id))
        data = json.loads(rv.get_data(as_text=True))

        self.assertEqual(data["id"], version_id)
        self.assertEqual(data["page"], page_id)
        self.assertEqual(data["current"], version_id)
        self.assertEqual(data["ancestor"], None)
        self.assertEqual(data["title"], "title")
        self.assertEqual(data["text"], "text")

    def test_edit_page(self):
        payload = json.dumps({
            "title": "title1",
            "text": "text1"
        })
        rv = self.app.post("/pages", data=payload, content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))
        version_id = data["version"]
        page_id = data["page"]

        payload = json.dumps({
            "title": "title2",
            "text": "text2"
        })
        rv = self.app.put("/pages/{0}".format(page_id), data=payload, content_type='application/json')
        data = json.loads(rv.get_data(as_text=True))

        version_id_2 = data["version"]

        rv = self.app.get("/pages/{0}/versions".format(page_id))
        data = json.loads(rv.get_data(as_text=True))

        self.assertSetEqual(set(data), {version_id, version_id_2})

        rv = self.app.get("/pages")
        self.assertEqual(rv.status_code, 200)
        data = json.loads(rv.get_data(as_text=True))
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "title2")
        self.assertEqual(data[0]["version"], version_id_2)
if __name__ == '__main__':
    unittest.main()