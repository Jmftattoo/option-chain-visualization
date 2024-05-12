# Import necessary libraries
import dash
from dash import dcc, html, Input, Output
import os
from convexlib.api import ConvexApi
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls

# Set up Chart Studio credentials
chart_studio.tools.set_credentials_file(username=os.getenv('CHART_STUDIO_USER'), api_key=os.getenv('CHART_STUDIO_KEY'))

# Initialize the ConvexApi instance
convex_instance = ConvexApi(os.getenv('CONVEX_EMAIL'), os.getenv('CONVEX_PASSWORD'), os.getenv('CONVEX_ENV'))

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the app
app.layout = html.Div([
    dcc.RadioItems(
        id='symbol-set',
        options=[
            {'label': 'Mag7 Stocks', 'value': 'mag7'},
            {'label': 'SPX/NDX', 'value': 'spx_ndx'}
        ],
        value='mag7'
    ),
    dcc.Graph(id='gamma-plot')
])

# Define callback to update the graph based on selected symbol set
@app.callback(
    Output('gamma-plot', 'figure'),
    Input('symbol-set', 'value')
)
def update_graph(selected_set):
    if selected_set == 'mag7':
        symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "META", "TSLA", "NVDA"]
        return fetch_and_plot_gamma_by_strike_plotly(symbols, rows=4, cols=2, subplot_spacing=(0.05, 0.05), filename='MAG7_Gamma')
    elif selected_set == 'spx_ndx':
        symbols = ["SPX", "NDX"]
        return fetch_and_plot_gamma_by_strike_plotly(symbols, rows=len(symbols), cols=1, subplot_spacing=(0.1, 0), filename='SPX_NDX_Gamma')

def fetch_and_plot_gamma_by_strike_plotly(symbols, rows, cols, subplot_spacing, filename):
    fig = make_subplots(rows=rows, cols=cols, subplot_titles=symbols, vertical_spacing=subplot_spacing[0], horizontal_spacing=subplot_spacing[1])
    for idx, symbol in enumerate(symbols, start=1):
        row = (idx - 1) // cols + 1
        col = idx % cols if idx % cols != 0 else cols
        response = convex_instance.get_chain(symbol, params=["gxoi", "strike", "opt_kind"], exps=[0], rng=0.25)
        chain_data = response['data'][0]['chain']
        call_gamma_by_strike = {}
        put_gamma_by_strike = {}
        for item in chain_data[0][1]:
            strike = item[0]
            for option in item[1:]:
                gamma_value = option[1]
                opt_kind = option[3]
                if opt_kind == 'Call':
                    call_gamma_by_strike[strike] = gamma_value
                elif opt_kind == 'Put':
                    put_gamma_by_strike[strike] = gamma_value
        strikes = sorted(set(call_gamma_by_strike.keys()) | set(put_gamma_by_strike.keys()))
        call_gammas = [call_gamma_by_strike[strike] for strike in strikes]
        put_gammas = [put_gamma_by_strike[strike] for strike in strikes]
        fig.add_trace(go.Bar(x=call_gammas, y=strikes, name='Calls', marker_color='blue', orientation='h'), row=row, col=col)
        fig.add_trace(go.Bar(x=put_gammas, y=strikes, name='Puts', marker_color='red', orientation='h'), row=row, col=col)
    fig.update_layout(
        template="plotly_dark",
        title=f"{filename} Gamma x Open Interest",
        xaxis_title="Gamma",
        yaxis_title="Strike",
        height=1000 * rows,
        width=1200
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)