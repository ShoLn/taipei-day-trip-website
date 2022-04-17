from flask import *
from taipei_day_trip_project.mysql.mysql_db import db
import jwt
from flask import current_app


user_blueprint = Blueprint('user_blueprint', __name__)
##################################################################
############################ Api 使用者 ###########################
##################################################################


@user_blueprint.route('/api/user', methods=['GET', 'POST', 'PATCH', 'DELETE'])
def user():
    # GET方法
    if request.method == 'GET':
        token = request.cookies.get('JWT')
        if token:
            try:
                user_data = jwt.decode(
                    token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
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
        sql = 'INSERT INTO `taipei_trip_member`(`name`, `email`, `password`) VALUES (%s,%s,%s); '
        val = (name, email, password)
        sql_result = db.change(sql, val)
        if sql_result.get("no_mysql_error"):
            return jsonify({'ok': True}), 200

        elif sql_result.get("error"):
            if sql_result.get("error").errno == 1062:
                duplicate_column = sql_result.get(
                    "error").args[1].split(" ")[7][20:-1]
                return jsonify({"error": True,
                                "message": "此 {} 已經有人使用".format(duplicate_column)}), 200
        else:
            return jsonify({'error': True,
                            'message': "伺服器內部錯誤"}), 500

    # PATCH方法 登入
    elif request.method == 'PATCH':
        email = request.json.get('email', None)
        password = request.json.get('password', None)
        sql = 'SELECT * FROM `taipei_trip_member` WHERE `email`= %s AND `password`=%s ;'
        val = (email, password)
        sql_result = db.select(sql, val, one_row=True)
        if sql_result.get("no_mysql_error"):
            if sql_result.get("data") is None:
                return jsonify({"error": True,
                                "message": "EMAIL或密碼錯誤"})

            else:
                res_data = {"ok": True}
                res = make_response(res_data, 200)
                token = jwt.encode({
                    'id': sql_result.get("data").get('id'),
                    'name': sql_result.get("data").get('name'),
                    'email': sql_result.get("data").get('email')
                }, current_app.config['SECRET_KEY'])
                res.set_cookie('JWT', token, httponly=True)
                return res

        else:
            return jsonify({"error": True,
                            "message": "伺服器內部錯誤"}), 500

    # DELETE方法 登出
    elif request.method == "DELETE":
        res_data = {"ok": True}
        res = make_response(res_data)
        res.delete_cookie('JWT')
        return res
