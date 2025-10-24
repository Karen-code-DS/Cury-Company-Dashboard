import streamlit as st
from PIL import Image
    
    # Configuração da página
st.set_page_config(
    page_title="Dashboard - Cury Company",
    page_icon="📊",
    layout="wide"
)

image = Image.open('Cury.png')
st.sidebar.image(image, width=200)

st.sidebar.markdown("# Cury Company")
st.sidebar.markdown("## Entregas mais rápidas da cidade")
st.sidebar.markdown("""---""")
    
# Corpo principal
st.title("📊 Dashboard")
st.markdown(
    """
    O Dashboard foi construído para acompanhar as **métricas de crescimento** dos Entregadores e Restaurantes.  
    
    ### Estrutura:
    - **Visão Empresa**
        - Visão Gerencial → Métricas gerais de comprometimento.  
        - Visão Tática → Indicadores semanais de crescimento.  
        - Visão Geográfica → Insights de geolocalização.  
    - **Visão Entregador**
        - Acompanhamento dos indicadores semanais de crescimento.  
    - **Visão Restaurante**
        - Indicadores semanais do restaurante.  
        ---
     ### 🆘 Suporte
     - Time de Data Science no Discord  
         - Contato: `karenleticiaferreiradasilva@gmail.com`
        """
    )
