from flask import Flask, render_template,request,redirect, flash,session,make_response,jsonify, session, url_for
from db_services import DBO
from crypt_services import encrypt_sha256
import random
import string,os,json
from pathlib import Path
import flask

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
    user_id      = form_data['username'].lower()
    password     = form_data['password']
    account      = dbo.get_cred(user_id)
    enc_pass     = password
    if(enc_pass == account["PASSWORD"]):        
      session['session_var'] = {"user_id": user_id,
                    "USER_NAME": account["FIRST_NAME"]+" "+account["LAST_NAME"],
                    "USER_DEPARTMENT": account["USER_DEPARTMENT"],
                    "USER_LEVEL": account["USER_LEVEL"]}
      return make_response(render_template('dashboard.html',msg = True, err = False, warn = False, role=session['session_var']["USER_DEPARTMENT"],
                                             level=session['session_var']["USER_LEVEL"]),200)
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
    session_var = session.get('session_var', {})
    return render_template('dashboard.html', session_var=session_var)



@app.route('/changecontrolform') 
def changecontrolform():
    session_var = session.get('session_var', {})
    return render_template('changecontrolform.html', session_var=session_var)  
    
    

@app.route("/request_change_control", methods=['POST'])
def request_change_control():
    try:
        area_of_change = request.form.get('areaOfChange')
        document_number = request.form.get('documentNumber')
        initiator_department = request.form.get('initiatorDepartmentHidden')
        description = request.form.get('description')
        existing_status = request.form.get('existingStatus')
        proposed_change = request.form.get('proposedChange')
        reason_justification = request.form.get('reasonJustification')
        if area_of_change == 'Other':
            area_of_change = f'Other: {document_number}'

        dbo.insert_change_control_data(area_of_change, initiator_department, description, existing_status, proposed_change, reason_justification)

        response = {"status": "success"}
        return redirect(url_for('changecontrolform'))

    except Exception as e:
        response = {"status": "error", "message": str(e)}
        return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)