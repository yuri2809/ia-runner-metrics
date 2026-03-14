import streamlit as st
from serpapi import GoogleSearch
import google.generativeai as genai
import pandas as pd

# 1. Configurações Iniciais de Interface
st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃", layout="centered")

st.title("🏃 IA Runner Metrics")
st.markdown("""
Esta aplicação utiliza **Inteligência Artificial** e dados do **Google Shopping** para encontrar o melhor preço e analisar a performance de tênis de corrida.
""")

# 2. Entrada do Usuário
modelo = st.text_input("Qual modelo de tênis você deseja analisar?", placeholder="Ex: Puma Deviate Nitro 3")

if st.button("Analisar Tênis"):
    if modelo:
        with st.spinner('Buscando ofertas e gerando análise técnica...'):
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
                    # Transformamos em tabela
                    df = pd.DataFrame(results["shopping_results"][:10])
                    
                    # Exibimos a melhor oferta em destaque
                    melhor_oferta = df.iloc[0]
                    st.success(f"🔥 Melhor oferta: {melhor_oferta['price']} na {melhor_oferta['source']}")
                    
                    # Tabela completa de preços
                    st.write("### Comparativo de Preços")
                    st.dataframe(df[['source', 'title', 'price']], use_container_width=True)
                    
                    # --- ETAPA 2: ANÁLISE COM IA (GEMINI) ---
                    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
                    
                    # Configuração de segurança para evitar que a IA bloqueie nomes de marcas
                    safety_settings = [
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                    ]
                    
                    modelos_testar = ["gemini-1.5-flash", "gemini-pro"]
                    analise_texto = None
                    
                    for m_name in modelos_testar:
                        try:
                            # Adicionamos o safety_settings aqui na criação do modelo
                            model_ai = genai.GenerativeModel(m_name, safety_settings=safety_settings)
                            
                            prompt = f"""
                            Você é um especialista em tênis de corrida. 
                            Analise o modelo: {modelo}.
                            1. Liste 3 pontos fortes.
                            2. Liste 2 pontos fracos.
                            3. Conclua se o preço de {melhor_oferta['price']} vale a pena.
                            Responda de forma direta com bullet points.
                            """
                            response = model_ai.generate_content(prompt)
                            analise_texto = response.text
                            if analise_texto:
                                break
                        except:
                            continue
                    
                    if analise_texto:
                        st.markdown("---")
                        st.markdown("### 🤖 Avaliação Técnica da IA")
                        st.markdown(analise_texto)
                    else:
                        st.warning("⚠️ A análise da IA falhou, mas os preços acima são reais.")
                
                else:
                    st.error("Nenhum resultado de preço encontrado para este modelo.")
            
            except Exception as e:
                st.error(f"Erro inesperado no sistema: {e}")
    else:
        st.warning("Por favor, digite o nome de um tênis para começar.")

# Rodapé informativo
st.markdown("---")
st.caption("Projeto desenvolvido para a Especialização em Comunicação e IA.")
