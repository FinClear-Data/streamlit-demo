import time
import sys
import subprocess
import streamlit as st
import streamlit_authenticator as stauth
from utils.multipage import MultiPage



def build_app():

    # Import all subpages here for cleaner dependency handling
    from subpages import home, charts, chatGPT, map

    app = MultiPage()
    app.add_page('home', 'Home', '🏠', home.app)
    app.add_page('charts', 'Charts', '📊', charts.app)
    app.add_page('chatgpt', 'ChatGPT API', '🧠', chatGPT.app)
    app.add_page('map', 'Map of Sydney', '🗺️', map.app)
    
    return app

def load_secrets():

    # Authentication
    credentials = dict(st.secrets.auth.credentials) # Must copy this as it is modified by stauth
    cookie = st.secrets.auth.cookie
    preauthorised = st.secrets.auth.preauthorised

    if 'authenticator' not in st.session_state:
        st.session_state['authenticator'] = stauth.Authenticate(credentials, cookie.name, cookie.key, int(cookie.expiry_days), preauthorised)

    if 'openai_api_key' not in st.session_state:
        st.session_state['openai_api_key'] = st.secrets.api_keys.openai

def main():

    st.set_page_config(
        page_title='FinClear Streamlit App',
        layout='centered',  # Can be wide
        initial_sidebar_state='auto',  # Best to have auto for mobile
        menu_items={
            'Report a bug': 'mailto:emlyn.evans@finclear.com.au',
            'Get help': 'mailto:emlyn.evans@finclear.com.au',
            'About': 'https://finclear.com.au/'
        }
    )

    # Import all private packages here at the start of the app boot.
    # You must "Reboot App" if you add more dependencies

    # based on https://discuss.streamlit.io/t/pip-installing-from-github/21484/5
    try:
        from toolbox import hi

    # This block executes only on the first run when your package isn't installed
    except ModuleNotFoundError as e:
        sleep_time = 10
        dependency_warning = st.warning(
            f"Installing dependencies, this takes {sleep_time} seconds."
        )

        subprocess.Popen([
            f"{sys.executable} -m pip install git+https://${{github_token}}@github.com/FinClear-Data/toolbox.git"],
            shell=True)

        # wait for subprocess to install package before running your actual code below
        time.sleep(sleep_time)

        # remove the installing dependency warning
        dependency_warning.empty()

    # Load secrets
    load_secrets()

    # Run authentication window
    st.session_state.authenticator.login('Login')

    # Control flow of authentication
    if st.session_state['authentication_status']:

        # Build app on login
        if 'app' not in st.session_state:
            st.session_state['app'] = build_app()
        
        st.session_state.app.run()

    elif st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect')

    elif st.session_state["authentication_status"] == None:
        st.info('Please enter your username and password')

        # Reset app when logout
        if 'app' in st.session_state:
            del st.session_state['app']


main()
