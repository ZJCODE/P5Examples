import streamlit as st
from utils import draw_script
import requests
from streamlit_js_eval import streamlit_js_eval
from streamlit_pills import pills

# Set page config
st.set_page_config(page_title='Template',
                   page_icon='🎨', 
                   layout='wide',
                   initial_sidebar_state='collapsed')

from streamlit_navigation_bar import st_navbar

styles = {
    "nav": {
        "background-color": "white",
        "justify-content": "left",
    },
    "span": {
        "color": "white",
        "padding-left": "48px",
    },
    "active": {
        "background-color": "white",
        "color": "#f58025",
        "font-size": "25px",
        "font-weight": "bold",
    }
}


page_select = st_navbar(    
                 pages=["Template"],
                 styles = styles,
                 options={"use_padding": False,"show_menu": False,"show_sidebar": False}
                 )


st.title("Template")