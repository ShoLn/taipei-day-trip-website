from flask import *
from taipei_day_trip_project.mysql.mysql_db import db

attraction_blueprint = Blueprint(
    'attraction_blueprint', __name__, template_folder='../templates/attraction')


@attraction_blueprint.route("/attraction/<id>")
def attraction(id):
    return render_template("attraction.html")


#################################################################################
########################### Api 旅遊景點-取得景點資料列表 ###########################
#################################################################################

@attraction_blueprint.route("/api/attractions")
def get_trip():
    error_dict = {
        "error": True,
        "message": None
    }

    page = int(request.args.get('page', 0))
    keyword = request.args.get('keyword', "")
    sql = 'SELECT COUNT(*) FROM `taipei_trip` WHERE `name` LIKE %s ;'
    val = ("%" + keyword + "%",)
    sql_result = db.select(sql,val,one_row=True)
    
    if sql_result["no_mysql_error"]:
        count = int(sql_result["data"]['COUNT(*)'])
        if count == 0:
            error_dict['message'] = '找不到符合關鍵字的資料'
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
            res = make_response(jsonify(error_dict))
            res.headers["Content-Type"] = "application/json"
            return res
        elif page == all_page:
            sql = 'SELECT * FROM `taipei_trip` WHERE `name` LIKE %s LIMIT %s,%s ;'
            val = ("%" + keyword + "%", page * 12, last_page_number)
            sql_result = db.select(sql,val,one_row=False)

            if sql_result["no_mysql_error"]:
                for trip in sql_result["data"]:
                    trip['images'] = trip['images'].split(' ')
                ans_dict = {
                    'nextPage': None,
                    'data': sql_result["data"]
                }
                res = make_response(jsonify(ans_dict))
                res.headers["Content-Type"] = "application/json"
                return res
        else:
            sql = 'SELECT * FROM `taipei_trip` WHERE `name` LIKE %s LIMIT %s,%s ;'
            val = ("%" + keyword + "%", page * 12, 12)
            sql_result = db.select(sql,val,one_row=False)

            for trip in sql_result["data"]:
                trip['images'] = trip['images'].split(' ')

            ans_dict = {
                'nextPage': page + 1,
                'data': sql_result["data"]
            }
            res = make_response(jsonify(ans_dict))
            res.headers["Content-Type"] = "application/json"
            return res

#################################################################################
########################### Api 旅遊景點-根據景點編號取得景點資料 ####################
#################################################################################


@attraction_blueprint.route('/api/attraction/', defaults={'attractionid': '1'})
@attraction_blueprint.route('/api/attraction/<path:attractionid>')
def id_get_trip(attractionid):
    error_dict = {
        "error": True,
        "message": None
    }
    
    sql = 'SELECT * FROM `taipei_trip` WHERE `id` = %s ;'
    val = (attractionid,)
    sql_result = db.select(sql,val,one_row=True)
    
    if sql_result["data"] is None:
        error_dict['message'] = '找不到符合此id編號的資料'
        res = make_response(jsonify(error_dict))
        res.headers["Content-Type"] = "application/json"
        return res
    else:
        sql_result["data"]['images'] = sql_result["data"]['images'].split(' ')
        ans_dict = {
            'data': sql_result["data"]
        }
        res = make_response(jsonify(ans_dict))
        res.headers["Content-Type"] = "application/json"
        return res