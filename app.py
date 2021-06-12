from flask import Flask, render_template, session, request, url_for, redirect, flash
from bson.objectid import ObjectId
from db import mongodb
from flask_pymongo import PyMongo
import datetime

DB = mongodb()
app = Flask(__name__)
app.secret_key = 'software_engineering'
app.config['MONGO_URI'] = "mongodb+srv://yonghee:dydgml2514@cluster0.zer9c.mongodb.net/software_engineering?retryWrites=true&w=majority"
storage = PyMongo(app)

@app.route('/')
def index():
    if 'username' in session:
        diaries = DB.diaries.find().sort('created_time', -1)
        return render_template("main.html", diaries = diaries)
    return redirect(url_for('login'))
@app.route('/main')
def main():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = DB.users.find_one({'user_name':username, 'user_password':password})
        if user is None:
            flash("ID와 비밀번호를 확인해 주세요")
            return redirect(url_for('login'))
        session['username'] = username
        session['password'] = password
        session['logged_in'] = True
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
   session.pop('username', None)
   session['logged_in'] = False
   return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        passwordcheck = request.form['passwordcheck']
        user = DB.users.find_one({'user_name':username})
        if user:
            flash("이미 존재하는 ID입니다")
            return redirect(url_for('register'))
        if not (username and password and passwordcheck):
            flash("모두 입력해주세요")
            return redirect(url_for('register'))
        if password != passwordcheck:
            flash("비밀번호를 확인해 주세요")
            return redirect(url_for('register'))
        DB.users.insert_one({'user_name':username, 'user_password':password})
        return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/diary/<diaryId>', methods=['GET'])
def show_diary(diaryId):
    diary = DB.diaries.find_one({'_id' : ObjectId(diaryId)})
    return render_template('detail.html', diary = diary)

@app.route('/diary/add', methods=['GET', 'POST'])
def add_diary():
    if 'username' not in session:
        return render_template('login.html')
    if request.method == 'POST':
        f = request.files['file']
        storage.save_file(f.filename, f)
        post = {
            "name": session['username'],
            "title": request.form['title'],
            "content": request.form['content'],
            "created_time": datetime.datetime.now(),
            "filename": f.filename
        }
        DB.diaries.insert_one(post)
        return redirect(url_for('index'))
    else:
        return render_template('write.html')

@app.route("/diary/edit/<diaryId>", methods = ['GET', 'POST'])
def edit_diary(diaryId):
    diary = DB.diaries.find_one({"_id": ObjectId(diaryId)})
    former_filename = diary["filename"]
    if session['username'] == diary["name"]:
        if request.method == 'POST':
            f = request.files['file']
            if f.filename != former_filename and f.filename != "":
                storage.save_file(f.filename, f)
                DB.diaries.update_one({'_id': ObjectId(diaryId)}, {'$set': {
                    "title": request.form['title'],
                    "content": request.form['content'],
                    "filename": f.filename
                }})
            else:
                DB.diaries.update_one({'_id': ObjectId(diaryId)}, {'$set': {
                    "title": request.form['title'],
                    "content": request.form['content']
                }})
        else:
            return render_template('update.html', diary = diary)
    else:
        flash("수정 권한이 없습니다.")
    return redirect(url_for('index'))


@app.route("/diary/delete/<diaryId>")
def delete_diary(diaryId):
    diary = DB.diaries.find_one({"_id": ObjectId(diaryId)})
    if session['username'] == diary["name"]:
        DB.diaries.delete_one({"_id": ObjectId(diaryId)})
    else:
        flash("삭제 권한이 없습니다.")
    return redirect(url_for('index'))


@app.route("/diary/showimage/<filename>")
def show_image(filename):
    return storage.send_file(filename)

if __name__ == "__main__":
    app.run(debug=True)