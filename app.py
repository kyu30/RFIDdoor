from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

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
    data = request.json
    uid = data.get("UID", '').strip().upper()
    name = data.get("User", '').strip()
    access = data.get("Permission", '').strip()
    time = data.get("Last Used", '').strip()
    if uid and name and access and time:
        df.loc[uid] = [name, access, time]
        df.to_csv(whitelist)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

@app.route('/delete_entry', methods=['POST'])
def delete_entry():
    data = request.json
    uid = data.get('UID', '').strip().upper()

    if uid in df.index:
        df.drop(uid, inplace = True)
        df.to_csv(whitelist)
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error'}), 400

if __name__ == '__main__':
    app.run(debug = True)