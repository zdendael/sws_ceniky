from flask import Flask, render_template, request, redirect, url_for, flash, send_file
import csv
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Funkce pro načtení všech zón ze zdrojového CSV souboru
def load_zones_from_csv(filename):
    zones = {}
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Přeskočíme hlavičku
        for row in reader:
            zones[row[3]] = row[4]
    return zones

# Načtení všech zón ze souboru
vsechny_zony = load_zones_from_csv('data/Default_CZK_1.csv')

# Přidání zón EU-F a EU-M do seznamu zón
vsechny_zony["EU-F"] = "Evropská unie - F"
vsechny_zony["EU-M"] = "Evropská unie - M"

# Konverze na seznam pro HTML šablonu
vsechny_zony_seznam = [{"kod": k, "nazev": v} for k, v in vsechny_zony.items()]

# Načtení CSV souboru do seznamu
def load_csv(filename):
    with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        return list(reader)

# Uložení seznamu do CSV souboru
def save_csv(filename, data):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)

# Úprava hodnot v seznamu
def modify_values(zmeny, zony_data):
    for zona in zony_data:
        nazev_zony = zona['nazev_zony']
        cena_hovoru = zona['cena_hovoru']
        tarifikace = zona['tarifikace']

        zmenene_zony = []

        if nazev_zony == "EU-F":
            zmenene_zony.extend(["BEL-F", "BGR-F", "DNK-F", "EST-F", "FIN-F", "FRA-F", "HRV-F", "IRL-F", "ITA-F", "CYP-F", "LTU-F", "LVA-F", "LUX-F", "HUN-F", "MLT-F", "DEU-F", "NLD-F", "POL-F", "PRT-F", "AUT-F", "ROU-F", "GRC-F", "SVK-F", "SVN-F", "ESP-F", "SWE-F"])
        elif nazev_zony == "EU-M":
            zmenene_zony.extend(["BEL-M", "BGR-M", "DNK-M", "EST-M", "FIN-M", "FRA-M", "HRV-M", "IRL-M", "ITA-M", "CYP-M", "LTU-M", "LVA-M", "LUX-M", "HUN-M", "MLT-M", "DEU-M", "NLD-M", "POL-M", "PRT-M", "AUT-M", "ROU-M", "GRC-M", "SVK-M", "SVN-M", "ESP-M", "SWE-M"])
        else:
            zmenene_zony.append(nazev_zony)

        for row in zmeny:
            if row[3] in zmenene_zony:
                row[5] = cena_hovoru
                if tarifikace:  # Pokud je tarifikace zadána, použij ji
                    row[6] = tarifikace

@app.route('/')
def index():
    if not os.path.exists('data'):
        flash('Složka "data" neexistuje. Ujistěte se, že složka je ve správném adresáři.')
    elif not os.path.isfile('data/Default_CZK_1.csv'):
        flash('Soubor "Default_CZK_1.csv" nebyl nalezen ve složce "data". Ujistěte se, že soubor je na správném místě.')

    return render_template('index.html', vsechny_zony=vsechny_zony_seznam)

@app.route('/process', methods=['POST'])
def process():
    try:
        vstupni_soubor = 'data/Default_CZK_1.csv'
        zmeny = load_csv(vstupni_soubor)

        zony_data = []
        for i in range(len(request.form.getlist('nazev_zony'))):
            zony_data.append({
                'nazev_zony': request.form.getlist('nazev_zony')[i],
                'cena_hovoru': request.form.getlist('cena_hovoru')[i],
                'tarifikace': request.form.getlist('tarifikace')[i] if request.form.getlist('tarifikace')[i] else None
            })

        modify_values(zmeny, zony_data)

        nazev_noveho_souboru = request.form['nazev_noveho_souboru']
        novy_soubor_path = f"data/{nazev_noveho_souboru}"
        save_csv(novy_soubor_path, zmeny)

        flash('Změny byly úspěšně provedeny. Můžete pokračovat v úpravách nebo stáhnout nový soubor.')
        return render_template('index.html', vsechny_zony=vsechny_zony_seznam, nazev_noveho_souboru=nazev_noveho_souboru)

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
