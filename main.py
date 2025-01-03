import sqlite3
import pandas as pd
import streamlit as st
import json

with open("config.json", "r") as config_file:
    config = json.load(config_file)

DB_PATH = config["DB_PATH"]

def execute_query(sql, params=None, fetch=False):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    if fetch:
        result = cursor.fetchall()
    conn.commit()
    conn.close()
    if fetch:
        return result

st.title("Suivi d'Activité Physique")

categorie = st.radio("Choisissez une catégorie :", ["Cardio", "Musculation"])

def get_exercises(categorie):
    table = "cardio" if categorie == "Cardio" else "musculation"
    result = execute_query(f"""
        SELECT exercice, COUNT(*) as frequence
        FROM {table}
        GROUP BY exercice
        ORDER BY frequence DESC
    """, fetch=True)
    return [row[0] for row in result]

tab_add, tab_view, tab_stats = st.tabs(["Ajouter une activité", "Consulter les données", "Statistiques"])

with tab_add:
    st.subheader("Ajouter une nouvelle activité")

    with st.form("ajouter_activite_form"):
        col1, col2 = st.columns(2)

        with col1:
            st.write("Informations générales")
            date = st.date_input("Date")
            exercice_selectionne = st.selectbox(
                "Exercice",
                options=["Nouveau"] + get_exercises(categorie),
                index=0
            )
            exercice = exercice_selectionne if exercice_selectionne != "Nouveau" else st.text_input("Nom du nouvel exercice")

        with col2:
            st.write("Détails de l'activité")
            if categorie == "Cardio":
                distance = st.number_input("Distance (km)", min_value=0.0, step=0.1)
                temps = st.number_input("Temps (min)", min_value=0.0, step=1.0)
            elif categorie == "Musculation":
                poids = st.number_input("Poids (kg)", min_value=0.0, step=0.5)
                series_x_reps = st.text_input("Séries x Répétitions")

        commentaires = st.text_area("Commentaires")
        submit = st.form_submit_button("Ajouter")

        if submit:
            if exercice_selectionne == "Nouveau" and not exercice.strip():
                st.error("Veuillez entrer un nom pour le nouvel exercice.")
            else:
                if categorie == "Cardio":
                    execute_query(
                        "INSERT INTO cardio (date, exercice, distance, temps, commentaires) VALUES (?, ?, ?, ?, ?)",
                        (str(date), exercice, distance, temps, commentaires)
                    )
                elif categorie == "Musculation":
                    execute_query(
                        "INSERT INTO musculation (date, exercice, poids, series_x_reps, commentaires) VALUES (?, ?, ?, ?, ?)",
                        (str(date), exercice, poids, series_x_reps, commentaires)
                    )
                st.success(f"Nouvelle activité ajoutée : {exercice}")

