from crypt import methods
from unicodedata import name
from flask import *
from mysql.connector import pooling, Error
import jwt
import requests as py_req
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'wehelp'

pool_object = pooling.MySQLConnectionPool(
    pool_size=5,
    pool_name='mypoolname',
    pool_reset_session=True,
    host='localhost',
    user='root',
    password='password',
    database='website',
    auth_plugin="mysql_native_password"
)

# Pages


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


@app.route("/booking")
def booking():
    return render_template("booking.html")


@app.route("/thankyou")
def thankyou():
    return render_template("thankyou.html")

#################################################################################
########################### Api 旅遊景點-取得景點資料列表 ###########################
#################################################################################


@app.route("/api/attractions")
def get_trip():
    error_dict = {
        "error": True,
        "message": None
    }

    page = int(request.args.get('page', 0))
    keyword = request.args.get('keyword', "")
    cnt_pool_obj = pool_object.get_connection()
    cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
    sql = 'SELECT COUNT(*) FROM `taipei_trip` WHERE `name` LIKE %s ;'
    val = ("%" + keyword + "%",)
    cursor.execute(sql, val)
    count = int(cursor.fetchone()['COUNT(*)'])

    if count == 0:
        error_dict['message'] = '找不到符合關鍵字的資料'
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(error_dict))
        res.headers["Content-Type"] = "application/json"
        return res

    count_div = divmod(count, 12)

    if count_div[1] == 0:
        all_page = count_div[0] - 1
        last_page_number = 0
    else:
        all_page = count_div[0]
        last_page_number = count_div[1]

    if page > all_page:
        error_dict['message'] = '所選頁數超過總頁數'
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(error_dict))
        res.headers["Content-Type"] = "application/json"
        return res
    elif page == all_page:
        sql = 'SELECT * FROM `taipei_trip` WHERE `name` LIKE %s LIMIT %s,%s ;'
        val = ("%" + keyword + "%", page * 12, last_page_number)
        cursor.execute(sql, val)
        select_data_list_of_dict = cursor.fetchall()
        for trip in select_data_list_of_dict:
            trip['images'] = trip['images'].split(' ')
        ans_dict = {
            'nextPage': None,
            'data': select_data_list_of_dict
        }
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(ans_dict))
        res.headers["Content-Type"] = "application/json"
        return res
    else:
        sql = 'SELECT * FROM `taipei_trip` WHERE `name` LIKE %s LIMIT %s,%s ;'
        val = ("%" + keyword + "%", page * 12, 12)
        cursor.execute(sql, val)
        select_data_list_of_dict = cursor.fetchall()
        for trip in select_data_list_of_dict:
            trip['images'] = trip['images'].split(' ')

        ans_dict = {
            'nextPage': page + 1,
            'data': select_data_list_of_dict
        }
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(ans_dict))
        res.headers["Content-Type"] = "application/json"
        return res
#################################################################################
########################### Api 旅遊景點-根據景點編號取得景點資料 ####################
#################################################################################


@app.route('/api/attraction/', defaults={'attractionid': '1'})
@app.route('/api/attraction/<path:attractionid>')
def id_get_trip(attractionid):
    error_dict = {
        "error": True,
        "message": None
    }
    cnt_pool_obj = pool_object.get_connection()
    cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
    sql = 'SELECT * FROM `taipei_trip` WHERE `id` = %s ;'
    val = (attractionid,)
    cursor.execute(sql, val)
    select_data_dict = cursor.fetchone()
    if select_data_dict is None:
        error_dict['message'] = '找不到符合此id編號的資料'
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(error_dict))
        res.headers["Content-Type"] = "application/json"
        return res
    else:
        select_data_dict['images'] = select_data_dict['images'].split(' ')
        ans_dict = {
            'data': select_data_dict
        }
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(ans_dict))
        res.headers["Content-Type"] = "application/json"
        return res


##################################################################
############################ Api 使用者 ###########################
##################################################################

