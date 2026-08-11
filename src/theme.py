"""Theme injector and custom CSS system matching the reference sidebar UI design."""

import streamlit as st

def apply_theme(role: str = "manager"):
    """Inject custom CSS matching the reference UI design for Manager or Product Sender."""
    
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }
    
    .main .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        max-width: 1380px;
    }

    /* Fixed Dark Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b132b !important;
        border-right: 1px solid #1e293b !important;
        padding-top: 1.5rem !important;
    }
    
    section[data-testid="stSidebar"] * {
        color: #f8fafc !important;
    }

    /* Hide standard radio circle indicators for clean menu items */
    div[data-testid="stSidebar"] div.stRadio [data-testid="stMarkdownContainer"] p {
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stSidebar"] div.stRadio label div[role="radiogroup"] {
        gap: 6px !important;
    }

    div[data-testid="stSidebar"] div.stRadio label {
        padding: 10px 16px !important;
        border-radius: 10px !important;
        cursor: pointer !important;
        transition: all 0.2s ease-in-out !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #94a3b8 !important;
        background: transparent !important;
        margin-bottom: 4px !important;
    }

    div[data-testid="stSidebar"] div.stRadio label:hover {
        background-color: #1c2541 !important;
        color: #ffffff !important;
    }

    div[data-testid="stSidebar"] div.stRadio label[data-checked="true"] {
        background: linear-gradient(135deg, #3a36db, #2563eb) !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.35) !important;
    }

    /* Hide radio dot circle */
    div[data-testid="stSidebar"] div.stRadio label div[data-testid="stRadioButtonIcon"] {
        display: none !important;
    }

    /* Primary Buttons */
    .stButton > button {
        background-color: #2563eb !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.15) !important;
    }

    .stButton > button:hover {
        background-color: #1d4ed8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.25) !important;
    }

    /* Header Banner */
    .role-banner-pill {
        background: linear-gradient(90deg, #1e3a8a, #2563eb);
        color: white;
        padding: 8px 18px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: inline-block;
        margin-bottom: 18px;
        box-shadow: 0 2px 8px rgba(37, 99, 235, 0.25);
    }

    /* Cards System */
    .saas-card-white {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .saas-card-white:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
    }

    /* Status Badges */
    .badge-instock {
        background-color: #dcfce7;
        color: #15803d;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .badge-lowstock {
        background-color: #fef3c7;
        color: #b45309;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }

    .badge-outstock {
        background-color: #fee2e2;
        color: #b91c1c;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        display: inline-block;
    }
    """

    if role == "auth":
        css += """
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        div[data-testid="collapsedControl"] {
            display: none !important;
        }
        button[kind="header"] {
            display: none !important;
        }
        """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
