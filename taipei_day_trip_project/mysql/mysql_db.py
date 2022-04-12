from mysql.connector import pooling, Error


class Db():
    def __init__(self):
        self.pool_object = pooling.MySQLConnectionPool(
            pool_size=5,
            pool_name='mypoolname',
            pool_reset_session=True,
            host='localhost',
            user='root',
            password='password',
            database='website',
            auth_plugin="mysql_native_password"
        )

    def select(self, sql, val, one_row):
        try:
            cnt_pool_obj = self.pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            cursor.execute(sql, val)
            if one_row:
                data = cursor.fetchone()  # return dict, return none if no data
                return {
                    "no_mysql_error": True,
                    "data": data
                }
            else:
                data = cursor.fetchall()  # return list of dict, return empty list if no data
                return {
                    "no_mysql_error": True,
                    "data": data
                }

        except Error as e:
            return {
                "no_mysql_error": False,
                "error": e
            }

        except:
            return {
                "no_mysql_error": False,
            }

        finally:
            cursor.close()
            cnt_pool_obj.close()

    def change(self, sql, val):
        try:
            cnt_pool_obj = self.pool_object.get_connection()
            cursor = cnt_pool_obj.cursor(dictionary=True, buffered=True)
            cursor.execute(sql, val)
            cnt_pool_obj.commit()
            return {
                "no_mysql_error": True
            }

        except Error as e:
            cnt_pool_obj.rollback()
            return {
                "no_mysql_error": False,
                "error": e
            }

        except:
            cnt_pool_obj.rollback()
            return {
                "no_mysql_error": False,
            }

        finally:
            cursor.close()
            cnt_pool_obj.close()


db = Db()
