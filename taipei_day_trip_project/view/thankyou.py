from flask import *

thankyou_blueprint = Blueprint(
    'thankyou_blueprint', __name__, template_folder='../templates/thankyou')

@thankyou_blueprint.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")