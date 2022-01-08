from flask import Flask, redirect, url_for, request, jsonify
from flask.templating import render_template
import pandas as pd
import joblib

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    pred_res = False
    kpr_res = False
    # if request.method == 'POST':
    #     for key, value in request.form.items():
    #         if key == 'luast':
    #             pred_res = predict(request.form)
    #         elif key == 'pinjam':
    #             kpr_res = kpr_calc(request.form)
    return render_template('index.html')

@app.route('/predict_calc')
def predict():
    model = joblib.load('Model rumah.sav')
    luast = int(request.args.get('x1'))
    luas = int(request.args.get('x2'))
    kamar = int(request.args.get('x3'))
    kamarm = int(request.args.get('x4'))
    lantai = int(request.args.get('x5'))
    garasi = int(request.args.get('x6'))
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
    prediksi_dump = cut_num(lower) + ' - ' + cut_num(upper)
    return render_template('predict_calc.html', prediksi_dump = prediksi_dump)

@app.route('/kpr_calc')
def kpr_calc_flat():
    #Cicilan bunga KPR dengan bunga flat
    #Bunganya tidak bertambah setiap tahunnya
    pinjam = int(request.args.get('kpr1'))
    suku = (float(request.args.get('kpr2')))/100
    jangka = float(request.args.get('kpr3'))

    bunga = (pinjam*suku*jangka)/(jangka*12)
    grand_total = pinjam + (bunga*(jangka*12))

    pred = int(request.args.get('kpr1'))
    suku = float(request.args.get('kpr2'))
    tahun = int(request.args.get('kpr3'))
    tenor = tahun*12
    cicilan_pokok = pred/tenor
    bunga = suku/1200

    minimal_bunga = bunga * pred 
    cibul = cicilan_pokok + minimal_bunga

    total_bayar= cibul * tenor

    # print("Sehingga, cicilan yang harus dibayarkan perbulan adalah", cibul)
    # print("Dengan total yang harus dibayar adalah", to_rupiah(total_bayar))
    # kpr_dump = [to_rupiah(cibul), to_rupiah(total_bayar)]
    # kpr_dump = to_rupiah(cibul)
    kpr_dump1 = to_rupiah(cibul)
    kpr_dump2 = to_rupiah(total_bayar)
    return render_template('kpr_calc.html', kpr_dump1 = kpr_dump1, kpr_dump2 = kpr_dump2)

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

if __name__ == '__main__':
    app.run(debug = True)
