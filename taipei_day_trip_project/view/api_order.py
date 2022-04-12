from flask import *
from taipei_day_trip_project.mysql.mysql_db import db
import requests as py_req

order_blueprint = Blueprint('order_blueprint', __name__)

#################################################################
########################### Api 訂單付款 #########################
#################################################################
@order_blueprint.route('/api/orders', methods=["POST"])
def api_orders():
    # api orders POST
    user_id = request.json["user"]["user_id"]
    contact_name = request.json["user"]["contact_name"]
    contact_email = request.json["user"]["contact_email"]
    contact_phone = request.json["user"]["contact_phone"]
    all_booking_id = request.json["order"]["all_booking_id"]
    total_price = request.json["order"]["total_price"]
    prime = request.json["prime"]
    attrac_id = []
    tour_date = []
    tour_time = []
    tour_cost = []

    for booking_id in all_booking_id.split(','):
        sql = 'SELECT * FROM `booking` WHERE `id` = %s;'
        val = (booking_id,)
        sql_result = db.select(sql, val, one_row=True)

        if sql_result.get("no_mysql_error"):
            book_data = sql_result.get("data")
            attrac_id.append(book_data["attrac_id"])
            tour_date.append(book_data["tour_date"])
            tour_time.append(book_data["tour_time"])
            tour_cost.append(book_data["tour_cost"])

        else:
            return jsonify({"error": True, "message": "伺服器錯誤"}), 500

    attrac_id = " ".join(str(e) for e in attrac_id)
    tour_date = " ".join(str(e) for e in tour_date)
    tour_time = " ".join(str(e) for e in tour_time)
    tour_cost = " ".join(str(e) for e in tour_cost)

    # 打api到tappay 後端

    url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
    header = {
        "Content-Type": "application/json",
        "x-api-key": "partner_oM6ZkSqDG3fZ0u3aPyqOyoPEXwfK7j8jBX5YK3TfU0bcqHhd3YDkqUlm"
    }
    data = {
        "prime": prime,
        "partner_key": "partner_oM6ZkSqDG3fZ0u3aPyqOyoPEXwfK7j8jBX5YK3TfU0bcqHhd3YDkqUlm",
        "merchant_id": "ShoLn_CTBC",
        "details": "TapPay Test",
        "amount": total_price,
        "cardholder": {
            "phone_number": str(contact_phone),
            "name": contact_name,
            "email": contact_email,
            "zip_code": "",
                        "address": "",
                        "national_id": ""
        },
        "remember": True
    }
    res_tp = py_req.post(url, headers=header, json=data)
    res_tp_status = res_tp.json()["status"]

    # 若付款成功
    if res_tp_status == 0:
        sql = """
                INSERT INTO `orders`
                (`user_id`, `contact_name`, `contact_email`, 
                `contact_phone`, `total_price`, `attrac_id`,
                `tour_date`, `tour_time`, `tour_cost`,`payment`) 
                VALUE (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
               """
        val = (user_id, contact_name, contact_email,
               contact_phone, total_price, attrac_id,
               tour_date, tour_time, tour_cost, 0)

        sql_result = db.change(sql, val)

        if sql_result.get("no_mysql_error"):
            for booking_id in all_booking_id.split(','):
                sql = 'DELETE FROM `booking` WHERE `id` = %s;'
                val = (booking_id,)
                sql_result = db.change(sql, val)

                if sql_result.get("no_mysql_error"):
                    sql = """
                    SELECT `order_id` FROM `orders` WHERE
                    `attrac_id` = %s AND
                    `tour_date` = %s AND
                    `tour_time` = %s AND
                    `user_id` = %s;    
                    """
                    val = (attrac_id, tour_date, tour_time, user_id)
                    sql_result = db.select(sql, val, one_row=True)

                    if sql_result.get("no_mysql_error"):
                        order_id = sql_result.get("data")["order_id"]
                        return jsonify({
                            "data": {
                                "number": order_id,
                                "payment": {
                                    "status": 0,
                                    "message": "付款成功"
                                }
                            }
                        }), 200
                    else:
                        return jsonify({"error": True, "message": "伺服器錯誤"}), 500
                else:
                    return jsonify({"error": True, "message": "伺服器錯誤"}), 500
        else:
            return jsonify({"error": True, "message": "伺服器錯誤"}), 500
    # 若付款失敗
    else:
        return jsonify({"error": True, "message": "付款失敗"}), 500


#################################################################
########################### Api 取得訂單資料 #########################
#################################################################
@order_blueprint.route('/api/order/<orderNumber>', methods=["GET"])
def api_order(orderNumber):
    # api order GET
    order_id = orderNumber
    sql = "SELECT * FROM `orders` WHERE `order_id` = %s; "
    val = (order_id,)
    sql_result = db.select(sql, val, one_row=True)

    if sql_result.get("no_mysql_error"):
        order_dic = sql_result.get("data")
        attraction = []
        for i in range(len(order_dic["attrac_id"].split())):
            sql = ' SELECT `name`,`address`,`images` FROM `taipei_trip` WHERE `id`=%s'
            val = (order_dic["attrac_id"].split()[i],)
            sql_result = db.select(sql, val, one_row=True)

            if sql_result.get("no_mysql_error"):
                taipei_trip_data = sql_result.get("data")
                name = taipei_trip_data["name"]
                address = taipei_trip_data["address"]
                image = taipei_trip_data["images"].split()[0]
                order_obj = {
                    "attrac_id": order_dic["attrac_id"].split()[i],
                    "name": name,
                    "address": address,
                    "image": image,
                    "date": order_dic["tour_date"].split()[i],
                    "time": order_dic["tour_time"].split()[i]
                }
                attraction.append(order_obj)

            else:
                return jsonify({"error": True,
                                "message": "伺服器內部錯誤"}), 500
        return jsonify({
            "data": {
                "number": order_id,
                "price": order_dic["total_price"],
                "attraction": attraction,
                "contact": {
                    "name": order_dic["contact_name"],
                    "email": order_dic["contact_email"],
                    "phone": order_dic["contact_phone"]
                },
                "status": order_dic["payment"]
            }
        }), 200

    else:
        return jsonify({"error": True,
                        "message": "伺服器內部錯誤"}), 500
