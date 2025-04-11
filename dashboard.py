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
    dcc.Graph(id='price-graph', figure={})
])

# Callback pour initialiser le graphe au lancement
@app.callback(
    Output('price-graph', 'figure'),
    Input('price-graph', 'id')  # Juste pour déclencher une première fois
)
def update_graph(_):
    df = load_data()
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Prix'
    ))

    fig.update_layout(
        title='Evolution du prix Eurostoxx 50',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark'
    )
    return fig

# Lancement du serveur Dash sur 0.0.0.0:8050
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
