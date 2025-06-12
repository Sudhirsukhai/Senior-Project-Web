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
    return render_template('register.html')

@app.route('/Main')
def Main_Page():
    return render_template('MainPage.html')


def calculate_bmr(gender: str, age: int, height_cm: float, weight_kg: float) -> float:
    if gender.lower() == 'male':
        return 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.75 * age)
    elif gender.lower() == 'female':
        return 655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'super': 1.9
    }
    return bmr * multipliers.get(activity_level, 1.2)

@app.route('/bmr', methods=['GET', 'POST'])
def bmr_page():
    bmr = tdee = None
    if request.method == 'POST':
        gender = request.form['gender']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity_level = request.form['activity']

        bmr = round(calculate_bmr(gender, age, height, weight), 2)
        tdee = round(calculate_tdee(bmr, activity_level), 2)

    return render_template('CalTrack.html', bmr=bmr, tdee=tdee)

 
if __name__ == '__main__':
    app.run(debug=True)