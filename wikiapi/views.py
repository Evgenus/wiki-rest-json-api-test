from .app import app, db
from .models import Page, PageVersion, User
from flask import jsonify, request
import inspect

class InvalidArgument(Exception):
    status_code = 400

    def __init__(self, message, payload=None):
        super().__init__(self)
        self.message = message
        self.payload = dict(payload or ())

    def to_dict(self):
        rv = dict(self.payload)
        rv['message'] = self.message
        rv['error'] = type(self).__name__
        return rv

class InvalidRequestBody(InvalidArgument):
    """
    Required JSON body
    """
    def __init__(self):
        super().__init__(inspect.getdoc(self))

class RequiredArgument(InvalidArgument):
    """
    Field `{0}` is required.
    """
    def __init__(self, name, **kwargs):
        super().__init__(inspect.getdoc(self).format(name))
        self.payload["arg_name"] = name

class InvalidArgumentType(InvalidArgument):
    """
    Field `{0}` has value of invalid type. `{1}` value required.
    """
    def __init__(self, name, type, **kwargs):
        super().__init__(inspect.getdoc(self).format(name, type))
        self.payload["arg_name"] = name
        self.payload["type_name"] = type.__name__

@app.errorhandler(InvalidArgument)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def check_page_params(data):
    if data is None:
        raise InvalidRequestBody()

    if "title" not in data:
        raise RequiredArgument("title", payload=data)
    if "text" not in data:
        raise RequiredArgument("text", payload=data)

    title = data["title"]
    text = data["text"]

    if not isinstance(title, str): 
        raise InvalidArgumentType("title", str, payload=data)
    if not isinstance(text, str): 
        raise InvalidArgumentType("text", str, payload=data)

    return title, text

@app.route("/pages", methods=["POST"])
def add_page():
    data = request.get_json()

    title, text = check_page_params(data)

    page = Page()
    version = PageVersion(title=title, text=text, page=page)
    page.current = version

    db.session.add(page)
    db.session.add(version)
    db.session.commit()

    result = {
        "page": page.id,
        "version": version.id,
    }

    return jsonify(result)

@app.route("/pages", methods=["GET"])
def list_pages(): 
    query = db.session.query(Page)
    query = query.join(PageVersion, Page.current_id == PageVersion.id)
    query = query.options(
        db.Load(PageVersion).load_only("title")
        )

    result = [
        {
            "id": page.id,
            "version": page.current_id,
            "title": page.current.title,
        }
        for page in query.all()
    ]

    return jsonify(result)

@app.route('/pages/<int:page_id>', methods=['GET'])
def get_page(page_id):
    raise NotImplementedError()

@app.route('/pages/<int:page_id>/versions', methods=['GET'])
def get_page_versions(page_id):
    query = db.session.query(PageVersion)
    query = query.filter(PageVersion.page_id == page_id)

    result = [
        page_version.id
        for page_version in query.all()
    ]

    return jsonify(result)

@app.route('/versions/<int:version_id>', methods=['GET'])
def get_page_version(version_id):
    query = db.session.query(PageVersion)
    query = query.filter(PageVersion.id == version_id)
    query = query.join(Page, PageVersion.page_id == Page.id)
    page_version = query.first()

    result = {
        "id": page_version.id,
        "page": page_version.page_id,
        "current": page_version.page.current_id,
        "ancestor": page_version.ancestor_id,
        "title": page_version.title,
        "text": page_version.text,
    }

    return jsonify(result)

@app.route('/pages/<int:page_id>', methods=['PUT'])
def edit_page(page_id):
    data = request.get_json()

    title, text = check_page_params(data)

    page = db.session.query(Page).get(page_id)



@app.route('/pages/<int:page_id>/versions', methods=['PUT'])
def set_page_version(page_id):
    raise NotImplementedError()
