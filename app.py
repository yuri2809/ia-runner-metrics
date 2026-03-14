import streamlit as st
from serpapi import GoogleSearch
import pandas as pd
import requests
import altair as alt

# 1. Configuração e Estética
st.set_page_config(page_title="IA Runner Metrics", page_icon="🏃", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .main-title { color: #1e3a8a; font-size: 40px; font-weight: bold; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

st.markdown('<p class="main-title">🏃 IA Runner Metrics</p>', unsafe_allow_html=True)
st.markdown("<center>Análise de Preços e Consultoria Técnica em Tempo Real</center>", unsafe_allow_html=True)
st.markdown("---")

# 2. Entrada do Usuário
col_input1, col_input2, col_input3 = st.columns([1, 2, 1])
with col_input2:
    modelo = st.text_input("Qual tênis você quer analisar?", placeholder="Ex: Nike Pegasus 40")
    analisar = st.button("🚀 Analisar Mercado e Performance", use_container_width=True)

if analisar and modelo:
    with st.spinner('Minerando dados e gerando insights...'):
        try:
            # --- BUSCA DE PREÇOS (SERPAPI) ---
            params = {
                "engine": "google_shopping",
                "q": modelo, "hl": "pt", "gl": "br",
                "api_key": st.secrets["SERP_API_KEY"]
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            if "shopping_results" in results:
                # Tratamento de Dados
                df = pd.DataFrame(results["shopping_results"][:10])
                
                # Limpeza para valores numéricos (essencial para o gráfico)
                df['preco_num'] = df['price'].str.replace('R$', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False).str.replace(' agora', '', regex=False).astype(float)
                df_sorted = df.sort_values('preco_num')
                
                melhor_oferta = df_sorted.iloc[0]

                # --- LINHA 1: MÉTRICAS DE DESTAQUE ---
                m1, m2, m3 = st.columns(3)
                m1.metric("Menor Valor", melhor_oferta['price'])
                m2.metric("Loja", melhor_oferta['source'])
                m3.metric("Variação", f"R$ {df['preco_num'].max() - df['preco_num'].min():.2f}")

                st.markdown("---")

                # --- LINHA 2: GRÁFICO E TABELA ---
                col_chart, col_table = st.columns([1.5, 1])

                with col_chart:
                    st.subheader("📈 Comparativo Visual de Preços")
                    chart = alt.Chart(df_sorted).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
                        x=alt.X('preco_num:Q', title="Preço (R$)"),
                        y=alt.Y('source:N', title="Loja", sort='-x'),
                        color=alt.condition(
                            alt.datum.preco_num == df_sorted['preco_num'].min(),
                            alt.value('#10b981'), # Verde para o mais barato
                            alt.value('#3b82f6')  # Azul para os outros
                        ),
                        tooltip=['source', 'price', 'title']
                    ).properties(height=350)
                    st.altair_chart(chart, use_container_width=True)

                with col_table:
                    st.subheader("📋 Lista de Ofertas")
                    st.dataframe(df_sorted[['source', 'price', 'title']], use_container_width=True, hide_index=True)

                # --- LINHA 3: INTELIGÊNCIA ARTIFICIAL ---
                st.markdown("---")
                st.subheader("🤖 Consultoria Especialista (OpenAI GPT-4o)")
                
                openai_key = st.secrets["OPENAI_API_KEY"]
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "Você é um especialista em corrida de performance."},
                        {"role": "user", "content": f"Analise o tênis {modelo}. Dê 3 prós, 2 contras e diga se vale a pena pagar {melhor_oferta['price']} na {melhor_oferta['source']}. Seja conciso."}
                    ]
                }
                headers = {"Authorization": f"Bearer {openai_key}"}
                response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                
                if response.status_code == 200:
                    st.info(response.json()['choices'][0]['message']['content'])
                else:
                    st.warning("IA em manutenção. Use os dados acima para sua decisão.")

            else:
                st.error("Modelo não encontrado no Google Shopping.")
        except Exception as e:
            st.error(f"Erro inesperado: {e}")

st.markdown("<br><br><center><small>Dashboard Yuri | Especialização Comunicação & IA</small></center>", unsafe_allow_html=True)