@app.route('/api/user', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user():
    # GET方法
    if request.method == 'GET':
        token = request.cookies.get('JWT')
        if token:
            try:
                user_data = jwt.decode(
                    token, app.config['SECRET_KEY'], algorithms=["HS256"])
                return jsonify({
                    "data": user_data
                }), 200
            except:
                return jsonify({'null': True})
        return jsonify({'null': True})
    # POST方法 註冊
    elif request.method == 'POST':
        name = request.json.get('name', None)
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        try:
            cnt_pool_obj = pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            sql = 'INSERT INTO `taipei_trip_member`(`name`, `email`, `password`) VALUES (%s,%s,%s); '
            val = (name, email, password)
            cursor.execute(sql, val)
            cnt_pool_obj.commit()
            return jsonify({'ok': True}), 200
        except Error as e:
            if e.errno == 1062:
                duplicate_column = e.args[1].split(" ")[7][20:-1]
                return jsonify({"error": True,
                                "message": "此 {} 已經有人使用".format(duplicate_column)}), 200
        except:
            return jsonify({'error': True,
                            'message': "伺服器內部錯誤"}), 500
        finally:
            cnt_pool_obj.rollback()
            cursor.close()
            cnt_pool_obj.close()
    # PATCH方法 登入
    elif request.method == 'PATCH':
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        try:
            cnt_pool_obj = pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            sql = 'SELECT * FROM `taipei_trip_member` WHERE `email`= %s AND `password`=%s ;'
            val = (email, password)
            cursor.execute(sql, val)
            user_data = cursor.fetchone()
            if user_data is None:
                return jsonify({"error": True,
                                "message": "EMAIL或密碼錯誤"})
            else:
                res_data = {"ok": True}
                res = make_response(res_data, 200)
                token = jwt.encode({
                    'id': user_data.get('id'),
                    'name': user_data.get('name'),
                    'email': user_data.get('email')
                }, app.config['SECRET_KEY'])
                res.set_cookie('JWT', token, httponly=True)
                return res
        except:
            return jsonify({"error": True,
                            "message": "伺服器內部錯誤"}), 500
        finally:
            cnt_pool_obj.rollback()
            cursor.close()
            cnt_pool_obj.close()
    # DELETE方法 登出
    elif request.method == "DELETE":
        res_data = {"ok": True}
        res = make_response(res_data)
        res.delete_cookie('JWT')
        return res


#################################################################
########################### Api 預定行程 #########################
#################################################################
@app.route('/api/booking', methods=["GET", "POST", "DELETE"])
def api_booking():
    token = request.cookies.get('JWT')
    user_data = jwt.decode(
        token, app.config['SECRET_KEY'], algorithms=["HS256"])
    user_id = user_data.get('id')
    user_name = user_data.get('name')
    user_email = user_data.get('email')
    # GET方法
    if request.method == "GET":
        try:
            cnt_pool_obj = pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            sql = " SELECT `booking`.`id` AS `booking_id`, `booking`.`attrac_id`, `taipei_trip`.`name` AS `attrac_name`, `taipei_trip`.`address`, `taipei_trip`.`images`,`booking`.`tour_date`, `booking`.`tour_time`, `booking`.`tour_cost` FROM `booking` JOIN `taipei_trip_member` ON `booking`.`user_id` = `taipei_trip_member`.id JOIN `taipei_trip` ON `booking`.`attrac_id` = `taipei_trip`.`id` WHERE `booking`.`user_id` = %s;  "
            val = (user_id,)
            cursor.execute(sql, val)
            data = cursor.fetchall()
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
            if len(data):
                for dict in data:
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
        except:
            return jsonify({"error": True,
                            "message": "伺服器內部錯誤"}), 500
        finally:
            cnt_pool_obj.rollback()
            cursor.close()
            cnt_pool_obj.close()
    # POST方法
    if request.method == "POST":
        attrac_id = request.json.get('attrac_id')
        tour_date = request.json.get('tour_date')
        tour_time = request.json.get('tour_time')
        tour_cost = request.json.get('tour_cost')

        try:
            cnt_pool_obj = pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            sql = ' INSERT INTO `booking`(`user_id`, `attrac_id`, `tour_date`, `tour_time`, `tour_cost`) VALUE(%s, %s, %s, %s, %s); '
            val = (user_id, attrac_id, tour_date, tour_time, tour_cost)
            cursor.execute(sql, val)
            cnt_pool_obj.commit()
            return jsonify({'ok': True}), 200
        except Error as e:
            if e.errno == 1062:
                cnt_pool_obj.rollback()
                return jsonify({"error": True,
                                "message": "同一天同個時段只能預定一個行程"}), 412
        except:
            cnt_pool_obj.rollback()
            return jsonify({"error": True,
                            "message": "伺服器內部錯誤"}), 500
        finally:
            cursor.close()
            cnt_pool_obj.close()

# API BOOKING DELETE 方法


@app.route('/api/booking/<booking_id>', methods=["DELETE"])
def api_booking_delete(booking_id):
    print(booking_id)
    try:
        cnt_pool_obj = pool_object.get_connection()
        cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
        sql = ' DELETE FROM `booking` WHERE `id` = %s '
        val = (booking_id,)
        cursor.execute(sql, val)
        cnt_pool_obj.commit()
        return jsonify({'ok': True}), 200
    except:
        return jsonify({"error": True,
                        "message": "伺服器內部錯誤"}), 500
    finally:
        cnt_pool_obj.rollback()
        cursor.close()
        cnt_pool_obj.close()

#################################################################
########################### Api 訂單付款 #########################
#################################################################


@app.route('/api/orders', methods=["POST"])
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
    print(all_booking_id.split(','))
    cnt_pool_obj = pool_object.get_connection()
    cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
    for booking_id in all_booking_id.split(','):
        sql = 'SELECT * FROM `booking` WHERE `id` = %s;'
        val = (booking_id,)
        cursor.execute(sql, val)
        book_data = cursor.fetchone()
        attrac_id.append(book_data["attrac_id"])
        tour_date.append(book_data["tour_date"])
        tour_time.append(book_data["tour_time"])
        tour_cost.append(book_data["tour_cost"])
    print("`----------------------------------------")
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
        try:
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
            cursor.execute(sql, val)
            cnt_pool_obj.commit()
            for booking_id in all_booking_id.split(','):
                sql = 'DELETE FROM `booking` WHERE `id` = %s;'
                val = (booking_id,)
                cursor.execute(sql, val)
                cnt_pool_obj.commit()

            sql = """
                    SELECT `order_id` FROM `orders` WHERE
                    `attrac_id` = %s AND
                    `tour_date` = %s AND
                    `tour_time` = %s AND
                    `user_id` = %s;    
                  """
            val = (attrac_id, tour_date, tour_time, user_id)

            cursor.execute(sql, val)
            order_id = cursor.fetchone()["order_id"]
            return jsonify({
                "data": {
                    "number": order_id,
                    "payment": {
                        "status": 0,
                        "message": "付款成功"
                    }
                }
            }), 200
        except:
            cnt_pool_obj.rollback()
            return jsonify({"error": True, "message": "伺服器錯誤"}), 500
        finally:
            cursor.close()
            cnt_pool_obj.close()

    # 若付款失敗
    else:
        cnt_pool_obj.rollback()
        cursor.close()
        cnt_pool_obj.close()
        return jsonify({"error": True, "message": "付款失敗"}), 500


@app.route('/api/order/<orderNumber>', methods=["GET"])
def api_order(orderNumber):
    # api order GET
    order_id = orderNumber
    try:
        cnt_pool_obj = pool_object.get_connection()
        cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
        sql = "SELECT * FROM `orders` WHERE `order_id` = %s; "
        val = (order_id,)
        cursor.execute(sql, val)
        order_dic = cursor.fetchone()
        attraction = []
        for i in range(len(order_dic["attrac_id"].split())):
            sql = ' SELECT `name`,`address`,`images` FROM `taipei_trip` WHERE `id`=%s'
            val = (order_dic["attrac_id"].split()[i],)
            cursor.execute(sql,val)
            taipei_trip_data = cursor.fetchone()
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
    except:
        return jsonify({"error": True,
                        "message": "伺服器內部錯誤"}), 500
    finally:
        cursor.close()
        cnt_pool_obj.close()


app.run(host='0.0.0.0', port=3000, debug=True)
