from flask import Flask, render_template, request, redirect, flash, session, make_response, jsonify, url_for
from db_services import DBO
from functools import wraps
import os

app = Flask(__name__)
app.secret_key = 'file_upload_key'
MYDIR = os.path.dirname(__file__)
print("MYDIR", MYDIR)
dbo = DBO()

def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if 'session_var' not in session:
            flash('Please login to access this page', 'warning')
            return redirect(url_for('signin'))
        return view(*args, **kwargs)
    return wrapped_view



@app.route('/')
def signin():
    return render_template('signin.html')

@app.route("/render_login", methods=["GET", "POST"])
def render_login():
    form_data = request.form
    user_id = form_data['username'].lower()
    password = form_data['password']
    account = dbo.get_cred(user_id)
    enc_pass = password
    if enc_pass == account["PASSWORD"]:
        session['session_var'] = {"user_id": user_id,
                                   "USER_NAME": account["FIRST_NAME"] + " " + account["LAST_NAME"],
                                   "USER_DEPARTMENT": account["USER_DEPARTMENT"],
                                   "USER_LEVEL": account["USER_LEVEL"]}
        flash('Login Successful', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid Credentials', 'danger')
        return render_template("signin.html")


    
@app.route('/logout')
def logout():
    session.pop('session_var', None)
    flash('Logout Successful')
    return make_response(render_template("signin.html", msg=True, err=False, warn=False, message='Logout Successful'), 200)


@app.route('/dashboard')
@login_required
def dashboard():
    session_var = session.get('session_var', {})
    user_level = session['session_var'].get('USER_LEVEL', None)

    if user_level == 'hod':
        audit_data = dbo.fetch_audit_data_for_department(session_var.get("USER_DEPARTMENT", ""))
    else:
        audit_data = []

    return render_template('dashboard.html', session_var=session_var, audit_data=audit_data)

@app.route('/changecontrolform')
@login_required
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

        user_level = session['session_var']['USER_LEVEL']

        if area_of_change == 'Other':
            area_of_change = f'Other: {document_number}'

        dbo.insert_change_control_data(
            area_of_change, initiator_department, description, existing_status, proposed_change, reason_justification,
            level=user_level
        )

        response = {"status": "success"}
        return redirect(url_for('changecontrolform'))

    except Exception as e:
        response = {"status": "error", "message": str(e)}
        return jsonify(response), 500

@app.route('/update_form/<int:audit_id>')
def update_form(audit_id):
    record = dbo.get_audit_data_by_id(audit_id)
    print("Record Data:", record)
    return render_template('changecontrolform.html', record=record, is_update=True)

@app.route("/update_form/<int:audit_id>", methods=['POST'])
def update_form_submit(audit_id):
    approval = request.form.get('approval')
    remark = request.form.get('remark')

    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
