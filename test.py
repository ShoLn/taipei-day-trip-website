#測試用老師請忽略此頁
from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return 'yayayay'

app.run(host='0.0.0.0', port=3000)