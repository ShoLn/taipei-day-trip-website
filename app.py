from flask import *
from mysql.connector import pooling
app=Flask(__name__)
app.config["JSON_AS_ASCII"]=False
app.config["TEMPLATES_AUTO_RELOAD"]=True
app.config['JSON_SORT_KEYS'] = False

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


# Api 旅遊景點-取得景點資料列表
@app.route("/api/attractions")
def get_trip():
    error_dict = {
        "error": True,
        "message": None
        }

    page = int(request.args.get('page',0))
    keyword = request.args.get('keyword',"")
    cnt_pool_obj = pool_object.get_connection()
    cursor = cnt_pool_obj.cursor(dictionary=True,buffered=True)
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

    count_div = divmod(count,12)

    if count_div[1] == 0:
        all_page = count_div[0] - 1 
        last_page_number = 0
    else :
        all_page = count_div[0] 
        last_page_number = count_div[1]
    
    if page > all_page :
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

# Api 旅遊景點-根據景點編號取得景點資料
@app.route('/api/attraction/', defaults={'attractionid':'1'})
@app.route('/api/attraction/<path:attractionid>')
def id_get_trip(attractionid):
    error_dict = {
    "error": True,
    "message": None
    }
    cnt_pool_obj = pool_object.get_connection()
    cursor = cnt_pool_obj.cursor(dictionary=True,buffered=True)
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
        select_data_dict['images'] =  select_data_dict['images'].split(' ')
        ans_dict = {
            'data': select_data_dict
        }
        cursor.close()
        cnt_pool_obj.close()
        res = make_response(jsonify(ans_dict))
        res.headers["Content-Type"] = "application/json"
        return res





app.run(host='0.0.0.0', port=3000)