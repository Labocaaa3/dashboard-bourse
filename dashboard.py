import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objs as go
import os
from dash.dependencies import Input, Output

# Chargement des données depuis le fichier CSV
def load_data():
    if os.path.exists('eurostoxx50_data.csv'):
        try:
            df = pd.read_csv('eurostoxx50_data.csv', names=['Date', 'Index', 'Price'])

            print(f"[INFO] {len(df)} lignes chargées depuis le CSV.")

            # Nettoyage de la colonne Date
            df['Date'] = df['Date'].str.replace(' CEST', '', regex=False)

            # Essayer format ISO
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
            mask_na = df['Date'].isna()
            if mask_na.any():
                print(f"[INFO] {mask_na.sum()} dates ISO non reconnues, tentative format texte long...")
                df.loc[mask_na, 'Date'] = pd.to_datetime(df.loc[mask_na, 'Date'], errors='coerce', format='%a %b %d %H:%M:%S %Y')

            # Conversion des prix
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

            # Drop les lignes invalides
            df_clean = df.dropna()

            print(f"[INFO] {len(df_clean)} lignes valides après nettoyage.")
            return df_clean

        except Exception as e:
            print(f"[ERROR] Erreur lors du chargement des données : {e}")
            return pd.DataFrame(columns=['Date', 'Index', 'Price'])
    else:
        print("[WARNING] Le fichier CSV n'existe pas.")
        return pd.DataFrame(columns=['Date', 'Index', 'Price'])


# Création de l'app Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Graphique Eurostoxx 50 - Données Temps Réel"),
    dcc.Graph(id='price-graph', figure={})
])

# Callback pour initialiser le graphe
@app.callback(
    Output('price-graph', 'figure'),
    Input('price-graph', 'id')  # juste pour déclencher une première fois
)
def update_graph(_):
    df = load_data()

    if df.empty:
        print("[WARNING] Données vides - aucun graphique à afficher.")
        return go.Figure(layout={'title': 'Aucune donnée disponible'})

    fig = go.Figure()

    # Courbe des prix
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Prix'
    ))

    # Histogramme de volatilité sur 10min, 30min, 2h (écart-type glissant)
    df.set_index('Date', inplace=True)
    df = df.sort_index()

    try:
        vol_10min = df['Price'].rolling('10min').std().mean()
        vol_30min = df['Price'].rolling('30min').std().mean()
        vol_2h = df['Price'].rolling('2h').std().mean()

        print(f"[INFO] Volatilités calculées: 10min={vol_10min:.2f}, 30min={vol_30min:.2f}, 2h={vol_2h:.2f}")

        fig.add_trace(go.Bar(
            x=['10min', '30min', '2h'],
            y=[vol_10min, vol_30min, vol_2h],
            name='Volatilité',
            marker_color=['red', 'orange', 'blue'],
            opacity=0.6
        ))

    except Exception as e:
        print(f"[ERROR] Erreur dans le calcul de la volatilité : {e}")

    fig.update_layout(
        title='Evolution du prix Eurostoxx 50',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark',
        yaxis_range=[0, 3]  # optionnel pour cadrer le y
    )

    return fig


# Lancement du serveur Dash
if __name__ == '__main__':
    print("[INFO] Lancement du serveur Dash sur 0.0.0.0:8050")
    app.run(debug=True, host='0.0.0.0', port=8050)
