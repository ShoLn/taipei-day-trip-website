import json
import mysql.connector

with open('taipei-attractions.json') as f:
    alldata = json.load(f)
    data = alldata['result']['results']

name = []
category = []
description = []
address = []
transport = []
mrt = []
latitude = []
longitude = []
images = []

for i in range(0, 58):
    name.append(data[i]['stitle'])
    category.append(data[i]['CAT2'])
    description.append(data[i]['xbody'])
    address.append(data[i]['address'])
    transport.append(data[i]['info'])
    if data[i]['MRT'] is None:
        mrt.append('No Avaible MRT')
    else:
        mrt.append(data[i]['MRT'])
    latitude.append(data[i]['latitude'])
    longitude.append(data[i]['longitude'])
    file = data[i]['file'].split('https://')
    tempImg = []
    for f in file:
        if (f[-4:] == '.jpg') or (f[-4:] == '.JPG'):
            tempImg.append("https://" + f)
        elif (f[-4:] == '.png') or (f[-4:] == '.PNG') :
            tempImg.append("https://" + f)
    tempImgStr = " ".join(tempImg)
    images.append(tempImgStr)

db = mysql.connector.connect(
    host="localhost",
    port="3306",
    user="root",
    password="password",
    database="website",
    auth_plugin="mysql_native_password"
)
cursor = db.cursor()


for i in range(0,58):
    try:
        sql = "INSERT INTO `taipei_trip` (`name`, `category`, `description`, `address`, `transport`, `mrt`, `latitude`, `longitude`, `images`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) " 
        val = (name[i], category[i], description[i], address[i], transport[i], mrt[i], latitude[i], longitude[i], images[i])
        cursor.execute(sql, val)
        db.commit()
    except mysql.connector.Error:
        print(mysql.connector.Error)
        print(i,'has error')
        db.rollback()
        break
cursor.close()
db.close()