import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objs as go
import os
from dash.dependencies import Input, Output
import numpy as np

# Chargement des données depuis le fichier CSV
def load_data():
    if os.path.exists('eurostoxx50_data.csv'):
        df = pd.read_csv('eurostoxx50_data.csv', names=['Date', 'Index', 'Price'])

        # Nettoyage : enlever " CEST"
        df['Date'] = df['Date'].str.replace(' CEST', '', regex=False)

        # Essayer les deux formats de date
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%a %b %d %H:%M:%S %Y')
        df.loc[df['Date'].isna(), 'Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # Conversion prix
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

        return df.dropna()
    else:
        return pd.DataFrame(columns=['Date', 'Index', 'Price'])

# Calcule la volatilité pour un intervalle (rolling std)
def calculate_volatility(df, window_minutes):
    df_sorted = df.sort_values('Date')
    df_sorted = df_sorted.set_index('Date').resample(f'{window_minutes}T').last()
    return df_sorted['Price'].pct_change().rolling(2).std().dropna().mean() * 100

# Création app Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Graphique Eurostoxx 50 - Données Temps Réel"),

    dcc.Graph(id='price-graph', figure={}),

    html.H2("Volatilité Moyenne (%)"),
    dcc.Graph(id='volatility-graph', figure={})
])

@app.callback(
    Output('price-graph', 'figure'),
    Output('volatility-graph', 'figure'),
    Input('price-graph', 'id')  # juste déclencheur
)
def update_graph(_):
    df = load_data()

    # --- Graphe des prix ---
    price_fig = go.Figure()
    price_fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Prix'
    ))
    price_fig.update_layout(
        title='Évolution du prix Eurostoxx 50',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark'
    )

    # --- Histogramme de volatilité ---
    vol_10 = calculate_volatility(df, 10)
    vol_30 = calculate_volatility(df, 30)
    vol_120 = calculate_volatility(df, 120)

    vol_fig = go.Figure()
    vol_fig.add_trace(go.Bar(x=['10 min', '30 min', '2h'], y=[vol_10, vol_30, vol_120],
                             marker=dict(color=['red', 'green', 'blue'], line=dict(width=0.5))))
    vol_fig.update_layout(
        yaxis=dict(range=[0, 3]),
        bargap=0.3,
        title='Volatilité moyenne (écart-type des variations %)',
        xaxis_title='Fenêtre',
        yaxis_title='Volatilité (%)',
        template='plotly_dark'
    )

    return price_fig, vol_fig

# Lancement du serveur
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
