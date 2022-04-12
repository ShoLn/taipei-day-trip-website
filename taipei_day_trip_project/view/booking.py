from flask import *
from taipei_day_trip_project.mysql.mysql_db import db
import jwt
from flask import current_app

booking_blueprint = Blueprint(
    'booking_blueprint', __name__, template_folder='../templates/booking')


@booking_blueprint.route("/booking")
def booking():
    return render_template("booking.html")

#################################################################
########################### Api 預定行程 #########################
#################################################################
@booking_blueprint.route('/api/booking', methods=["GET", "POST", "DELETE"])
def api_booking():
    token = request.cookies.get('JWT')
    user_data = jwt.decode(
        token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
    user_id = user_data.get('id')
    user_name = user_data.get('name')
    user_email = user_data.get('email')
    # GET方法
    if request.method == "GET":
        sql = " SELECT `booking`.`id` AS `booking_id`, `booking`.`attrac_id`, `taipei_trip`.`name` AS `attrac_name`, `taipei_trip`.`address`, `taipei_trip`.`images`,`booking`.`tour_date`, `booking`.`tour_time`, `booking`.`tour_cost` FROM `booking` JOIN `taipei_trip_member` ON `booking`.`user_id` = `taipei_trip_member`.id JOIN `taipei_trip` ON `booking`.`attrac_id` = `taipei_trip`.`id` WHERE `booking`.`user_id` = %s;  "
        val = (user_id,)
        sql_result = db.select(sql, val, one_row=False)
        if sql_result.get("no_mysql_error"):
            res_data = {
                "data": {
                    "user": {
                        "id": user_id,
                        "name": user_name,
                        "email": user_email
                    },
                    "attrac": []
                }
            }
            if len(sql_result.get("data")):
                for dict in sql_result.get("data"):
                    res_data["data"]["attrac"].append({
                        "booking_id": dict["booking_id"],
                        "attrac_id": dict["attrac_id"],
                        "name": dict["attrac_name"],
                        "image": dict["images"].split()[0],
                        "address": dict["address"],
                        "date": dict["tour_date"],
                        "time": dict["tour_time"],
                        "price": dict["tour_cost"]
                    })
                return jsonify(res_data)

            else:
                return jsonify(res_data)

        else:
            return jsonify({"error": True,
                            "message": "伺服器內部錯誤"}), 500

    # POST方法
    if request.method == "POST":
        attrac_id = request.json.get('attrac_id')
        tour_date = request.json.get('tour_date')
        tour_time = request.json.get('tour_time')
        tour_cost = request.json.get('tour_cost')
        sql = ' INSERT INTO `booking`(`user_id`, `attrac_id`, `tour_date`, `tour_time`, `tour_cost`) VALUE(%s, %s, %s, %s, %s); '
        val = (user_id, attrac_id, tour_date, tour_time, tour_cost)
        sql_result = db.change(sql, val)
        
        if sql_result.get("no_mysql_error"):
            return jsonify({'ok': True}), 200

        elif sql_result.get("error"):
            if sql_result.get("error").errno == 1062:
                return jsonify({"error": True,
                                "message": "同一天同個時段只能預定一個行程"}), 412

        else:
            return jsonify({'error': True,
                            'message': "伺服器內部錯誤"}), 500


# API BOOKING DELETE 方法

@booking_blueprint.route('/api/booking/<booking_id>', methods=["DELETE"])
def api_booking_delete(booking_id):
    sql = ' DELETE FROM `booking` WHERE `id` = %s '
    val = (booking_id,)
    sql_result = db.change(sql, val)
    if sql_result.get("no_mysql_error"):
        return jsonify({'ok': True}), 200

    else:
        return jsonify({"error": True,
                        "message": "伺服器內部錯誤"}), 500
