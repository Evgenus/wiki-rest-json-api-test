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

@app.route("/pages", methods=["POST"])
def add_page():
    data = request.get_json()

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

    version = PageVersion(title=title, text=text)
    db.session.add(version)
    db.session.commit()

    page = Page(current=version.id)
    db.session.add(page)
    db.session.commit()

    return jsonify({})

@app.route("/pages", methods=["GET"])
def list_pages(): 
    raise NotImplementedError()

@app.route('/pages/<int:page>', methods=['GET'])
def get_page(page):
    raise NotImplementedError()

@app.route('/pages/<int:page>/versions', methods=['GET'])
def get_page_versions(page):
    raise NotImplementedError()

@app.route('/pages/<int:page>', methods=['PUT'])
def edit_page(page):
    raise NotImplementedError()

@app.route('/pages/<int:page>/versions', methods=['PUT'])
def set_page_version(page):
    raise NotImplementedError()
