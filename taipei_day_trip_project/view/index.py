from flask import *

index_blueprint = Blueprint(
    'index_blueprint', __name__, template_folder='../templates/index')

@index_blueprint.route("/")
def index():
    return render_template("index.html")