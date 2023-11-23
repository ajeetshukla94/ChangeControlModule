from flask import Flask, render_template,request,flash,session,make_response
from db_dervices import DBO
from crypt_services import encrypt_sha256
import random
import string,os
from pathlib import Path

app = Flask(__name__)
app.secret_key = 'file_upload_key'
MYDIR = os.path.dirname(__file__)
print("MYDIR",MYDIR)
dbo = DBO()


@app.route('/')
def signin():
    return render_template('signin.html')                  
                
@app.route("/render_login", methods=["GET", "POST"])
def render_login(): 
    form_data    = request.form
    user_id      = "ashukl94"#form_data['email'].lower()
    password     = "password"#form_data['password']
    account      = dbo.get_cred(user_id)
    enc_pass     = password
    print(account["PASSWORD"])
    print(password)
    print(account)
    if(enc_pass == account["PASSWORD"]):        
      session_var = {"user_id": user_id,"USER_NAME": account["FIRST_NAME"]+" "+account["LAST_NAME"],"USER_TYPE": account["USER_TYPE"],}
      return make_response(render_template('dashboard.html',msg = True, err = False, warn = False, role = session_var["USER_TYPE"]),200)
    else:
      flash('Invalid Credentials')
      return make_response(render_template("signin.html", msg = False, err = True, warn = False),403)   
      
      
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('selected_file', None)
    flash('Logout Successful')
    return make_response(render_template("signin.html",msg = True,err = False, warn = False,message='Logout Successful'),200)  

#################################### End Login logout ###################################### 

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/changecontrolform') 
def changecontrolform():
    return render_template('changecontrolform.html')  

if __name__ == '__main__':
    app.run(debug=True)