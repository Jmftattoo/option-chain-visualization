import os
import subprocess
import streamlit as st

def install_private_repo():
    try:
        username = st.secrets["repo"]["username"]
        password = st.secrets["repo"]["password"]
        repo_url = f"https://{username}:{password}@github.com/Jmftattoo/convexlib.git"
        result = subprocess.run(["pip", "install", f"git+{repo_url}#egg=convexlib"], check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        error_message = f"Failed to install the repository. Command output:\n{e.stdout}\nError output:\n{e.stderr}"
        st.error(error_message)
        raise Exception(error_message)

install_private_repo()

from SPX_NDX_VIX import fetch_and_plot_gamma_by_strike_plotly as fetch_spx_ndx
from Mag7_GxOI import fetch_and_plot_gamma_by_strike_plotly as fetch_mag7

# Access other secrets
api_key = st.secrets["CHART_STUDIO_KEY"]

st.title('Option Chain Gamma Visualization')

# Dropdown to select the dataset
option = st.selectbox(
    'Choose a dataset to visualize',
    ('SPX/NDX', 'Mag7')
)

# Button to fetch and display data
if st.button('Fetch and Display Data'):
    if option == 'SPX/NDX':
        fetch_spx_ndx(["SPX", "NDX"], api_key=api_key)
    elif option == 'Mag7':
        fetch_mag7(["AAPL", "AMZN", "GOOGL", "MSFT", "META", "TSLA", "NVDA"], api_key=api_key)

    st.success('Data fetched and displayed successfully!')

# Instructions or additional information
st.write("Select a dataset from the dropdown and click the button to visualize the option chain gamma values.")
