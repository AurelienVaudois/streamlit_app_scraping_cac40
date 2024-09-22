import streamlit as st
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import numpy as np

# Configuration des lignes spécifiques par secteur
sector_config = {
        
    'Banques': {
        'produit_net': 'Produit net bancaire',
        'resultat_brut': 'Resultat brut d\'exploitation',
        'interet_sur_la_dette': 'Coût du risque',
        'company': ['BNP', 'Societe Generale', 'Credit Agricole']
    },
    'Automobile': {
        'produit_net': 'Chiffre d\'affaires',
        'resultat_brut': 'Résultat opérationnel',
        'interet_sur_la_dette': 'Coût de l\'endettement financier net',
        'company': ['Stellantis', 'Renault']

    },
    'Luxe': {
        'produit_net': 'Chiffre d\'affaires',
        'resultat_brut': 'Résultat opérationnel',
        'interet_sur_la_dette': 'Coût de l\'endettement financier net',
        'company': ['Kering', 'LVMH', 'Christian Dior', 'Hermes']

    },
    
            'Semi_conducteurs': {
        'produit_net': 'Chiffre d\'affaires',
        'resultat_brut': 'Résultat opérationnel',
        'interet_sur_la_dette': 'Coût de l\'endettement financier net',
        'company': ['STMICROELECTRONICS', 'Soitec']

},

    # Ajoutez d'autres configurations pour d'autres secteurs ici
}

# Dictionnaire pour stocker les URLs des entreprises
company_urls = {
    'BNP': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPBNP/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPBNP/',
        'dividendes':'https://rendementbourse.com/bnp-bnp-paribas/dividendes',
        'fiscal_year_end': '12'
    },
    'Societe Generale': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPGLE/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPGLE/',
        'dividendes':'https://rendementbourse.com/gle-societe-generale/dividendes',
        'fiscal_year_end': '12'
    },
    'Credit Agricole': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPACA/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPACA/',
        'dividendes':'https://rendementbourse.com/aca-credit-agricole/dividendes',
        'fiscal_year_end': '12'
    },
    'Stellantis': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPSTLAP/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPSTLAP/',
        'dividendes':'https://rendementbourse.com/stla-stellantis/dividendes',
        'fiscal_year_end': '12'
    },
    'Renault': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPRNO/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPRNO/',
        'dividendes':'https://rendementbourse.com/rno-renault/dividendes',
        'fiscal_year_end': '12'
    },
    'Kering': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPKER/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPKER/',
        'dividendes':'https://rendementbourse.com/ker-kering/dividendes',
        'fiscal_year_end': '12'
    },
    'LVMH': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPMC/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPMC/',
        'dividendes':'https://rendementbourse.com/mc-lvmh/dividendes',        
        'fiscal_year_end': '12'
    },
    'Christian Dior': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPCDI/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPCDI/',
        'dividendes':'https://rendementbourse.com/cdi-christian-dior/dividendes',
        'fiscal_year_end': '12'
    },
    'Hermes': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPRMS/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPRMS/',
        'dividendes':'https://rendementbourse.com/rms-hermes-international/dividendes',
        'fiscal_year_end': '12'
    },
    'STMICROELECTRONICS': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPSTMPA/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPSTMPA/',
        'dividendes':'https://rendementbourse.com/stm-stmicroelectronics/dividendes',
        'fiscal_year_end': '12'
    },
    'Soitec': {
        'consensus': 'https://www.boursorama.com/cours/consensus/1rPSOI/',
        'chiffres_cles': 'https://www.boursorama.com/cours/societe/chiffres-cles/1rPSOI/',
        'dividendes': 'https://rendementbourse.com/soi-soitec/dividendes',
        'fiscal_year_end': '03'
    }
}


