from .app import app
from flask import jsonify, request

class InvalidArgument(Exception):
    status_code = 400

    def __init__(self, message, payload=None):
        super().__init__(self)
        self.message = message
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv

class RequiredArgument(InvalidArgument):
    """
    field `{0}` is required for this request
    """
    def __init__(self, name, **kwargs):
        super().__init__(inspect.getdoc(self).format(name))

@app.errorhandler(InvalidArgument)
def handle_exception(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.route("/pages", methods=["POST"])
def add_page(): 
    if "title" not in request.json:
        raise RequiredArgument("title", request.json)
    if "text" not in request.json:
        raise RequiredArgument("text", request.json)

@app.route("/pages", methods=["GET"])
def list_pages(): 
    raise NotImplementedError()

@app.route('/pages/<string:page>', methods=['GET'])
def get_page():
    raise NotImplementedError()

@app.route('/pages/<string:page>/versions', methods=['GET'])
def get_page_versions():
    raise NotImplementedError()

@app.route('/pages/<string:page>', methods=['PUT'])
def edit_page():
    raise NotImplementedError()

@app.route('/pages/<string:page>/versions', methods=['PUT'])
def set_page_version():
    raise NotImplementedError()
