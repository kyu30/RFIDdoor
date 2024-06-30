from flask import Flask, request, jsonify, render_template
from datetime import datetime as dt
from datetime import time, date, timedelta
import pandas as pd
import os
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
whitelist = 'whitelist.csv'
if os.path.exists(whitelist):
    df = pd.read_csv(whitelist, index_col = 'UID')
else: 
    df = pd.DataFrame(columns = ['UID', 'Permission','User', 'Last Used']).set_index("UID")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/get_whitelist', methods = ['GET'])
def get_whitelist():
    return jsonify(df.reset_index().to_dict(orient='records'))

@app.route('/add_entry', methods = ["POST"])
def add_entry():
    try:
        data = request.json
        logging.debug(f"Received data for add_entry: {data}")
        if not data:
            logging.debug(f"Received data for add_entry: {data}")
        uid = data.get("uid", '').strip().upper()
        name = data.get("name", '').strip()
        access = data.get("permissions", '').strip()
        time = dt.now()
        if not uid or not name or not access or not time:
                logging.error(f"Invalid data received: {data}")
                return jsonify({'status': 'error', 'message': 'Invalid data received'}), 400
        else:
            df.loc[uid] = [name, access, time]
            print(df)
            df.to_csv(whitelist)
            logging.debug(f"Added entry: {uid}, {name}, {access}, {time}")
            return jsonify({'status': 'success'})
    except Exception as e:
        logging.error(f"Error adding entry: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500
        '''if uid and name and access and time:
            df.loc[uid] = [name, access, time]
            df.to_csv(whitelist)
            logging.debug(f"Added entry: {uid}, {name}, {access}")
            return jsonify({'status': 'success'})
        logging.error(f"Failed to add entry: {uid}, {name}, {access}")
        return jsonify({'status': 'error'}), 400'''

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    uid = data.get('uid', '').strip().upper()

    if uid in df.index:
        df.drop(uid, inplace = True)
        df.to_csv(whitelist)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(debug = True)