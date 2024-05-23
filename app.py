from flask import Flask, render_template, request, redirect, url_for
import csv
import os

app = Flask(__name__)

# Seznamy zón pro Evropskou unii (zóna EU-F a EU-M)
zona_EU_F = ["BEL-F", "BGR-F", "DNK-F", "EST-F", "FIN-F", "FRA-F", "HRV-F", "IRL-F", "ITA-F", "CYP-F", "LTU-F", "LVA-F", "LUX-F", "HUN-F", "MLT-F", "DEU-F", "NLD-F", "POL-F", "PRT-F", "AUT-F", "ROU-F", "GRC-F", "SVK-F", "SVN-F", "ESP-F", "SWE-F"]
zona_EU_M = ["BEL-M", "BGR-M", "DNK-M", "EST-M", "FIN-M", "FRA-M", "HRV-M", "IRL-M", "ITA-M", "CYP-M", "LTU-M", "LVA-M", "LUX-M", "HUN-M", "MLT-M", "DEU-M", "NLD-M", "POL-M", "PRT-M", "AUT-M", "ROU-M", "GRC-M", "SVK-M", "SVN-M", "ESP-M", "SWE-M"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    vstupni_soubor = 'data/Default_CZK_1.csv'
    nazev_zony = request.form['nazev_zony']
    cena_hovoru = request.form['cena_hovoru']
    zmena_tarifikace = request.form.get('zmena_tarifikace')
    tarifikace_1 = request.form.get('tarifikace_1')
    tarifikace_2 = request.form.get('tarifikace_2')

    zmeny = []  # Seznam pro ukládání změn

    # Načtení vstupního souboru do seznamu
    with open(vstupni_soubor, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        zmeny.extend(list(reader))  # Načtení všech řádků ze vstupního souboru

    # Seznam zón, které mají být změněny
    zmenene_zony = []

    # Pokud je zadaný název zóny "EU-F" nebo "EU-M", aplikuj změny pro všechny zóny v těchto seznamech
    if nazev_zony == "EU-F":
        zmenene_zony.extend(zona_EU_F)
    elif nazev_zony == "EU-M":
        zmenene_zony.extend(zona_EU_M)
    else:
        # Pokud uživatel zadal jiný název zóny, aplikuj změny pouze pro tuto konkrétní zónu
        zmenene_zony.append(nazev_zony)

    # Procházíme řádky a aplikujeme změny pro vybrané zóny
    for row in zmeny:
        if row[3] in zmenene_zony:
            row[5] = cena_hovoru  # šestý sloupec v CSV s cenou pro první interval
            row[7] = cena_hovoru  # osmý sloupec v CSV s cenou pro druhý a každý další interval, cena shodná s prvním intervalem
            # Pokud uživatel zvolil, že chce upravovat i tarifikaci, budeme ukládat i tyto hodnoty ze vstupů
            if zmena_tarifikace == 'a': 
                row[6] = tarifikace_1  # sedmý sloupec v CSV s tarifikací pro první interval
                row[8] = tarifikace_2  # devátý sloupec v CSV s tarifikací pro každý další interval

    # Dotaz na název nového souboru
    nazev_noveho_souboru = request.form['nazev_noveho_souboru']
    novy_soubor_path = f"data/{nazev_noveho_souboru}"
    print("Vytváření nového souboru...")

    # Uložení změn do nového CSV souboru
    if zmeny:
        with open(novy_soubor_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerows(zmeny)

    return render_template('result.html', nazev_noveho_souboru=nazev_noveho_souboru)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
