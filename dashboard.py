import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objs as go
import os
from dash.dependencies import Input, Output


# Chargement des données depuis le fichier CSV
def load_data():
    if os.path.exists('eurostoxx50_data.csv'):
        df = pd.read_csv('eurostoxx50_data.csv', names=['Date', 'Index', 'Price'])

        # Nettoyage de la colonne Date
        df['Date'] = df['Date'].str.replace(' CEST', '', regex=False)
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Conversion des prix en float
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

        return df.dropna()
    else:
        return pd.DataFrame(columns=['Date', 'Index', 'Price'])


# Création de l'app Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Graphique Eurostoxx 50 - Données Temps Réel"),

    dcc.Graph(id='price-graph', figure={}),
    dcc.Graph(id='volatility-graph', figure={})
])


@app.callback(
    Output('price-graph', 'figure'),
    Output('volatility-graph', 'figure'),
    Input('price-graph', 'id')  # Déclenchement initial
)
def update_graphs(_):
    df = load_data()
    if df.empty:
        return {}, {}

    # Graphique principal : prix
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Prix'
    ))
    price_fig.update_layout(
        title='Evolution du prix Eurostoxx 50',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark'
    )

    # Calcul de la volatilité
    now = df['Date'].max()
    vol_10min = df[df['Date'] > now - pd.Timedelta(minutes=10)]['Price'].std()
    vol_30min = df[df['Date'] > now - pd.Timedelta(minutes=30)]['Price'].std()
    vol_2h = df[df['Date'] > now - pd.Timedelta(hours=2)]['Price'].std()

    # Graphique secondaire : histogramme de volatilité
    vol_fig = go.Figure(go.Bar(
        x=['10 min', '30 min', '2 h'],
        y=[vol_10min, vol_30min, vol_2h],
        marker_color='orange'
    ))
    vol_fig.update_layout(
        title='Volatilité sur différentes périodes',
        xaxis_title='Période',
        yaxis_title='Écart-type (volatilité)',
        template='plotly_dark'
    )

    return price_fig, vol_fig


# Lancement du serveur Dash sur 0.0.0.0:8050
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
