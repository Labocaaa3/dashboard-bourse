import pandas as pd
import numpy as np
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import os

# Créer l'application Dash
app = Dash(__name__)

def load_data():
    if os.path.exists('eurostoxx50_data.csv'):
        try:
            df = pd.read_csv('eurostoxx50_data.csv', names=['Date', 'Index', 'Price'])
            # Supprimer le fuseau horaire "CEST" dans les chaînes de dates
            df['Date'] = df['Date'].str.replace(r' CEST', '', regex=True)

            # Conversion en datetime
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

            # Nettoyage
            df = df.dropna(subset=['Date', 'Price'])
            df = df.sort_values(by='Date')
            return df

        except Exception as e:
            print(f"❌ Erreur lors du chargement du fichier : {e}")
            return pd.DataFrame(columns=['Date', 'Index', 'Price'])
    else:
        print("❌ Fichier 'eurostoxx50_data.csv' introuvable.")
        return pd.DataFrame(columns=['Date', 'Index', 'Price'])

# Fonction pour calculer la volatilité
def calculate_volatility(df, interval_minutes=60):
    # Filtrer les données des dernières "interval_minutes"
    recent_df = df[df['Date'] > (df['Date'].max() - pd.Timedelta(minutes=interval_minutes))]
    if len(recent_df) < 2:  # Si pas assez de données, retour vide
        return None
    prices = recent_df['Price'].astype(float)
    returns = prices.pct_change().dropna()  # Variation en pourcentage
    volatility = np.std(returns) * np.sqrt(len(returns))  # Volatilité annualisée approximative
    return volatility

# Layout de l'application
app.layout = html.Div([
    html.H1("Dashboard Eurostoxx 50 en Temps Réel"),
    dcc.Graph(id='live-graph-price'),
    dcc.Graph(id='live-graph-volatility'),
    dcc.Interval(
        id='interval-component',
        interval=5*60*1000,  # Actualisation toutes les 5 minutes
        n_intervals=0
    )
])

# Callback pour mettre à jour les graphiques
@app.callback(
    [Output('live-graph-price', 'figure'),
     Output('live-graph-volatility', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    df = load_data()
    if df.empty:
        return go.Figure(), go.Figure()

    # Graphique des prix
    price_fig = go.Figure(data=[
        go.Scatter(
            x=df['Date'],
            y=df['Price'],
            mode='lines+markers',
            name='Prix Eurostoxx 50'
        )
    ])
    price_fig.update_layout(
        title='Prix Eurostoxx 50 en temps réel',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark'
    )

    # Calcul de la volatilité sur 3 intervalles
    vol_2h = calculate_volatility(df, interval_minutes=120)
    vol_30min = calculate_volatility(df, interval_minutes=30)
    vol_10min = calculate_volatility(df, interval_minutes=10)

    # Graphique de la volatilité en barres
    vol_fig = go.Figure(data=[
        go.Bar(
            x=['2h', '30min', '10min'],
            y=[vol_2h or 0, vol_30min or 0, vol_10min or 0],
            name='Volatilité'
        )
    ])
    vol_fig.update_layout(
        title="Volatilité de l'Eurostoxx 50",
        xaxis_title='Période',
        yaxis_title='Volatilité',
        yaxis=dict(range=[0, 2]),
        template='plotly_dark'
    )

    return price_fig, vol_fig

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
