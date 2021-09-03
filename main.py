from operator import pos
import re
from flask import Flask, render_template,request,session,redirect

from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
#from flask_mail import Mail
import math
from werkzeug.utils import secure_filename
import os

import json
import pymysql
pymysql.install_as_MySQLdb()



with open('config.json','r') as c:
    params=json.load(c)["params"]
local_server=True
app=Flask(__name__)
app.secret_key='super-secret-key'

#to send email
# app.config.update(
#     MALI_SERVER='smtp.gmail.com',
#     MAIL_PORT='465',
#     MAIL_USE_SSL=True,
#     MAIL_USERNAME=params['gmail_user'],
#     MAIN_PASSWORD=params['gmail_pass']
#     )
# mail=Mail(app)


# uploading for file
app.config['UPLOAD_FOLDER']=params['upload_location']




if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db=SQLAlchemy(app)


class Contacts(db.Model):
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False)
    message= db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=True)
    sno = db.Column(db.Integer, primary_key=True)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    date = db.Column(db.String, nullable=True)
    slug = db.Column(db.Integer, primary_key=True)

@app.route("/")
def home():
    #pagination logic
    posts=Posts.query.filter_by().all()
    last=math.ceil(len(posts)/int(params['no_of_posts']))
    #posts=posts[]

    page=request.args.get('page')
    if(not str(page).isnumeric()):
        page=1
    page=int(page)
    post= posts[(page-1)*int(params['no_of_posts']):(page-1)*int(params['no_of_posts'])+ int(params['no_of_posts'])]
    if(page==1):
        prev="#"
        next="/?page="+str(page+1)
    elif(page==last):
        prev="/?page="+str(page-1)
        next="#"
    else:
        prev="/?page="+str(page-1)
        next="/?page="+str(page+1)

    posts = Posts.query.filter_by().all()
    return render_template('index.html',params=params,posts=post,prev=prev,next=next)

@app.route("/about")
def about():
    return render_template('public/about.html',params=params)

@app.route("/contact", methods=['GET','POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')

        entry=Contacts(name=name,email=email,phone=phone,message=message, date=datetime.now())

        db.session.add(entry)
        db.session.commit()

        #to send email
        #mail.send_message('New Message from '+name,sender=email,recipients=[params['gmail_user']],body=message+"\n"+phone)


    return render_template('public/contact.html',params=params)

@app.route("/post/<string:post_slug>",methods=['GET'])
def post_route(post_slug):
    post=Posts.query.filter_by(slug=post_slug).first()
    return render_template('public/post.html',params=params,post=post)


# admin part
@app.route("/dashboard",methods=['GET','POST'])
def dashboard():
    if ('user' in session and session['user']==params['admin_user']):
        posts=Posts.query.all()
        return render_template('admin/dashboard.html',params=params,posts=posts)
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pass')
        if(username==params['admin_user'] and password==params['admin_password']):
            session['user']=username
            posts=Posts.query.all()
            return render_template('admin/dashboard.html',params=params,posts=posts)

    return render_template('admin/login.html',params=params)

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if ('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            box_title=request.form.get('title')
            box_slug=request.form.get('slug')
            box_content=request.form.get('content')
            date=datetime.now()

            if(sno!='0'):
            #     post=Posts(title=box_title,content=box_content,date=date,slug=box_slug)
            #     db.session.add(post)
            #     db.session.commit()
            # else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=box_slug
                post.content=box_content
                post.date=date
                db.session.commit()
                return redirect('/dashboard')
        post=Posts.query.filter_by(sno=sno).first()
        return render_template('admin/edit.html',params=params,post=post)

@app.route("/add/<string:sno>",methods=['GET','POST'])
def add(sno):
    if ('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            box_title=request.form.get('title')
            box_slug=request.form.get('slug')
            box_content=request.form.get('content')
            date=datetime.now()

            if(sno=='0'):
                post=Posts(title=box_title,content=box_content,date=date,slug=box_slug)
                db.session.add(post)
                db.session.commit()
                return redirect('/dashboard')
        return render_template('admin/add.html',params=params,sno=sno)


@app.route("/upload",methods=['POST','GET'])
def upload():
    if ('user' in session and session['user']==params['admin_user']):
        if(request.method=='POST'):
            f=request.files['file']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'],secure_filename(f.filename)))
            return "Updated Successfully"

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if ('user' in session and session['user']==params['admin_user']):
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/dashboard')




app.run(debug=True)
