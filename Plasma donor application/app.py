from flask import Flask, redirect, url_for, render_template, request
from flask_email import Mail, Message
import ibm_db
app = Flask(__name__, static_url_path='/static')

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rsd77088;PWD=LwKz2V6x2Vw4eEy1",'','')


@app.route('/signup')
def signup():
    return render_template("register.html")

@app.route('/register',methods=['POST'])
def register():
    x = [x for x in request.form.values()]
    print(x)
    name=x[0]
    email=x[1]
    phone=x[2]
    city=x[3]
    infect=x[4]
    blood=x[5]
    password=x[6]
    sql = "SELECT * FROM user WHERE email =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,email)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print(account)
    if account:
        return render_template('register.html', pred="You are already a member, please login using your details")
    else:
        insert_sql = "INSERT INTO  user VALUES (?, ?, ?, ?, ?, ?, ?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1, name)
        ibm_db.bind_param(prep_stmt, 2, email)
        ibm_db.bind_param(prep_stmt, 3, phone)
        ibm_db.bind_param(prep_stmt, 4, city)
        ibm_db.bind_param(prep_stmt, 5, infect)
        ibm_db.bind_param(prep_stmt, 6, blood)
        ibm_db.bind_param(prep_stmt, 7, password)
        ibm_db.execute(prep_stmt)
        return render_template('register.html', pred="Registration Successful, please login using your details")
       

@app.route('/')
@app.route('/login')
def home():
    return render_template("login.html")

@app.route('/loginpage',methods=['POST'])
def loginpage():
    user = request.form['email']
    passw = request.form['password']
    sql = "SELECT * FROM user WHERE email =? AND password=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,user)
    ibm_db.bind_param(stmt,2,passw)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)
    print (account)
    print(user,passw)
    if account:
            return redirect(url_for('dashboard'))
    else:
        return render_template('login.html', pred="Login unsuccessful. Incorrect username / password !") 
    
@app.route('/dashboard')
def dashboard():
    sql = "SELECT BLOOD, count(*) as NUM FROM user GROUP BY BLOOD"
    b=0
    b1=0
    b2=0
    b3=0
    b4=0
    b5=0
    b6=0
    b7=0
    b8=0
    stmt = ibm_db.exec_immediate(conn, sql)
    while ibm_db.fetch_row(stmt):
        blood_type = ibm_db.result(stmt, 0)
        count = ibm_db.result(stmt, 1)
        if blood_type == "O Positive":
            b1 = count
            b += count
        if blood_type == "A Positive":
            b2 = count
            b += count
        if blood_type == "B Positive":
            b3 = count
            b += count
        if blood_type == "AB Positive":
            b4 = count
            b += count
        if blood_type == "O Negative":
            b5 = count
            b += count
        if blood_type == "A Negative":
            b6 = count
            b += count
        if blood_type == "B Negative":
            b7 = count
            b += count
        if blood_type == "AB Negative":
            b8 = count
            b += count
    return render_template('dashboard.html',b=b,b1=b1,b2=b2,b3=b3,b4=b4,b5=b5,b6=b6,b7=b7,b8=b8)
    
@app.route('/feedback', methods = ['GET','POST'])
def feedback():
    return render_template('feedback.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/requester')
def requester():
    return render_template('request.html')


@app.route('/requested',methods=['POST'])
def requested():
    bloodgrp = request.form['bloodgrp']
    address = request.form['address']
    print(address)
    sql = "SELECT * FROM user WHERE blood=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,bloodgrp)
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    msg = "Need Plasma of your blood group for: "+address
    while data != False:
        print ("The Phone is : ", data["PHONE"])
        url="https://www.fast2sms.com/dev/bulk?authorization=xCXuwWTzyjOD2ARd1EngbH3a7tKIq5PklJ8YSf0Lh4FQZecs9iNI1dSvuqprxFwCKYJXA5amQkBE36Rl&sender_id=FSTSMS&message="+msg+"&language=english&route=p&numbers="+str(data["PHONE"])
        result= requested.request("GET",url)
        print(result)
        data = ibm_db.fetch_assoc(stmt)
    return render_template('request.html', pred="Your request is sent to the concerned people.")



if __name__ == "__main__":
    app.run(debug=True)