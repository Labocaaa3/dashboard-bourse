import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import numpy as np
import os

# Créer l'application Dash
app = dash.Dash(__name__)

import pandas as pd

def load_data():
    if os.path.exists('eurostoxx50_data.csv'):
        try:
            df = pd.read_csv('eurostoxx50_data.csv')
            # Vérifier si la colonne 'date' existe (en minuscules)
            if 'date' in df.columns:
                df['Date'] = df['date']
            # Suppression de la partie du fuseau horaire (CEST) et de l'année
            df['Date'] = df['Date'].str.replace(r' \w{3} \d{4}', '', regex=True)  # Suppression du CEST et de l'année
            df['Date'] = pd.to_datetime(df['Date'], format='%a %b %d %H:%M:%S', errors='coerce')
            df = df.sort_values(by='Date')
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
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
    if len(recent_df) < 2:
        return None
    prices = recent_df['Price'].astype(float)
    returns = prices.pct_change().dropna()  # Variation en pourcentage
    volatility = np.std(returns) * np.sqrt(len(returns)) * 100  # Volatilité annualisée approximative
    return volatility

# Layout de l'application
app.layout = html.Div([
    html.H1("Dashboard Eurostoxx50"),
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
        return go.Figure(), go.Figure()  # Renvoie des graphiques vides si aucune donnée n'est trouvée

    # Graphique des prix
    price_fig = go.Figure(data=[go.Scatter(x=df['Date'], y=df['Price'], mode='lines+markers', name='Prix Eurostoxx 50')])
    price_fig.update_layout(title='Price Eurostoxx 50',
                            xaxis_title='Date',
                            yaxis_title='Price',
                            template='plotly_dark')

    # Calcul de la volatilité
    vol_10min = calculate_volatility(df, 10)
    vol_30min = calculate_volatility(df, 30)
    vol_60min = calculate_volatility(df, 60)  # Volatilité sur 1 heure

    # Préparation des graphiques de volatilité
    vol_fig = go.Figure()
    vol_fig.add_trace(go.Bar(x=['Volatilité 10 min'], y=[vol_10min if vol_10min else 0], name='Volatilité 10 min'))
    vol_fig.add_trace(go.Bar(x=['Volatilité 30 min'], y=[vol_30min if vol_30min else 0], name='Volatilité 30 min'))
    vol_fig.add_trace(go.Bar(x=['Volatilité 1 heure'], y=[vol_60min if vol_60min else 0], name='Volatilité 1 heure'))

    vol_fig.update_layout(title='Volatilités calculées',
                          xaxis_title='Période',
                          yaxis_title='Volatilité en %',
                          yaxis=dict(range=[0, 3]),
                          template='plotly_dark')

    return price_fig, vol_fig

# Lancer l'application
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