# Réutilisation des fonctions existantes :
def fetch_webpage(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def parse_tables(html):
    soup = BeautifulSoup(html, 'html.parser')
    tables = soup.find_all('table')
    
    if not tables:
        return []
    
    dataframes = []
    for i, table in enumerate(tables):
        headers = []
        rows = []
        for th in table.find_all('th'):
            headers.append(th.text.strip())
        
        for tr in table.find_all('tr'):
            cells = tr.find_all('td')
            if cells:
                row = [cell.text.strip() for cell in cells]
                rows.append(row)
        
        if rows:
            if headers and len(headers) == len(rows[0]):
                df = pd.DataFrame(rows, columns=headers)
            else:
                df = pd.DataFrame(rows)
            dataframes.append(df)
    
    return dataframes

def get_valorisation_and_cours(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    valorisation_element = soup.find_all('li', class_='c-list-info__item')
    valorisation = 'N/A'

    for item in valorisation_element:
        heading = item.find('p', class_='c-list-info__heading u-color-neutral')
        if heading and 'valorisation' in heading.get_text(strip=True).lower():
            valorisation = item.find('p', class_='c-list-info__value u-color-big-stone').get_text(strip=True).replace(' MEUR', '').replace(' ', '')
            break

    cours_element = soup.find('span', class_='c-instrument c-instrument--last')
    cours_du_jour = cours_element.text.strip().replace(' ', '').replace(',', '.') if cours_element else 'N/A'
    
    return float(valorisation) * 1_000_000, float(cours_du_jour)

def save_to_excel(dataframes, file_name, sheet_name, valorisation=None, cours_du_jour=None):  
    file_exists = os.path.exists(file_name)
    
    with pd.ExcelWriter(file_name, mode='a' if file_exists else 'w') as writer:
        for i, df in enumerate(dataframes):
            sheet_name_to_use = f'{sheet_name}_Table_{i+1}'
            if sheet_name_to_use in writer.book.sheetnames:
                print(f"Sheet {sheet_name_to_use} already exists. It will be overwritten.")
                writer.book.remove(writer.book[sheet_name_to_use])
            df.to_excel(writer, sheet_name=sheet_name_to_use, index=False)
        
        if valorisation and cours_du_jour:
            summary_sheet_name = f'{sheet_name}_Summary'
            if summary_sheet_name in writer.book.sheetnames:
                writer.book.remove(writer.book[summary_sheet_name])
            summary_df = pd.DataFrame({
                'Valorisation': [valorisation],
                'Cours du jour': [cours_du_jour]
            })
            summary_df.to_excel(writer, sheet_name=summary_sheet_name, index=False)
        
def calculate_and_store_indicators(file_name, output_file, societe_name, secteur_name):
    if secteur_name not in sector_config:
        print(f"Secteur {secteur_name} non configuré.")
        return

    config = sector_config[secteur_name]
    company_info = company_urls[societe_name]
    
    # Récupérer la fin de l'exercice fiscal spécifique à l'entreprise
    fiscal_year_end = company_info.get('fiscal_year_end', '12')  # Par défaut, on prend décembre si non spécifié
    year_suffix = '23' if fiscal_year_end == '12' else '24'  # Utiliser l'année 23 pour décembre, 24 pour mars

    # Ajustement des années en fonction de la fin de l'exercice fiscal
    current_year_23 = f"{fiscal_year_end}.{year_suffix}"
    previous_year_22 = f"{fiscal_year_end}.{int(year_suffix)-1}"  # Ex: "12.22" ou "03.23"
    previous_year_21 = f"{fiscal_year_end}.{int(year_suffix)-2}"
    previous_year_20 = f"{fiscal_year_end}.{int(year_suffix)-3}"
    previous_year_19 = f"{fiscal_year_end}.{int(year_suffix)-4}"

    valo = pd.read_excel(file_name, sheet_name='Cours_Summary')
    compte_de_resultat = pd.read_excel(file_name, sheet_name='Cours_Table_1')
    ratios_financiers = pd.read_excel(file_name, sheet_name='Cours_Table_3')
    bilan = pd.read_excel(file_name, sheet_name='Cours_Table_2')
    chiffres_daffaires = pd.read_excel(file_name, sheet_name='Cours_Table_4')
    dividende = pd.read_excel(file_name, sheet_name='Consensus_Table_3')
        
    try:
        evol_dividende = pd.read_excel(file_name, sheet_name='Dividendes_Table_1')
    except Exception as e:
        print(f"Pas de tableau de dividende pour {societe_name}. Croissance du dividende seront ignorés.")
        evol_dividende = None
        
    valorisation = pd.to_numeric(valo.iloc[0, 0])
    cours_du_jour = pd.to_numeric(valo.iloc[0, 1])

    compte_de_resultat.set_index('Milliers EUR', inplace=True)
    compte_de_resultat = compte_de_resultat.applymap(lambda x: pd.to_numeric(x.replace(' ', '').replace(',', '.'), errors='coerce'))

    ratios_financiers.set_index('Unnamed: 0', inplace=True)
    ratios_financiers = ratios_financiers.applymap(lambda x: pd.to_numeric(x.replace(' ', '').replace(',', '.'), errors='coerce'))

    bilan.set_index('Milliers EUR', inplace=True)
    cap_propres = pd.to_numeric(bilan.loc['Capitaux propres', current_year_23].replace(' ', ''))
    
    # Vérification et chargement des prévisions si disponibles
    try:
        previsions_resultats = pd.read_excel(file_name, sheet_name='Consensus_Table_4')
        previsions_resultats.set_index('Unnamed: 0', inplace=True)
        cash_flow = pd.to_numeric(previsions_resultats.loc['Cash Flow par action\n                                    (7)', '2023'].replace(' ', '').replace(',', '.'))
    except Exception as e:
        print(f"Le free cash flow ne sera pas calculé pour {societe_name} car l'information n'est pas disponible.")
        cash_flow = None  # Gérer l'absence de cash flow

    # Utiliser l'exercice fiscal dynamique
    taux_de_marge_23 = compte_de_resultat.loc['Résultat net (part du groupe)', current_year_23] / compte_de_resultat.loc[config['produit_net'], f'{fiscal_year_end}.23'] * 100
    taux_de_marge_20 = compte_de_resultat.loc['Résultat net (part du groupe)', previous_year_20] / compte_de_resultat.loc[config['produit_net'], previous_year_20] * 100
    taux_de_marge_21 = compte_de_resultat.loc['Résultat net (part du groupe)', previous_year_21] / compte_de_resultat.loc[config['produit_net'], previous_year_21] * 100
    taux_de_marge_22 = compte_de_resultat.loc['Résultat net (part du groupe)', previous_year_22] / compte_de_resultat.loc[config['produit_net'], previous_year_22] * 100

    tx_marge_moyen_4ans = np.mean([taux_de_marge_20, taux_de_marge_21, taux_de_marge_22, taux_de_marge_23])

    res_par_action_23 = ratios_financiers.loc['Résultat net part du groupe par action (en €)', current_year_23]
    res_par_action_19 = ratios_financiers.loc['Résultat net part du groupe par action (en €)', previous_year_19]

    bna_5ans = (((res_par_action_23 - res_par_action_19) / res_par_action_19) / 5) * 100

    pbv = (valorisation / 1000) / cap_propres

    # Calcul du Price to Cash Flow uniquement si le cash flow est disponible
    if cash_flow is not None:
        pcf = cours_du_jour / cash_flow if cash_flow != 0 else np.nan
    else:
        pcf = np.nan
    per = cours_du_jour / res_par_action_23

    interest_cover = compte_de_resultat.loc[config['resultat_brut'], current_year_23] / compte_de_resultat.loc[config['interet_sur_la_dette'], current_year_23]

    # evol CA
    # Sélectionner les deux dernières colonnes
    last_two_columns = chiffres_daffaires.iloc[:, -2:]
    # Nettoyer les espaces et convertir en numérique pour les deux dernières colonnes
    chiffres_daffaires.iloc[:, -2:] = last_two_columns.apply(lambda col: pd.to_numeric(col.str.replace(r'\s+', '', regex=True), errors='coerce'))
    # Exemple : Récupérer la dernière valeur non nulle dans la derniere col
    last_ca_n = chiffres_daffaires[chiffres_daffaires.iloc[:,-1] != 0].iloc[:,-1].iloc[-1]
    # Exemple : Récupérer la dernière valeur non nulle dans l'avant derniere col
    last_ca_n1 = chiffres_daffaires[chiffres_daffaires.iloc[:,-1] != 0].iloc[:,-2].iloc[-1]
    evol_ca = ((last_ca_n - last_ca_n1)/last_ca_n1)*100
    
    # dividende sur valo
    div_par_action = pd.to_numeric(dividende.iloc[0,1].split("\n")[0].replace(',','.'))
    div_sur_valo = (div_par_action / cours_du_jour) * 100

    # evol dividende
    if evol_dividende is not None:
        try:
            evol_dividende.set_index('Année', inplace=True)
            div_2024 = pd.to_numeric(evol_dividende.loc[2024,'Montant'].split('\xa0€')[0].replace(',','.'))
            div_2019 = pd.to_numeric(evol_dividende.loc[2019,'Montant'].split('\xa0€')[0].replace(',','.'))
            if div_2019 == 0:
                div_2019 = 0.0001
            croissance_div_5_ans = ((div_2024 - div_2019)/div_2019) * 100
            
        except Exception as e:
            croissance_div_5_ans = "pas de dividende versé"
            print(f"Erreur lors du calcul de la croissance du dividende pour {societe_name}: {e}")
    else:
        croissance_div_5_ans = "pas de dividende versé"

    results = {
        'Societe': societe_name,
        'Capitalisation (EUR)': valorisation,
        'Taux de marge 2023 (en %)': taux_de_marge_23,
        'TM sur 4 ans (en %)': tx_marge_moyen_4ans,
        'Croissance BNPA 5 ans (en %)': bna_5ans,
        'Price to Book Value': pbv,
        'Price to Cash Flow': pcf,
        'PER': per,
        'Interest Cover': interest_cover,
        'Evolution du dernier CA': evol_ca,
        '% Dividende': div_sur_valo,
        'Croissance du dividende sur 5 ans (en %)': croissance_div_5_ans
    }

    results_df = pd.DataFrame([results])

        
    # Vérifier si le fichier de sortie existe déjà
    if os.path.exists(output_file):
        # Charger toutes les feuilles existantes dans un dictionnaire de DataFrames
        with pd.ExcelFile(output_file) as reader:
            all_sheets = {sheet_name: reader.parse(sheet_name) for sheet_name in reader.sheet_names}

        # Si la feuille du secteur existe, on la charge
        if secteur_name in all_sheets:
            existing_df = all_sheets[secteur_name]

            # Vérifier si la société existe déjà dans les données
            if societe_name in existing_df['Societe'].values:
                # Mettre à jour la ligne correspondante
                existing_df.loc[existing_df['Societe'] == societe_name] = results_df.values
            else:
                # Ajouter une nouvelle ligne si la société n'existe pas
                existing_df = pd.concat([existing_df, results_df], ignore_index=True)

            # Mettre à jour le dictionnaire avec la nouvelle version de la feuille
            all_sheets[secteur_name] = existing_df
        else:
            # Si la feuille du secteur n'existe pas, la créer avec les nouvelles données
            all_sheets[secteur_name] = results_df

        # Écriture dans le fichier Excel, en conservant toutes les feuilles existantes
        with pd.ExcelWriter(output_file, mode='w') as writer:
            for sheet_name, df in all_sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)

    else:
        # Si le fichier n'existe pas encore, créer un nouveau fichier avec une seule feuille
        with pd.ExcelWriter(output_file, mode='w') as writer:
            results_df.to_excel(writer, sheet_name=secteur_name, index=False)

        
        
def delete_intermediate_file(intermediate_file):
    """Supprime le fichier intermédiaire s'il existe."""
    if os.path.exists(intermediate_file):
        os.remove(intermediate_file)


def main(intermediate_file, output_file):
    # Barre de progression et conteneur de progression dynamique
    progress = st.progress(0)  # Barre de progression
    status_message = st.empty()  # Conteneur unique pour les messages d'étapes (mis à jour dynamiquement)
    total_steps = len(sector_config) * len(company_urls)  # Nombre total d'étapes
    step = 0  # Pour suivre l'avancement

    for sector_name, config in sector_config.items():
        for company_name in config['company']:
            company_info = company_urls.get(company_name)
            if not company_info:
                continue  # Ne pas afficher de message dans l'interface

            try:
                # Suppression du fichier intermédiaire avant de démarrer
                delete_intermediate_file(intermediate_file)

                # Étape 1 : Scraping des données de consensus
                status_message.info(f"Scraping des données de consensus pour {company_name}...")
                html1 = fetch_webpage(company_info['consensus'])
                tables1 = parse_tables(html1)
                save_to_excel(tables1, intermediate_file, sheet_name='Consensus')

                # Étape 2 : Scraping des chiffres clés
                status_message.info(f"Scraping des chiffres clés pour {company_name}...")
                html2 = fetch_webpage(company_info['chiffres_cles'])
                tables2 = parse_tables(html2)
                valorisation, cours_du_jour = get_valorisation_and_cours(html2)
                save_to_excel(tables2, intermediate_file, sheet_name='Cours', valorisation=valorisation, cours_du_jour=cours_du_jour)

                # Étape 3 : Scraping des dividendes
                status_message.info(f"Scraping des dividendes pour {company_name}...")
                html3 = fetch_webpage(company_info['dividendes'])
                tables3 = parse_tables(html3)
                save_to_excel(tables3, intermediate_file, sheet_name='Dividendes')

                # Calcul des indicateurs financiers
                status_message.info(f"Calcul des indicateurs financiers pour {company_name}...")
                calculate_and_store_indicators(intermediate_file, output_file, company_name, sector_name)

                # Mise à jour de la progression
                step += 1
                progress.progress(step / total_steps)

            except Exception as e:
                status_message.error(f"Erreur lors du traitement de {company_name}: {e}")

    # Une fois le processus terminé, remplacez la barre de progression par les résultats
    progress.empty()  # Supprime la barre de progression

    # Afficher les résultats finaux à la place de la barre de progression
    if os.path.exists(output_file):
        result_df = pd.read_excel(output_file)
        status_message.success("Traitement terminé. Voici un aperçu des résultats :")
        status_message.dataframe(result_df)

        # Ajouter un bouton pour télécharger les résultats avec une clé unique
        with open(output_file, "rb") as file:
            status_message.download_button(label="Télécharger les résultats en Excel", data=file, file_name="financial_indicators.xlsx", key="download_button_final")
    else:
        status_message.error("Aucun résultat trouvé.")

# Interface Web avec Streamlit
def run_app():
    st.title("Scraping des données financières")
    st.write("Appuyez sur le bouton ci-dessous pour lancer le scraping et les calculs d'indicateurs.")

    if st.button('Lancer le scraping et les calculs'):
        intermediate_file = r'C:\Users\RAGNAR\OneDrive\Documents\Bourse\DATA\combined_data.xlsx'
        output_file = r'C:\Users\RAGNAR\OneDrive\Documents\Bourse\DATA\financial_indicators.xlsx'
        
        st.write("Traitement en cours...")
        main(intermediate_file, output_file)
        
        st.write("Traitement terminé !")
        
        # Affichage des résultats finaux si vous le souhaitez
        if os.path.exists(output_file):
            result_df = pd.read_excel(output_file)
            st.write("Voici un aperçu des résultats :")
            st.dataframe(result_df)

        # Ajouter un bouton pour télécharger les résultats
        with open(output_file, "rb") as file:
            st.download_button(label="Télécharger les résultats en Excel", data=file, file_name="financial_indicators.xlsx")

if __name__ == '__main__':
    run_app()