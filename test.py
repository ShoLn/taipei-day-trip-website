#測試用老師請忽略此頁
import mysql.connector
db = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="password",
    database="website",
    auth_plugin="mysql_native_password"
)
cursor = db.cursor(dictionary=True,buffered=True)

sql = 'SELECT * FROM `taipei_trip` WHERE `name` LIKE %s LIMIT %s,%s;'
val = ('%'+'sfjskjfsd'+'%', 0, 3)
cursor.execute(sql,val)
ans = cursor.fetchone()
print(ans)

