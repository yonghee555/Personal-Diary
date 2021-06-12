from flask import Flask, render_template, session, request, url_for, redirect, flash
from db import mongodb

DB = mongodb()

app = Flask(__name__)
app.secret_key = 'software_engineering'

@app.route('/')
def index():
	if 'username' in session:
		return render_template("main.html")
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

@app.route('/diary/add')
def addDiary():
	if 'username' not in session:
		return render_template('index.html')
	# TODO: diary 추가 페이지 구현

if __name__ == "__main__":
	app.run(debug=True)