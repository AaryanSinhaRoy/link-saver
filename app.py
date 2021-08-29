from flask import Flask, render_template,url_for, request, session, redirect
from flask_sqlalchemy import SQLAlchemy

import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
app.secret_key='boat'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///saverdb.db'
app.config['SECRET_KEY'] = "boat"
db=SQLAlchemy(app)

class users(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    username=db.Column(db.String(100),nullable=False)
    password=db.Column(db.String(100),nullable=False)


class links(db.Model):
    id=db.Column(db.Integer(),primary_key=True)
    linkname=db.Column(db.String(100),nullable=False)
    thelink=db.Column(db.String(100),nullable=False)
    username=db.Column(db.String(100),nullable=False)


@app.route('/')
def home():
    #if session['username']:
        #return redirect("/linksaver")
    #else:
    return render_template("landingpage.html")


@app.route('/linksaver')
def linksaver():
    if session['username']:
        resdata=links.query.filter_by(username=session['username']).all()
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
    conf_pswrd_error=False
    username=request.form['usrname']
    password=request.form['pswrd']
    conf_password=request.form['conf-pswrd']
    isusername=""
    checkpassword=""
    if conf_password != password:
        conf_pswrd_error=True
        return render_template("signup.html",conf_pswrd_error=conf_pswrd_error)
    
    else:
        res=users.query.filter_by(username=username).first()
        
        if res:
            return "username already taken"
        else:
            linky=users(username=username,password=password)
            db.session.add(linky)
            db.session.commit()
            return redirect(url_for("loginpage"))

@app.route('/process_login', methods=["POST"])
def login():
    error=False
    username=request.form['usrname']
    password=request.form['pswrd']
    resdata = users.query.filter_by(password=password).first()
    if resdata:
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
            linkerror=False
            flag=False
            thelink=request.form['thelink']
            linkname=""
            try:
                page=requests.get(thelink)
                soup=BeautifulSoup(page.text,'html.parser')
                linkname=soup.title.get_text()
               
                newlink=links(linkname=linkname,thelink=thelink,username=session['username'])
                db.session.add(newlink)
                db.session.commit()
                return redirect(url_for("linksaver"))
            except requests.exceptions.MissingSchema:
                thelink="http://"+thelink
                page=requests.get(thelink)
                soup=BeautifulSoup(page.text,'html.parser')
                linkname=soup.title.get_text()
                newlink=links(linkname=linkname,thelink=thelink,username=session['username'])
                db.session.add(newlink)
                db.session.commit()
                return redirect(url_for("linksaver"))
            
    else:
         return redirect("/login")


@app.route('/deletelink/<id>', methods=['GET','POST'])
def deletelink(id):
    linkdelete=links.query.filter_by(id=id).first()
    db.session.delete(linkdelete)
    db.session.commit()
    return redirect(url_for("linksaver"))


@app.route('/changepassword')
def changepassword():
    return render_template("change-password.html")

@app.route('/change-password',methods=['GET','POST'])
def change_password():
    conf_pswrd_error=False
    old_pswrd_error=False
    if request.method=="POST":
        old_password=request.form['oldpswrd']
        new_password=request.form['newpswrd']
        conf_password=request.form['conf-pswrd']
        resdata=users.query.filter_by(username=session['username']).all()
        for x in resdata:
            if str(x.password) == str(old_password):
                if new_password==conf_password:
                    x.password=new_password
                    db.session.commit()
                    return redirect(url_for("logout"))
                else:
                    conf_pswrd_error=True
                    return render_template("change-password.html",conf_pswrd_error=conf_pswrd_error)
            else:
                old_pswrd_error=True
                return render_template("change-password.html",old_pswrd_error=old_pswrd_error)



@app.route('/admin',methods=["GET","POST"])
def admin():
    error=False
    admin_password="randompassword"
    if request.method=="POST":
        adminpass=request.form['admin-password']
        if str(adminpass)==str(admin_password):
            session['logged_in']=True
            logged_in=session['logged_in'] 

            return redirect("/admin-dashboard")
        else:
            error=True
            return render_template("admin.html",error=error)
    else:
        return render_template("admin.html")

@app.route('/admin-dashboard')
def admin_dashboard():
    if session['logged_in']:
        allusers=users.query.all()
        return render_template("admin-dashboard.html",allusers=allusers)
    else:
        return redirect("/admin")

@app.route('/deleteuser/<id>')
def deleteuser(id):
    userdelete=users.query.filter_by(id=id).first()
    db.session.delete(userdelete)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route('/admin-logout')
def admin_logout():
    session['logged_in']=False
    session.pop("logged_in")
    return redirect(url_for("home"))


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)