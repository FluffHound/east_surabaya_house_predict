from flask import Flask, redirect, url_for, request, jsonify
from flask.json import load
from flask.templating import render_template
import pandas as pd
import joblib

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    pred_res = False
    kpr_res = False
    if request.method == 'POST':
        for key, value in request.form.items():
            if key == 'luast':
                pred_res = predict(request.form)
            elif key == 'pinjam':
                kpr_res = kpr_calc(request.form)
    return render_template('index.html', pred_res = pred_res, kpr_res = kpr_res)

def predict(form):
    model = joblib.load('/home/zagreus/Documents/Coding/HTML/AlPro/UAS/Model rumah.sav')
    luast = int(request.form['luast'])
    luas = int(request.form['luas'])
    kamar = int(request.form['kamar'])
    kamarm = int(request.form['kamarm'])
    lantai = int(request.form['lantai'])
    garasi = int(request.form['garasi'])
    dict = {'Luas Tanah': [luast],
            'Luas Bangunan': [luas],
            'Kamar': [kamar],
            'Kamar Mandi': [kamarm],
            'Jumlah Lantai': [lantai],
            'Garasi': [garasi]}
    payload = pd.DataFrame(dict)
    result = model.predict(payload)
    lower = str(int(result[0]*(90/100))) + '.00'
    lower = to_rupiah(lower)
    upper = str(int(result[0]*(110/100))) + '.00'
    upper = to_rupiah(upper)
    return cut_num(lower) + ' - ' + cut_num(upper)

def kpr_calc(form):
    pinjam = int(request.form['pinjam'])
    suku = (float(request.form['suku']))/100
    jangka = float(request.form['tahun'])

    bunga = (pinjam*suku*jangka)/(jangka*12)
    grand_total = pinjam + (bunga*(jangka*12))
    return (to_rupiah(bunga), to_rupiah(grand_total))

def to_rupiah(value):
    str_value = str(value)
    separate_decimal = str_value.split(".")
    after_decimal = separate_decimal[0]
    before_decimal = separate_decimal[1]

    reverse = after_decimal[::-1]
    temp_reverse_value = ""

    for index, val in enumerate(reverse):
        if (index + 1) % 3 == 0 and index + 1 != len(reverse):
            temp_reverse_value = temp_reverse_value + val + "."
        else:
            temp_reverse_value = temp_reverse_value + val

    temp_result = temp_reverse_value[::-1]

    return "Rp " + temp_result

def cut_num(angka):
    if len(angka) > 12:
        if angka[5] == '0':
            return str(angka[3] + ' M')
        else:
            return str(angka[3] + ',' + angka[5] + ' M')
    else:
        return str(angka + ' Juta')

@app.route('/input', methods=['GET', 'POST'])
def calc_mom():
    hasil = False
    if request.method == 'POST':
        numbers = request.form
        hasil = rumus(numbers)
    
    return render_template('student.html', hasil = hasil)

def rumus(form):
    panjang = int(request.form['panjang'])
    lebar = int(request.form['lebar'])

    keliling = 2*panjang + 2*lebar
    luas = panjang*lebar

    return(keliling, luas)


@app.route('/input/result', methods = ['POST', 'GET'])
def result():
    angka = []
    for i in range(3):
        angka.append(i)
    data = pd.read_csv('/home/zagreus/Documents/Coding/HTML/AlPro/UAS/Dataset rumah123 akhir.csv')
    data = data[['Luas Tanah', 'Luas Bangunan', 'Kamar', 'Kamar Mandi', 'Garasi']]
    features = ['Luas Tanah', 'Luas Bangunan', 'Kamar', 'Kamar Mandi', 'Garasi']
    if request.method == 'POST':
        result = request.form
        return render_template('result.html', result = result, test = angka, data = data, fitur = features)

@app.route('/response', methods=['POST'])
def my_form_post():
    text = request.form['text']
    processed_text = text.upper()
    return render_template('result.html', miu = processed_text)

if __name__ == '__main__':
    app.run(debug = True)