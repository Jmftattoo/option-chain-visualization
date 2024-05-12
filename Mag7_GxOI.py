import os
from convexlib.api import ConvexApi
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import chart_studio
import chart_studio.plotly as py
import chart_studio.tools as tls

# Access credentials from environment variables
chart_studio.tools.set_credentials_file(username=os.getenv('CHART_STUDIO_USER'), api_key=os.getenv('CHART_STUDIO_KEY'))
 
# Commented out the print statements as per the instructions
# print("Email:", os.getenv('CONVEX_EMAIL'))
# print("Password:", os.getenv('CONVEX_PASSWORD'))
# print("Environment:", os.getenv('CONVEX_ENV'))

try:
    # Initialize the ConvexApi instance with environment variables
    convex_instance = ConvexApi(os.getenv('CONVEX_EMAIL'), os.getenv('CONVEX_PASSWORD'), os.getenv('CONVEX_ENV'))
    # Commented out the success message print statement
    # print("Initialized ConvexApi successfully.")
except Exception as e:
    print("Failed to initialize ConvexApi:", str(e))

# Proceed with further API usage and add try-except blocks to catch and log errors
def fetch_and_plot_gamma_by_strike_plotly(symbols):
    # Creating a subplot with 4 rows and 2 columns for the Mag7 stocks
    fig = make_subplots(rows=4, cols=2, subplot_titles=symbols, vertical_spacing=0.05, horizontal_spacing=0.05)

    for idx, symbol in enumerate(symbols, start=1):
        row = (idx - 1) // 2 + 1
        col = idx % 2 if idx % 2 != 0 else 2

        # Fetching option chain data
        response = convex_instance.get_chain(symbol, params=["gxoi", "strike", "opt_kind"], exps=[0], rng=0.25)
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

    # Set the layout to use the Plotly Dark theme and add axis titles
    fig.update_layout(
        template="plotly_dark",
        title="Mag 7 Gamma x Open Interest",
        xaxis_title="Gamma",
        yaxis_title="Strike",
        height=2000,
        width=1200
    )

    # Upload the figure to Chart Studio and get the URL
    url = py.plot(fig, filename='MAG7_Gamma', auto_open=True)
    print("Chart URL: ", url)

# Example usage with Mag7 stocks
mag7_symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "META", "TSLA", "NVDA"]
fetch_and_plot_gamma_by_strike_plotly(mag7_symbols)
