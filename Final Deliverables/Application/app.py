

import ibm_db
from flask import Flask, redirect, render_template, request, session, url_for
from markupsafe import escape

#mail
from flask import Flask
from flask_mail import Mail, Message


app = Flask(__name__)
mail = Mail(app) 
   
# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "ashwindev1462001@gmail.com" 
app.config['MAIL_PASSWORD'] = "ntmquaqeniemojyk" 
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
   




conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=824dfd4d-99de-440d-9991-629c01b3832d.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30119;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=kpr74378;PWD=0ijMNdNTAeNHpl5E",'','')

app.secret_key='a'


def send_mail(recipient_mail):
  msg = Message(
            'Expense tracker',
            sender ='ashwindev1462001@gmail.com',
            recipients = [recipient_mail]
            )
  msg.body = 'Your Expense Limit has Exceeded'
  mail.send(msg)
  return True

@app.route('/')
@app.route('/register')
def register():
  return render_template('register.html')
@app.route('/index')
def index():
  return render_template('index.html')

@app.route('/header')
def header():
    return render_template('header.html')

@app.route('/home')
def home():
  return render_template('home.html')



@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/addExpense')
def addExpense():
    return render_template('AddExpense.html')

#for mail 
'''
@app.route('/send_mail', methods=['GET', 'POST'])
def send_mail():
    print("method")
    print(request.method)
    if request.method == 'POST':
        
      print("post method activated")
      print(request.form)
      recipient = request.form['recipient']
      print(recipient)
      msg = Message('Twilio SendGrid Test Email', recipients=[recipient])
      msg.body = ('Congratulations! You have sent a test email with '
                  'Twilio SendGrid!')
      msg.html = ('<h1>Twilio SendGrid Test Email</h1>'
                  '<p>Congratulations! You have sent a test email with '
                  '<b>Twilio SendGrid</b>!</p>')
      mail.send(msg)
      flash(f'A test message was sent to {recipient}.')
      #return redirect(url_for('index'))
    return render_template('home.html')

#end for mail
'''


@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
  if request.method == 'POST':

    name = request.form['name']
    email = request.form['email']
    phone = request.form['phone']
    password= request.form['password']

    sql = "SELECT * FROM USERS WHERE NAME =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt,1,name)
    ibm_db.execute(stmt)
    account = ibm_db.fetch_assoc(stmt)

    if account:
      return render_template('login.html', msg="You are already a member, please login using your details")
    else:
      insert_sql = "INSERT INTO USERS (Name,email,phone,password) VALUES (?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, name)
      ibm_db.bind_param(prep_stmt, 2, email )
      ibm_db.bind_param(prep_stmt, 3, phone)
      ibm_db.bind_param(prep_stmt, 4, password)
      ibm_db.execute(prep_stmt)

    
    return render_template('login.html', msg="Registered successfuly..")






