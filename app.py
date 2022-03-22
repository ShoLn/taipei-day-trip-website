from flask import *
from mysql.connector import pooling, Error
import jwt
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
            print(1111)
            cursor.execute(sql, val)
            print(2222)
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


app.run(host='0.0.0.0', port=3000, debug=True)
