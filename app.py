from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import csv
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Seznamy zón pro Evropskou unii (zóna EU-F a EU-M)
zona_EU_F = ["BEL-F", "BGR-F", "DNK-F", "EST-F", "FIN-F", "FRA-F", "HRV-F", "IRL-F", "ITA-F", "CYP-F", "LTU-F", "LVA-F", "LUX-F", "HUN-F", "MLT-F", "DEU-F", "NLD-F", "POL-F", "PRT-F", "AUT-F", "ROU-F", "GRC-F", "SVK-F", "SVN-F", "ESP-F", "SWE-F"]
zona_EU_M = ["BEL-M", "BGR-M", "DNK-M", "EST-M", "FIN-M", "FRA-M", "HRV-M", "IRL-M", "ITA-M", "CYP-M", "LTU-M", "LVA-M", "LUX-M", "HUN-M", "MLT-M", "DEU-M", "NLD-M", "POL-M", "PRT-M", "AUT-M", "ROU-M", "GRC-M", "SVK-M", "SVN-M", "ESP-M", "SWE-M"]

# Načtení CSV souboru do seznamu
def load_csv(filename):
    with open(filename, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

# Uložení seznamu do CSV souboru
def save_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

# Úprava hodnot v seznamu
def modify_values(zmeny, nazev_zony, cena_hovoru, zmena_tarifikace, tarifikace_1, tarifikace_2):
    zmenene_zony = []

    if nazev_zony == "EU-F":
        zmenene_zony.extend(zona_EU_F)
    elif nazev_zony == "EU-M":
        zmenene_zony.extend(zona_EU_M)
    else:
        zmenene_zony.append(nazev_zony)

    for row in zmeny:
        if row[3] in zmenene_zony:
            row[5] = cena_hovoru
            row[7] = cena_hovoru
            if zmena_tarifikace == 'a':
                row[6] = tarifikace_1
                row[8] = tarifikace_2

@app.route('/')
def index():
    if not os.path.exists('data'):
        flash('Složka "data" neexistuje. Ujistěte se, že složka je ve správném adresáři.')
    elif not os.path.isfile('data/Default_CZK_1.csv'):
        flash('Soubor "Default_CZK_1.csv" nebyl nalezen ve složce "data". Ujistěte se, že soubor je na správném místě.')

    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    try:
        vstupni_soubor = 'data/Default_CZK_1.csv'
        zmeny = load_csv(vstupni_soubor)

        nazev_zony = request.form['nazev_zony']
        cena_hovoru = request.form['cena_hovoru']
        zmena_tarifikace = request.form.get('zmena_tarifikace')
        tarifikace_1 = request.form.get('tarifikace_1')
        tarifikace_2 = request.form.get('tarifikace_2')

        modify_values(zmeny, nazev_zony, cena_hovoru, zmena_tarifikace, tarifikace_1, tarifikace_2)

        nazev_noveho_souboru = request.form['nazev_noveho_souboru']
        novy_soubor_path = f"data/{nazev_noveho_souboru}"
        save_csv(novy_soubor_path, zmeny)

        flash('Změny byly úspěšně provedeny. Můžete pokračovat v úpravách nebo stáhnout nový soubor.')
        return render_template('index.html', nazev_noveho_souboru=nazev_noveho_souboru)

    except Exception as e:
        flash(f"Došlo k chybě: {e}")
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    file_path = os.path.join('data', filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    else:
        flash('Soubor nebyl nalezen.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
