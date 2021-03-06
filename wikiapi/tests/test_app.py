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

    def post_json(self, uri, data):
        data = json.dumps(data)
        rv = self.app.post(uri, data=data, content_type='application/json')
        rv.json = json.loads(rv.get_data(as_text=True))
        return rv

    def put_json(self, uri, data):
        data = json.dumps(data)
        rv = self.app.put(uri, data=data, content_type='application/json')
        rv.json = json.loads(rv.get_data(as_text=True))
        return rv

    def get_json(self, uri):
        rv = self.app.get(uri)
        rv.json = json.loads(rv.get_data(as_text=True))
        return rv        

    def test_add_page_no_body(self):
        rv = self.app.post("/pages")
        self.assertEqual(rv.status_code, 400)
        data = json.loads(rv.get_data(as_text=True))
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidRequestBody")

    def test_add_page_no_title(self):
        payload = {
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 400)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "RequiredArgument")
        self.assertEqual(data.get("arg_name"), "title")

    def test_add_page_no_text(self):
        payload = {
            "title": "title"
        }
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 400)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "RequiredArgument")
        self.assertEqual(data.get("arg_name"), "text")

    def test_add_page_invalid_title_type(self):
        payload = {
            "title": 0,
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 400)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidArgumentType")
        self.assertEqual(data.get("arg_name"), "title")
        self.assertEqual(data.get("type_name"), "str")

    def test_add_page_invalid_text_type(self):
        payload = {
            "title": "title",
            "text": 0
        }
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 400)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidArgumentType")
        self.assertEqual(data.get("arg_name"), "text")
        self.assertEqual(data.get("type_name"), "str")

    def test_add_page_success_simple(self):
        payload = {
            "title": "title",
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 200)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(Page.query.count(), 1)
        self.assertEqual(PageVersion.query.count(), 1)
        self.assertIn("page", data)
        self.assertIn("version", data)

    def test_add_page_success_double(self):
        payload = {
            "title": "title",
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        rv = self.post_json("/pages", data=payload)
        self.assertEqual(rv.status_code, 200)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(Page.query.count(), 2)
        self.assertEqual(PageVersion.query.count(), 2)
        page1, page2 = Page.query.all()
        self.assertNotEqual(page1.id, page2.id)
        self.assertNotEqual(page1.current_id, page2.current_id)

    def test_list_pages(self):
        payload = {
            "title": "title",
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        rv = self.post_json("/pages", data=payload)
        rv = self.get_json("/pages")
        self.assertEqual(rv.status_code, 200)
        data = rv.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)
        self.assertIn("title", data[0])
        self.assertIn("id", data[0])
        self.assertIn("version", data[0])

    def test_page_versions_simple(self):
        payload = {
            "title": "title",
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        rv = self.get_json("/pages/{0}/versions".format(page_id))
        data = rv.json

        self.assertSequenceEqual(data, [version_id])

    def test_page_version_simple(self):
        payload = {
            "title": "title",
            "text": "text"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        rv = self.get_json("/versions/{0}".format(version_id))
        data = rv.json

        self.assertEqual(data["id"], version_id)
        self.assertEqual(data["page"], page_id)
        self.assertEqual(data["current"], version_id)
        self.assertEqual(data["ancestor"], None)
        self.assertEqual(data["title"], "title")
        self.assertEqual(data["text"], "text")

    def test_edit_page(self):
        payload = {
            "title": "title1",
            "text": "text1"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        payload = {
            "title": "title2",
            "text": "text2"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_2 = data["version"]

        rv = self.get_json("/pages/{0}/versions".format(page_id))
        data = rv.json

        self.assertSetEqual(set(data), {version_id, version_id_2})

        rv = self.get_json("/pages")
        self.assertEqual(rv.status_code, 200)
        data = rv.json
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "title2")
        self.assertEqual(data[0]["version"], version_id_2)

    def test_get_page(self):
        payload = {
            "title": "title1",
            "text": "text1"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        rv = self.get_json("/pages/{0}".format(page_id))
        data = rv.json
        self.assertEqual(data["title"], "title1")
        self.assertEqual(data["version"], version_id)

        payload = {
            "title": "title2",
            "text": "text2"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_2 = data["version"]

        rv = self.get_json("/pages/{0}".format(page_id))
        data = rv.json
        self.assertEqual(data["title"], "title2")
        self.assertEqual(data["version"], version_id_2)

    def test_change_page_version(self):
        payload = {
            "title": "title1",
            "text": "text1"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        payload = {
            "title": "title2",
            "text": "text2"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_2 = data["version"]

        payload = {
            "title": "title3",
            "text": "text3"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_3 = data["version"]

        rv = self.get_json("/pages/{0}".format(page_id))
        data = rv.json
        self.assertEqual(data["title"], "title3")
        self.assertEqual(data["version"], version_id_3)

        payload = {
            "version": version_id
        }
        rv = self.put_json("/pages/{0}/versions".format(page_id), data=payload)
        data = rv.json

        rv = self.get_json("/pages/{0}".format(page_id))
        data = rv.json
        self.assertEqual(data["title"], "title1")
        self.assertEqual(data["version"], version_id)
        
    def test_change_page_version_fail(self):
        payload = {
            "title": "title1other",
            "text": "text1"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id_other = data["version"]

        payload = {
            "title": "title1",
            "text": "text1"
        }
        rv = self.post_json("/pages", data=payload)
        data = rv.json
        version_id = data["version"]
        page_id = data["page"]

        payload = {
            "title": "title2",
            "text": "text2"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_2 = data["version"]

        payload = {
            "title": "title3",
            "text": "text3"
        }
        rv = self.put_json("/pages/{0}".format(page_id), data=payload)
        data = rv.json

        version_id_3 = data["version"]

        rv = self.get_json("/pages/{0}".format(page_id))
        data = rv.json
        self.assertEqual(data["title"], "title3")
        self.assertEqual(data["version"], version_id_3)

        payload = {
            "version": version_id_other
        }
        rv = self.put_json("/pages/{0}/versions".format(page_id), data=payload)
        data = rv.json

        self.assertEqual(rv.status_code, 400)
        data = rv.json
        self.assertNotEqual(data, None)
        self.assertEqual(data.get("error"), "InvalidArgumentValue")
        self.assertEqual(data.get("arg_name"), "version")

if __name__ == '__main__':
    unittest.main()