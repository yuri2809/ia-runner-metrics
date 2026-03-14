import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests
import json

# 1. Configuração da Página
st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃", layout="centered")

st.title("🏃 IA Runner Metrics")
st.markdown("""
Esta aplicação utiliza **Inteligência Artificial** e dados em tempo real para ajudar corredores a encontrar o melhor preço e entender a performance de seus equipamentos.
""")

# 2. Entrada do Usuário
modelo = st.text_input("Qual tênis de corrida você quer analisar?", placeholder="Ex: Puma Deviate Nitro 3")

if st.button("Analisar Tênis"):
    if modelo:
        with st.spinner('Buscando ofertas e consultando a IA...'):
            try:
                # --- ETAPA 1: BUSCA DE PREÇOS (SERPAPI) ---
                search_params = {
                    "engine": "google_shopping",
                    "q": modelo,
                    "hl": "pt",
                    "gl": "br",
                    "api_key": st.secrets["SERP_API_KEY"]
                }
                search = GoogleSearch(search_params)
                results = search.get_dict()
                
                if "shopping_results" in results:
                    df = pd.DataFrame(results["shopping_results"][:10])
                    
                    # Identificando a melhor oferta
                    melhor_oferta = df.iloc[0]
                    st.success(f"🔥 Melhor preço encontrado: {melhor_oferta['price']} na {melhor_oferta['source']}")
                    
                    # Exibindo a tabela de preços
                    st.write("### Comparativo de Preços")
                    st.dataframe(df[['source', 'title', 'price']], use_container_width=True)
                    
                    # --- ETAPA 2: ANÁLISE COM IA (GEMINI VIA API DIRETA V1) ---
                    api_key = st.secrets["GEMINI_API_KEY"]
                    
                    # URL da API Estável do Google
                    url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    # Montagem do Prompt técnico
                    prompt_text = (
                        f"Você é um especialista técnico em tênis de corrida. "
                        f"Analise o modelo {modelo}. "
                        f"Forneça 3 pontos fortes, 2 pontos fracos e uma conclusão curta se o preço de "
                        f"{melhor_oferta['price']} na loja {melhor_oferta['source']} é competitivo. "
                        f"Responda em Português, de forma direta e usando bullet points."
                    )
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": prompt_text
                            }]
                        }]
                    }
                    
                    headers = {'Content-Type': 'application/json'}
                    
                    # Chamada para o Google
                    response = requests.post(url, json=payload, headers=headers)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        try:
                            # Extração do texto da resposta JSON do Google
                            texto_ia = res
