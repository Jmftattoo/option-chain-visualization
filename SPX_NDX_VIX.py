from convexlib.api import ConvexApi
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls
import os
# Set up your credentials with your username and API key
chart_studio.tools.set_credentials_file(username=os.getenv('CHART_STUDIO_USER'), api_key=os.getenv('CHART_STUDIO_KEY'))

# Initialize the ConvexApi instance
convex_instance = ConvexApi(os.getenv('CONVEX_EMAIL'), os.getenv('CONVEX_PASSWORD'), os.getenv('CONVEX_ENV'))

def fetch_and_plot_gamma_by_strike_plotly(symbols):
    # Adjusting subplot creation for vertical stacking
    fig = make_subplots(rows=len(symbols), cols=1, subplot_titles=symbols, vertical_spacing=0.1)

    for idx, symbol in enumerate(symbols, start=1):
        row = idx
        col = 1

        # Fetching option chain data
        response = convex_instance.get_chain(symbol, params=["gxvolm", "strike", "opt_kind"], exps=[0], rng=0.04)
        chain_data = response['data'][0]['chain']
        
        # Initialize dictionaries to hold gamma values by strike for calls and puts
        call_gamma_by_strike = {}
        put_gamma_by_strike = {}
        
        # Parsing the data
        for item in chain_data[0][1]:
            strike = item[0]
            for option in item[1:]:
                gamma_value = option[1]
                opt_kind = option[3]
                
                if opt_kind == 'Call':
                    call_gamma_by_strike[strike] = gamma_value
                elif opt_kind == 'Put':
                    put_gamma_by_strike[strike] = gamma_value
        
        # Sorting strikes for plotting
        strikes = sorted(set(call_gamma_by_strike.keys()) | set(put_gamma_by_strike.keys()))
        
        # Extracting gamma values in sorted order of strikes
        call_gammas = [call_gamma_by_strike[strike] for strike in strikes]
        put_gammas = [put_gamma_by_strike[strike] for strike in strikes]
        
        # Adding call and put gamma bars on a single vertical axis for each stock
        fig.add_trace(go.Bar(x=call_gammas, y=strikes, name='Calls', marker_color='blue', orientation='h'), row=row, col=col)
        fig.add_trace(go.Bar(x=put_gammas, y=strikes, name='Puts', marker_color='red', orientation='h'), row=row, col=col)

    # Adjusting layout for better visibility of stacked charts
    fig.update_layout(
        template="plotly_dark",
        title="SPX/NDX Gamma x Open Interest",
        xaxis_title="Gamma",
        yaxis_title="Strike",
        height=1000 * len(symbols),  # Adjust height based on number of symbols
        width=1200
    )

    # Upload the figure to Chart Studio and get the URL
    url = py.plot(fig, filename='SPX_NDX_Gamma', auto_open=True)
    print("Chart URL: ", url)

# Example usage with SPX/NDX stocks
SPX_NDX_symbols = ["SPX", "NDX"]
fetch_and_plot_gamma_by_strike_plotly(SPX_NDX_symbols)