from flask import Flask, render_template, request, send_file, jsonify
import csv
import os

app = Flask(__name__)

# Seznam zón pro Evropskou unii (zóna EU-F a EU-M)
zona_EU_F = ["BEL-F", "BGR-F", "DNK-F", "EST-F", "FIN-F", "FRA-F", "HRV-F", "IRL-F", "ITA-F", "CYP-F", "LTU-F", "LVA-F", "LUX-F", "HUN-F", "MLT-F", "DEU-F", "NLD-F", "POL-F", "PRT-F", "AUT-F", "ROU-F", "GRC-F", "SVK-F", "SVN-F", "ESP-F", "SWE-F"]
zona_EU_M = ["BEL-M", "BGR-M", "DNK-M", "EST-M", "FIN-M", "FRA-M", "HRV-M", "IRL-M", "ITA-M", "CYP-M", "LTU-M", "LVA-M", "LUX-M", "HUN-M", "MLT-M", "DEU-M", "NLD-M", "POL-M", "PRT-M", "AUT-M", "ROU-M", "GRC-M", "SVK-M", "SVN-M", "ESP-M", "SWE-M"]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'HEAD':
        return '', 200
    vsechny_zony = []
    with open('Default_CZK_1.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Přeskočíme hlavičku
        for row in reader:
            vsechny_zony.append({'kod': row[3], 'nazev': row[4]})
    
    return render_template('index.html', vsechny_zony=vsechny_zony)

@app.route('/process', methods=['POST'])
def process():
    try:
        nazev_noveho_souboru = request.form['nazev_noveho_souboru'] + '.csv'
        input_zones = request.form.getlist('nazev_zony')
        ceny_hovoru = request.form.getlist('cena_hovoru')
        tarifikace_1 = request.form.getlist('tarifikace_1')
        tarifikace_2 = request.form.getlist('tarifikace_2')
        
        # Načteme původní data
        with open('Default_CZK_1.csv', 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        
        # Změníme hodnoty v souboru
        for i, zona in enumerate(input_zones):
            for row in rows:
                if row[3] == zona or (zona == "EU-F" and row[3] in zona_EU_F) or (zona == "EU-M" and row[3] in zona_EU_M):
                    row[5] = ceny_hovoru[i]  # Cena hovoru
                    row[7] = ceny_hovoru[i]  # Cena hovoru pro druhý interval
                    if tarifikace_1[i]:
                        row[6] = tarifikace_1[i]  # Tarifikace pro první interval
                    if tarifikace_2[i]:
                        row[8] = tarifikace_2[i]  # Tarifikace pro druhý interval

        # Uložíme nový soubor
        with open(nazev_noveho_souboru, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(rows)
        
        return jsonify({'filename': nazev_noveho_souboru})
    except Exception as e:
        print(e)
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists('data'):
        os.makedirs('data')
    app.run(debug=True)
