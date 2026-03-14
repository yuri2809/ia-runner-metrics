import streamlit as st
from serpapi import GoogleSearch
import google.generativeai as genai
import os
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃")

st.title("🏃 IA Runner Metrics")
st.markdown("Análise de preços e performance para corredores.")

# Campo de busca
modelo = st.text_input("Qual modelo de tênis você deseja analisar?", placeholder="Ex: Puma Deviate Nitro 3")

if st.button("Analisar"):
    if modelo:
        with st.spinner('Consultando mercado e IA...'):
            try:
                # 1. Busca via SerpApi (usando segredos do Streamlit)
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
                    
                    # Limpeza de preços para métricas
                    df['Preco_Num'] = df['price'].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.replace(' agora', '', regex=False).astype(float)
                    melhor_oferta = df.loc[df['Preco_Num'].idxmin()]
                    
                    # Exibição
                    st.success(f"Melhor preço: {melhor_oferta['price']} na {melhor_oferta['source']}")
                    st.write("### Ofertas encontradas:")
                    st.dataframe(df[['source', 'title', 'price']])
                    
                    # 2. Análise com Gemini (Versão Estabilizada)
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    # Usando o nome mais simples e universal do modelo
                    model_ai = genai.GenerativeModel('gemini-1.5-flash')
                    
                    prompt = f"Você é um especialista em corrida. Analise o tênis {modelo}. Dê 3 prós, 2 contras e diga se vale a pena por {melhor_oferta['price']} na {melhor_oferta['source']}."
                    
                    response = model_ai.generate_content(prompt)
                    
                    st.markdown("### 🤖 Avaliação da IA")
                    st.write(response.text)
                else:
                    st.error("Nenhum resultado encontrado.")
            except Exception as e:
                st.error(f"Erro: {e}")
    else:
        st.warning("Por favor, digite um modelo.")
