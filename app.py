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
def calculate_bmr(gender, age, height, weight):
    if gender == 'male':
        # Harris-Benedict equation for males
        return round(66.5 + (13.75 * weight) + (5.003 * height) - (6.75 * age))
    elif gender == 'female':
        # Harris-Benedict equation for females
        return round(655.1 + (9.563 * weight) + (1.850 * height) - (4.676 * age))
@app.route('/CalTrack', methods=['GET','POST'])
def CalTrack():
    bmr_result = None
    if request.method == 'POST':
        gender = request.form['gender']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        bmr_result = calculate_bmr(gender, age, height, weight)
    return render_template('CalTrack.html', bmr=bmr_result)


if __name__ == '__main__':
    app.run(debug=True)