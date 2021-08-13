from flask import Flask, render_template,url_for, request, session, redirect
import sqlite3
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key='voat'

create_table="create table if not exists users ( username varchar(255), password varchar(255))"
conn=sqlite3.connect("database.db")
cur=conn.cursor()
cur.execute(create_table)
conn.commit()

@app.route('/')
def home():
    return render_template("landingpage.html")


@app.route('/linksaver')
def linksaver():
    if session['username']:
        conn=sqlite3.connect("database.db")
        cur=conn.cursor()
        resdata=cur.execute("select linkname,thelink,username,ROWID from links where username=?",(session['username'],))
        return render_template("index.html",resdata=resdata)
    else:
        return redirect("/")
    
@app.route('/login')
def loginpage():
    return render_template("login.html")

@app.route('/signup')
def signuppage():
    return render_template("signup.html")

@app.route('/process_signup', methods=["POST"])
def signup():
    username=request.form['usrname']
    password=request.form['pswrd']
    conn=sqlite3.connect("database.db")
    cur=conn.cursor()

    usrs=cur.execute("select * from users where username=?",(username,))
    if len(list(usrs))==1:
        return "username already taken"
    else:
        cur.execute("insert into users (username, password) values(?,?)",(username,password))
        conn.commit()
        return render_template("login.html",)

@app.route('/process_login', methods=["POST"])
def login():
    error=False
    username=request.form['usrname']
    password=request.form['pswrd']
    conn=sqlite3.connect("database.db")
    cur=conn.cursor()
    res=cur.execute("select * from users where username=? and password=?",(username,password))
    if len(list(res))>=1:
        session['username']=username
        return redirect(url_for("linksaver"))
    else:
        error=True
        return render_template("login.html",error=error)


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('home'))

@app.route('/newlink', methods=['POST'])
def newlink():
    if session['username']:
        if request.method== "POST":
           try:
            linkerror=False
            flag=False
            thelink=request.form['thelink']
            linkname=""
            flag="an error occured, please try again"
            page=requests.get(thelink)
            soup=BeautifulSoup(page.text,'html.parser')
            linkname=soup.title.get_text()
            conn=sqlite3.connect("database.db")
            cur=conn.cursor()
            res=cur.execute("insert into links (linkname,thelink,username) values(?,?,?)",(linkname,thelink,session['username']))
            conn.commit()
            return redirect(url_for("linksaver"))
           except requests.exceptions.MissingSchema:
            linkerror=True
            return render_template("index.html",linkerror=linkerror)
           except:
            flag=True
            return render_template("index.html",flag=flag)
    else:
         return redirect("/login")


@app.route('/deletelink/<id>', methods=['GET','POST'])
def deletelink(id):
    conn=sqlite3.connect("database.db")
    cur=conn.cursor()
    res=cur.execute("delete from links where ROWID=?",(id,))
    conn.commit()
    return redirect(url_for("linksaver"))

if __name__ == '__main__':
    app.run(debug=True)
