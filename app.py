import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests

# 1. Configuração da Página
st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃")
st.title("🏃 IA Runner Metrics (Powered by GPT-4o)")

# 2. Entrada do Usuário
modelo = st.text_input("Qual tênis quer analisar?", placeholder="Ex: Puma Deviate Nitro 3")

if st.button("Analisar Tênis"):
    if modelo:
        with st.spinner('Buscando preços e consultando a inteligência do ChatGPT...'):
            try:
                # --- ETAPA 1: BUSCA DE PREÇOS (SERPAPI) ---
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
                    
                    # --- ETAPA 2: ANÁLISE COM OPENAI (GPT-4o-mini) ---
                    openai_key = st.secrets["OPENAI_API_KEY"]
                    url = "https://api.openai.com/v1/chat/completions"
                    
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {openai_key}"
                    }
                    
                    data = {
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": "Você é um especialista em corrida de rua e materiais esportivos."},
                            {"role": "user", "content": f"Analise o tênis {modelo}. Liste 3 pontos fortes, 2 pontos fracos e diga se o preço de {melhor_oferta['price']} na loja {melhor_oferta['source']} vale a pena. Seja direto."}
                        ],
                        "temperature": 0.7
                    }
                    
                    response = requests.post(url, headers=headers, json=data)
                    
                    if response.status_code == 200:
                        texto_ia = response.json()['choices'][0]['message']['content']
                        st.markdown("---")
                        st.markdown("### 🤖 Análise Real via GPT-4o")
                        st.write(texto_ia)
                    else:
                        st.error(f"Erro na OpenAI ({response.status_code}): {response.text}")
                else:
                    st.error("Nenhum preço encontrado.")
            except Exception as e:
                st.error(f"Erro no sistema: {e}")
