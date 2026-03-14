import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests
import json

st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃")
st.title("🏃 IA Runner Metrics")

modelo = st.text_input("Qual tênis de corrida quer analisar?", placeholder="Ex: Puma Deviate Nitro 3")

if st.button("Analisar"):
    if modelo:
        with st.spinner('Buscando preços e consultando a IA...'):
            try:
                # 1. BUSCA DE PREÇOS (SERPAPI)
                params = {
                    "engine": "google_shopping",
                    "q": modelo,
                    "hl": "pt",
                    "gl": "br",
                    "api_key": st.secrets["SERP_API_KEY"]
                }
                search = GoogleSearch(params)
                results = search.get_dict()
                
                if "shopping_results" in results:
                    df = pd.DataFrame(results["shopping_results"][:10])
                    melhor_oferta = df.iloc[0]
                    st.success(f"Melhor preço: {melhor_oferta['price']} na {melhor_oferta['source']}")
                    st.dataframe(df[['source', 'title', 'price']])
                    
                    # 2. ANÁLISE COM GEMINI (VIA CHAMADA DIRETA)
                    # Tentamos falar com a IA sem usar a biblioteca 'generativeai'
                    api_key = st.secrets["GEMINI_API_KEY"]
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    
                    payload = {
                        "contents": [{
                            "parts": [{
                                "text": f"Você é um especialista em tênis de corrida. Analise o modelo {modelo}. Dê 3 prós, 2 contras e diga se vale a pena por {melhor_oferta['price']} na loja {melhor_oferta['source']}. Seja direto."
                            }]
                        }]
                    }
                    
                    response = requests.post(url, json=payload)
                    res_json = response.json()
                    
                    if response.status_code == 200:
                        texto_ia = res_json['candidates'][0]['content']['parts'][0]['text']
                        st.markdown("### 🤖 Análise da IA")
                        st.write(texto_ia)
                    else:
                        st.warning(f"A IA retornou um erro ({response.status_code}). Mas os preços estão acima!")
                else:
                    st.error("Nenhum preço encontrado.")
            except Exception as e:
                st.error(f"Erro no sistema: {e}")
