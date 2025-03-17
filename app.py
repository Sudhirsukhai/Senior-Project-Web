from flask import Flask, render_template, url_for,request,flash
from flask_sqlalchemy import SQLAlchemy

app=Flask(__name__)


@app.route('/', methods=['GET','POST'])
def home():
    data=request.form
    print(data)
    return render_template('index.html', boolean=True)

@app.route('/register',methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('Uname')
        Pass = request.form.get('Pass')
        Pass2 = request.form.get('ConPass')
        if len(Pass)<4:
            flash('Email must be greater than 4 characters.', category='error')
            pass
        elif len(username)<2:
            flash('Password must be greater than 2 characters.', category='error')
            pass
        elif Pass!= Pass2:
            flash('Passwords do not match.', category='error')
            pass
        else:
            flash('Account Created.', category='Success')
            #add user
            pass

    return render_template('register.html')

@app.route('/Main')
def Main():
    return render_template('MainPage.html')

if __name__ == '__main__':
    app.run(debug=True)