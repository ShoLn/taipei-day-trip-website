from flask import *
from taipei_day_trip_project.view.api_order import order_blueprint
from taipei_day_trip_project.view.api_user import user_blueprint
from taipei_day_trip_project.view.attraction import attraction_blueprint
from taipei_day_trip_project.view.booking import booking_blueprint
from taipei_day_trip_project.view.index import index_blueprint
from taipei_day_trip_project.view.thankyou import thankyou_blueprint

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'wehelp'

app.register_blueprint(order_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(attraction_blueprint)
app.register_blueprint(booking_blueprint)
app.register_blueprint(index_blueprint)
app.register_blueprint(thankyou_blueprint)