@app.route('/signin', methods =['GET', 'POST'])
def signIn():
    global userid
    msg = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        sql ="SELECT * FROM USERS WHERE  email = ? AND password = ?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,email)
        ibm_db.bind_param(stmt,2,password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)
            
        if account:
            session['loggedin'] = True
            session['id'] = account['USERID']
            userid=account['USERID']
            session['username']=account['NAME']

            #session["name"] = request.form.get("name")
            
            #session['username'] = account['Name']
            msg = 'Welcome'+" "+session['username']+"!!"
            return render_template('home.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
        return render_template('login.html', msg = msg)





@app.route('/add', methods =['GET', 'POST'])
def add():
    global id
    if request.method=='POST':
      date=request.form['date']
      name=request.form['expenseName']
      amount=request.form['expenseAmount']
      category=request.form['expenseCategory']
      paymethod=request.form['payMethod']
      id=session['id']
      print("session id",id)


      


      insert_sql = "INSERT INTO EXPENSES (USERID,DATE,NAME,AMOUNT,CATEGORY,PAYMENTMETHOD) VALUES (?,?,?,?,?,?)"
      prep_stmt = ibm_db.prepare(conn, insert_sql)
      ibm_db.bind_param(prep_stmt, 1, id)
      ibm_db.bind_param(prep_stmt, 2, date )
      ibm_db.bind_param(prep_stmt, 3, name)
      ibm_db.bind_param(prep_stmt, 4, amount)
      ibm_db.bind_param(prep_stmt, 5, category)
      ibm_db.bind_param(prep_stmt, 6, paymethod)
      ibm_db.execute(prep_stmt)

      limit="SELECT AMOUNT FROM LIMIT WHERE USERID=?"
      stmt = ibm_db.prepare(conn, limit)
      ibm_db.bind_param(stmt,1,id)
      ibm_db.execute(stmt)
      account = ibm_db.fetch_assoc(stmt)
      print(account)
      limit_amount=account['AMOUNT']
      print(limit_amount)

      total="SELECT SUM(AMOUNT) FROM EXPENSES WHERE USERID=?"
      stmt = ibm_db.prepare(conn, total)
      ibm_db.bind_param(stmt,1,id)
      ibm_db.execute(stmt)
      account= ibm_db.fetch_assoc(stmt)

      print("account")
      print( account)

      print("account id")
      print(id)
      total_amount=account['1']
      print("total_amount")
      print(total_amount)

      if (int(total_amount)>int(limit_amount)):
        print("Limit exceeded")
        account_stmt="SELECT EMAIL FROM USERS WHERE USERID=?"
        stmt = ibm_db.prepare(conn, account_stmt)
        ibm_db.bind_param(stmt,1,id)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        send_mail(account['EMAIL'])
        return render_template("limitwarn.html")
      else:
        print(total_amount, limit_amount)
    return render_template('AddExpense.html')
      
            


   

      
      

@app.route('/history')
def history():
  global id
  id=session['id']
  print(session['username'])
  students = []
  total=0
  sql = "SELECT * FROM EXPENSES where USERID=?"
  stmt = ibm_db.prepare(conn, sql)
  ibm_db.bind_param(stmt,1,id)
  ibm_db.execute(stmt)
  dictionary = ibm_db.fetch_both(stmt)
  
  '''limit="SELECT AMOUNT FROM LIMIT WHERE USERID=?"
  stmt = ibm_db.prepare(conn, limit)
  ibm_db.bind_param(stmt,1,id)
  ibm_db.execute(stmt)
  account = ibm_db.fetch_assoc(stmt)
  print(account)
  amount=account['AMOUNT']
  print(amount)'''
  while dictionary != False:
    # print ("The Name is : ",  dictionary)
    students.append(dictionary)
    total+=int(dictionary[3])
    dictionary = ibm_db.fetch_both(stmt)

  
        

  if students:
    return render_template("history.html", students = students,total=total)


@app.route('/limit')
def limit():
      return render_template("limit.html")



@app.route('/limitnum' , methods = ['POST' ])
def limitnum():
     if request.method == "POST":
        number= request.form['number']
        sql = "INSERT INTO LIMIT(USERID,AMOUNT) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt,1,session['id'])
        ibm_db.bind_param(stmt,2,number)
        ibm_db.execute(stmt)
        return render_template("today.html")

@app.route('/logout')
def logout():
  session.pop('loggedin', None)
  session.pop('id', None)
  session.pop('username', None)
  return render_template('register.html')
      
@app.route("/today")
def today():
      
      
      sql = "SELECT * FROM EXPENSES  WHERE userid =? AND date = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense=ibm_db.fetch_tuple(stmt)
      print(texpense)
      
      

      sql = "SELECT * FROM EXPENSES WHERE USERID=? AND DATE(date) = DATE(NOW())"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)  
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
        total +=int(x[3])
        if x[4] == "food":
          t_food += int(x[3])
        
        elif x[4] == "entertainment":
            t_entertainment  += int(x[3])
      
        elif x[4] == "business":
              t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
          
  


     
      return render_template("today.html", texpense = list1, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )




@app.route("/month")
def month():
      sql = "SELECT MONTHNAME(DATE),SUM(AMOUNT) FROM EXPENSES WHERE USERID=? GROUP BY MONTHNAME(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)
      
      

      sql = "SELECT * FROM EXPENSES WHERE USERID=? AND MONTH(date)=MONTH(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
      print(list1)  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
          
        total += int(x[3])
        if x[4] == "food":
          t_food +=int(x[3])
            
        elif x[4] == "entertainment":
          t_entertainment  += int(x[3])
        
        elif x[4] == "business":
          t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("month.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )
         


@app.route("/year")
def year():
      
      
      sql = "SELECT YEAR(DATE),SUM(AMOUNT) FROM EXPENSES WHERE USERID=? GROUP BY YEAR(DATE)"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list2=[]
      texpense = ibm_db.fetch_tuple(stmt)
      while(texpense):
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
      print(list2)


      

      sql = "SELECT * FROM EXPENSES WHERE USERID=? AND YEAR(date)=YEAR(DATE(NOW()))"
      stmt = ibm_db.prepare(conn, sql)
      ibm_db.bind_param(stmt,1,session['id'])
      ibm_db.execute(stmt)
      list1=[]
      expense = ibm_db.fetch_tuple(stmt)
      while(expense):
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)
  
      total=0
      t_food=0
      t_entertainment=0
      t_business=0
      t_rent=0
      t_EMI=0
      t_other=0
 
     
      for x in list1:
        total += int(x[3])
        if x[4] == "food":
          t_food +=int(x[3])
            
        elif x[4] == "entertainment":
          t_entertainment  += int(x[3])
        
        elif x[4] == "business":
          t_business  += int(x[3])
        elif x[4] == "rent":
          t_rent  += int(x[3])
           
        elif x[4] == "emi":
          t_EMI  += int(x[3])
         
        elif x[4] == "Miscellaneous":
          t_other  += int(x[3])
          
            
      print(total)
        
      print(t_food)
      print(t_entertainment)
      print(t_business)
      print(t_rent)
      print(t_EMI)
      print(t_other)


     
      return render_template("year.html", texpense = list2, expense = expense,  total = total ,
                           t_food = t_food,t_entertainment =  t_entertainment,
                           t_business = t_business,  t_rent =  t_rent, 
                           t_EMI =  t_EMI,  t_other =  t_other )

if __name__ =='__main__':
    app.run(host='0.0.0.0',debug=True)