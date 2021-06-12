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
    return render_template("index.html")

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

        userinfo = {'user_name':username, 'user_password':password}

        if not (username and password and passwordcheck):
            flash("모두 입력해주세요")
            return redirect(url_for('register'))

        elif password != passwordcheck:
            flash("비밀번호를 확인해 주세요")
            return redirect(url_for('register'))

        else:
            DB.users.insert_one(userinfo)
            return redirect(url_for('login'))
    else:
        return render_template('register.html')

@app.route('/diary/<diaryId>', methods=['GET'])
def show_diary(diaryId):
    diary = DB.diaries.find_one({'_id' : diaryId})
    # TODO: diary 보기 페이지 구현

@app.route('/diary/add', methods=['GET', 'POST'])
def add_diary():
    if 'username' not in session:
        return render_template('index.html')
    if request.method == 'POST':
        f = request.files['file']
        # filename = secure_filename(f.filename)
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

@app.route("/diary/edit/<diaryId>")
def edit_diary(diaryId):
    diary = DB.diaries.find_one({"_id": ObjectId(diaryId)})
    if session['username'] == diary["name"]:
        return render_template('update.html', diary = diary)
    else:
        flash("삭제 권한이 없습니다.")
    return redirect(url_for('index'))


@app.route("/diary/delete/<diaryId>")
def delete_diary(diaryId):
    diary = DB.diaries.find_one({"_id": ObjectId(diaryId)})
    if session['username'] == diary["name"]:
        DB.diaries.delete_one({"_id": ObjectId(diaryId)})
        flash("삭제 되었습니다.")
    else:
        flash("삭제 권한이 없습니다.")
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)