with tab_view:
    st.subheader("Consulter les données existantes")

    if categorie == "Cardio":
        cardio_data = execute_query("SELECT * FROM cardio", fetch=True)
        cardio_df = pd.DataFrame(cardio_data, columns=["ID", "Date", "Exercice", "Distance (km)", "Temps (min)", "Commentaires"])

        if not cardio_df.empty:
            cardio_df['Date'] = pd.to_datetime(cardio_df['Date']).dt.date

            st.write("Filtrer par date")
            date_min = cardio_df['Date'].min()
            date_max = cardio_df['Date'].max()
            date_range = st.date_input("Plage de dates", [date_min, date_max])

            if len(date_range) == 2:
                start_date, end_date = date_range
                cardio_df = cardio_df[(cardio_df['Date'] >= start_date) & (cardio_df['Date'] <= end_date)]

            st.write("Tableau des données")
            st.dataframe(cardio_df.style.format({"Distance (km)": "{:.2f}", "Temps (min)": "{:.0f}"}))

            st.write("Vue par jour")
            data_by_day = cardio_df.groupby("Date").agg({"Distance (km)": "sum", "Temps (min)": "sum"}).reset_index()
            st.bar_chart(data_by_day.set_index("Date"))

        else:
            st.write("Aucune donnée cardio disponible.")

    elif categorie == "Musculation":
        musculation_data = execute_query("SELECT * FROM musculation", fetch=True)
        musculation_df = pd.DataFrame(musculation_data, columns=["ID", "Date", "Exercice", "Poids (kg)", "Séries x Répétitions", "Commentaires"])

        if not musculation_df.empty:
            musculation_df['Date'] = pd.to_datetime(musculation_df['Date']).dt.date

            st.write("Filtrer par date")
            date_min = musculation_df['Date'].min()
            date_max = musculation_df['Date'].max()
            date_range = st.date_input("Plage de dates", [date_min, date_max])

            if len(date_range) == 2:
                start_date, end_date = date_range
                musculation_df = musculation_df[(musculation_df['Date'] >= start_date) & (musculation_df['Date'] <= end_date)]

            st.write("Tableau des données")
            st.dataframe(musculation_df.style.format({"Poids (kg)": "{:.1f}"}))

            st.write("Vue par jour")
            data_by_day = musculation_df.groupby("Date").agg({"Poids (kg)": "mean"}).reset_index()
            st.bar_chart(data_by_day.set_index("Date"))

        else:
            st.write("Aucune donnée de musculation disponible.")

with tab_stats:
    st.subheader("Statistiques et Graphiques")

    if categorie == "Cardio":
        cardio_data = execute_query("SELECT * FROM cardio", fetch=True)
        cardio_df = pd.DataFrame(cardio_data, columns=["ID", "Date", "Exercice", "Distance (km)", "Temps (min)", "Commentaires"])

        if not cardio_df.empty:
            exercice_selectionne = st.selectbox("Choisir un exercice :", cardio_df["Exercice"].unique())

            exercice_df = cardio_df[cardio_df["Exercice"] == exercice_selectionne]
            exercice_df['Date'] = pd.to_datetime(exercice_df['Date']).dt.date

            st.write(f"Progression de la distance pour {exercice_selectionne}")
            progression_distance = exercice_df.groupby("Date")["Distance (km)"].sum().reset_index()
            st.line_chart(progression_distance.set_index("Date"))

            st.write(f"Progression du temps pour {exercice_selectionne}")
            progression_temps = exercice_df.groupby("Date")["Temps (min)"].sum().reset_index()
            st.line_chart(progression_temps.set_index("Date"))

        else:
            st.write("Aucune donnée cardio disponible pour les statistiques.")

    elif categorie == "Musculation":
        musculation_data = execute_query("SELECT * FROM musculation", fetch=True)
        musculation_df = pd.DataFrame(musculation_data, columns=["ID", "Date", "Exercice", "Poids (kg)", "Séries x Répétitions", "Commentaires"])

        if not musculation_df.empty:
            exercice_selectionne = st.selectbox("Choisir un exercice :", musculation_df["Exercice"].unique())

            exercice_df = musculation_df[musculation_df["Exercice"] == exercice_selectionne]
            exercice_df['Date'] = pd.to_datetime(exercice_df['Date']).dt.date

            st.write(f"Progression des poids pour {exercice_selectionne}")
            progression_poids = exercice_df.groupby("Date")["Poids (kg)"].mean().reset_index()
            st.line_chart(progression_poids.set_index("Date"))

            st.write(f"Progression des séries pour {exercice_selectionne}")
            exercice_df['Total Séries'] = exercice_df['Séries x Répétitions'].apply(
                lambda x: sum(int(rep.split('x')[0]) for rep in x.split(';')) if pd.notnull(x) else 0
            )
            progression_series = exercice_df.groupby("Date")["Total Séries"].sum().reset_index()
            st.line_chart(progression_series.set_index("Date"))

        else:
            st.write("Aucune donnée de musculation disponible pour les statistiques.")
