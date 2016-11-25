from wikiapi.app import app
from flask import jsonify

@app.route("/pages", methods=["POST"])
def add_page(): 
    raise NotImplementedError()

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
