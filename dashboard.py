import pandas as pd
from dash import Dash, dcc, html
import plotly.graph_objs as go
import os
from dash.dependencies import Input, Output

def load_data():
    if not os.path.exists('eurostoxx50_data.csv'):
        print("[ERROR] Fichier CSV non trouvé.")
        return pd.DataFrame(columns=['Date', 'Index', 'Price'])

    df = pd.read_csv('eurostoxx50_data.csv', names=['Date', 'Index', 'Price'])

    # Nettoyage des dates
    df['Date'] = df['Date'].str.replace(' CEST', '', regex=False)
    
    # Tentative 1 : ISO
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    mask_na = df['Date'].isna()

    # Tentative 2 : format texte long
    if mask_na.any():
        df.loc[mask_na, 'Date'] = pd.to_datetime(df.loc[mask_na, 'Date'], errors='coerce', format='%a %b %d %H:%M:%S %Y')
    
    # Erreur persistante ?
    if df['Date'].isna().any():
        print("[ERROR] Certaines dates sont toujours invalides après les conversions.")
        print(df[df['Date'].isna()].head())  # afficher les lignes problématiques

    # Prix
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    return df.dropna()

# App Dash
app = Dash(__name__)

app.layout = html.Div(children=[
    html.H1("Graphique Eurostoxx 50 - Données Temps Réel"),
    dcc.Graph(id='price-graph', figure={})
])

@app.callback(
    Output('price-graph', 'figure'),
    Input('price-graph', 'id')
)
def update_graph(_):
    df = load_data()

    if df.empty:
        print("[ERROR] Données vides après parsing.")
        return go.Figure(layout={'title': 'Erreur: Données vides'})

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Price'],
        mode='lines+markers',
        name='Prix'
    ))

    df.set_index('Date', inplace=True)
    df.sort_index(inplace=True)

    try:
        vol_10min = df['Price'].rolling('10min').std().mean()
        vol_30min = df['Price'].rolling('30min').std().mean()
        vol_2h = df['Price'].rolling('2h').std().mean()
    except Exception as e:
        print(f"[ERROR] Problème lors du calcul de la volatilité : {e}")
        vol_10min = vol_30min = vol_2h = 0

    fig.add_trace(go.Bar(
        x=['10min', '30min', '2h'],
        y=[vol_10min, vol_30min, vol_2h],
        name='Volatilité',
        marker_color=['red', 'orange', 'blue'],
        opacity=0.6
    ))

    fig.update_layout(
        title='Evolution du prix Eurostoxx 50',
        xaxis_title='Date',
        yaxis_title='Prix',
        template='plotly_dark',
        yaxis_range=[0, 3]
    )

    return fig


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
