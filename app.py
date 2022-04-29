from flask import Flask,render_template,request,session,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from datetime import datetime
#from werkzeug import secure_filename
import json,os
import OTP_SEND

with open('config.json', 'r') as c:
    params = json.load(c)["params"]


app = Flask(__name__)
app.config['UPLOAD_FILE'] = params['image_uploder']
app.secret_key = "super-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
send = OTP_SEND.Otp_send()
db = SQLAlchemy(app)

app.config.update(
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = '465',
    MAIL_USE_SSL = True,
    MAIL_USE_TLS = False, 
    MAIL_USERNAME = params['gmail-user'],
    MAIL_PASSWORD=  params['gmail-password']
     

)
mail = Mail(app)

class contacts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=False)
    message = db.Column(db.String(120), unique=False, nullable=False)

class Menu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    price = db.Column(db.String(120), unique=False, nullable=False)
    image = db.Column(db.String(120), unique=False, nullable=False)
    flavor = db.Column(db.String(120), unique=False, nullable=False)
    size = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=False)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    c_name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(120), unique=False, nullable=False)
    phone = db.Column(db.String(12), unique=False, nullable=False)
    a_phone = db.Column(db.String(12), unique=False, nullable=False)
    p_name = db.Column(db.String(120), unique=False, nullable=False)
    date = db.Column(db.String(120), unique=False, nullable=False)
    address = db.Column(db.String(200), unique=False, nullable=False)

@app.route("/")
def index():
    data = Menu.query.all()
    return render_template("index.html",data=data)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/menu")
def menu():
    data = Menu.query.all() 
    return render_template("menu.html",data=data)

@app.route("/contact",methods=['GET','POST'])
def contact():
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = contacts(name=name ,email=email,phone=phone,message=message,date= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,
						  sender=email,
						  recipients=[params['gmail-user']],
						  body=message + "\n" + phone
						  )

    return render_template("contact.html")

@app.route('/dashboard',methods = ['GET','POST'])
def login():
    if 'user' in session and session['user'] == params['uname']:
        data = Menu.query.all()
        return render_template("dashboard.html",params=params,data=data)

    if request.method == 'POST':
        uname = request.form.get('uname')
        password = request.form.get('pass')
        if(uname == params['uname'] and password == params['pass']):
            session['user'] = uname
            data = Menu.query.all()
            return render_template("dashboard.html",params=params,data=data)
        else:
            return "your user name and password should be a wrong."
    else:
        return render_template("login.html",params=params)

@app.route('/edit/<string:id>',methods = ['GET','POST'])
def edit(id):
    if 'user' in session and session['user'] == params['uname']:
        if request.method == 'POST':
            name = request.form.get('name')
            price = request.form.get('price')
            image = request.form.get('image')
            flavor = request.form.get('flavor')
            size = request.form.get('size')
            date = datetime.now()
            if id == '0':
                post = Menu(name =name,price=price,image=image,date=date,flavor=flavor,size=size)
                db.session.add(post)
                db.session.commit()
            else:
                datas = Menu.query.filter_by(id=id).first()
                datas.name = name
                datas.price = price
                datas.image = image
                datas.flavor = flavor
                datas.size = size
                db.session.commit()
                return redirect('/edit/' + id)
        data = Menu.query.filter_by(id=id).first()
        return render_template("edit.html",params = params,id=id,data=data)
    else:
        return render_template("login.html",params=params)

@app.route("/order/<string:id>",methods=["GET","POST"])
def order(id):
    if request.method == "POST":
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        aphone = request.form.get('aphone')
        pname = request.form.get('pname')
        address = request.form.get('address')
        date = datetime.now()
        go = Order(c_name=name,email=email,phone=phone,a_phone=aphone,p_name=pname,date=date,address=address)
        db.session.add(go)
        db.session.commit()

        return redirect("/otp/"+id)
    data = Menu.query.filter_by(id=id).first()
    return render_template("order.html",id=id,data=data)

@app.route('/logout')
def logout():
	session.pop('user')
	return redirect('/')

@app.route('/uploader',methods = ['GET','POST'])
def upload():
	if 'user' in session and session['user'] == params['uname']:
		if (request.method == "POST"):
			f = request.files['file']
			f.save(os.path.join(app.config['UPLOAD_FILE'], secure_filename(f.filename)))
			return "image Upload successfully"

@app.route('/delete/<string:id>',methods = ['GET','POST'])
def delete(id):
	if 'user' in session and session['user'] == params['uname']:
		posts = Menu.query.filter_by(id=id).first()
		db.session.delete(posts)
		db.session.commit()
	return redirect('/dashboard')

@app.route('/delete1/<string:id>',methods = ['GET','POST'])
def delete1(id):
	if 'user' in session and session['user'] == params['uname']:
		posts = Order.query.filter_by(id=id).first()
		db.session.delete(posts)
		db.session.commit()
	return redirect('/dashboard_view')

@app.route('/food/<string:id>')
def food(id):
    data = Menu.query.filter_by(id=id).first()
    return render_template("food.html",data=data,id=id)

@app.route('/otp/<string:id>',methods=["GET","POST"])
def otp(id):
    if request.method == "POST":
        name = request.form.get('otp')
        if name == send:
            data1 = Order.query.filter_by(id=id).first()
            return render_template("confirm.html",d1=data1)
        else:
            return "Enter a Valid Otp !!!"
    data = Order.query.filter_by(id=id).first()
    return render_template("otp.html",data=data,id=id)

@app.route('/dashboard_view',methods = ['GET','POST'])
def dashboard_view():
    if 'user' in session and session['user'] == params['uname']:
        data = Order.query.all()
        return render_template("order_dashboard.html",params=params,data=data)

    else:
        return render_template("login.html",params=params)


@app.route("/view/<string:id>")
def view(id):
    if 'user' in session and session['user'] == params['uname']:
        data = Order.query.filter_by(id=id).first()
        return render_template("view.html",data=data,id=id)

if __name__ == "__main__":
    app.run(debug=True)