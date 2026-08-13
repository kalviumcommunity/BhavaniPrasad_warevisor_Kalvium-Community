"""Theme injector and custom CSS system for Dark Blue / Navy Enterprise SaaS UI."""

import streamlit as st

def apply_theme(role: str = "manager"):
    """Inject global CSS rules and Tailwind CSS v3 Play CDN for Dark Blue / Navy Enterprise SaaS UI."""
    
    # Inject Tailwind CSS v3 Play CDN
    st.markdown("""
        <script src="https://cdn.tailwindcss.com"></script>
        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            navy: {
                                950: '#07111F',
                                900: '#060F1F',
                                850: '#0B172A',
                                800: '#101D31',
                                750: '#111F35',
                                700: '#1E293B',
                                650: '#26364D'
                            },
                            brand: {
                                500: '#3b82f6',
                                600: '#2563eb',
                                700: '#1d4ed8',
                            }
                        }
                    }
                }
            }
        </script>
    """, unsafe_allow_html=True)

    sidebar_bg = "#060F1F"
    sidebar_active_bg = "linear-gradient(135deg, #2563eb, #1d4ed8)" if role == "manager" else "linear-gradient(135deg, #059669, #047857)"
    btn_bg = "#2563eb" if role != "product_sender" else "#059669"
    btn_hover_bg = "#1d4ed8" if role != "product_sender" else "#047857"

    css = f"""
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {{
        font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    }}

    /* Global App Canvas: Deep Dark Navy */
    .stApp {{
        background-color: #07111F !important;
        color: #F8FAFC !important;
    }}

    .main .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 2.5rem;
        max-width: 1320px;
    }}

    /* Typography & Text Contrast */
    .main h1, .main h2, .main h3, .main h4, .main h5, .main h6 {{
        color: #F8FAFC !important;
    }}

    .main p, .main span, .main div, .main label, .main [data-testid="stMarkdownContainer"] p {{
        color: #F8FAFC;
    }}

    .main [data-testid="stCaptionContainer"] p, .main .text-muted {{
        color: #94A3B8 !important;
    }}

    /* Input & Select Customization */
    input, textarea, select, div[data-baseweb="input"], div[data-baseweb="select"] > div {{
        background-color: #0B172A !important;
        border-color: #26364D !important;
        color: #F8FAFC !important;
        border-radius: 8px !important;
    }}

    input:focus, textarea:focus {{
        border-color: #3B82F6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.25) !important;
    }}

    /* Form Containers */
    div[data-testid="stForm"] {{
        background-color: #101D31 !important;
        border: 1px solid #1E293B !important;
        border-radius: 14px !important;
        padding: 24px !important;
    }}

    /* Streamlit Metric Overrides */
    div[data-testid="stMetricValue"] {{
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }}

    div[data-testid="stMetricLabel"] {{
        color: #94A3B8 !important;
        font-weight: 600 !important;
    }}

    /* Sidebar Styling: Darkest Navy */
    section[data-testid="stSidebar"] {{
        background-color: {sidebar_bg} !important;
        border-right: 1px solid #1E293B !important;
        padding-top: 1.5rem !important;
        width: 290px !important;
    }}
    
    section[data-testid="stSidebar"] *, 
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] span, 
    section[data-testid="stSidebar"] div {{
        color: #F8FAFC;
    }}

    /* Navigation Menu Group Headings */
    .nav-section-title {{
        font-size: 10px;
        font-weight: 800;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #64748B;
        margin: 16px 0 6px 12px;
    }}

    /* Sidebar Clickable Buttons */
    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] {{
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
        padding: 9px 14px !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        color: #94A3B8 !important;
        background-color: transparent !important;
        border: none !important;
        box-shadow: none !important;
        margin-bottom: 2px !important;
        transition: all 0.2s ease-in-out !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover {{
        background-color: #0F2340 !important;
        color: #ffffff !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"] * {{
        color: #94A3B8 !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button[kind="secondary"]:hover * {{
        color: #ffffff !important;
    }}

    /* Active Navigation Button */
    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] {{
        width: 100% !important;
        text-align: left !important;
        justify-content: flex-start !important;
        display: flex !important;
        align-items: center !important;
        padding: 9px 14px !important;
        border-radius: 8px !important;
        font-size: 13.5px !important;
        font-weight: 700 !important;
        color: #ffffff !important;
        background: {sidebar_active_bg} !important;
        border: none !important;
        margin-bottom: 2px !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
    }}

    section[data-testid="stSidebar"] div.stButton > button[kind="primary"] * {{
        color: #ffffff !important;
        font-weight: 700 !important;
    }}

    /* Main Area Primary Buttons */
    .main .stButton > button {{
        background-color: {btn_bg} !important;
        color: #ffffff !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 8px 18px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2) !important;
    }}

    .main .stButton > button * {{
        color: #ffffff !important;
    }}

    .main .stButton > button:hover {{
        background-color: {btn_hover_bg} !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4) !important;
    }}

    /* Data Table Container */
    div[data-testid="stDataFrame"] {{
        border: 1px solid #1E293B !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }}

    /* Streamlit Tabs Customization */
    button[data-baseweb="tab"] {{
        color: #94A3B8 !important;
        font-weight: 600 !important;
    }}

    button[aria-selected="true"] {{
        color: #3B82F6 !important;
        border-bottom-color: #2563EB !important;
    }}
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
        header[data-testid="stHeader"] {
            display: none !important;
        }
        .main .block-container {
            max-width: 1100px !important;
            padding-top: 2rem !important;
        }
        """

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
