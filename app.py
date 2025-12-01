import streamlit as st
import requests

st.set_page_config(page_title="Olist AI Data Analyst", layout="wide")

st.title("📊 Olist AI Data Analyst")
st.write("Ask a question about the Olist dataset")

question = st.text_input("Your question")

if st.button("Run Query"):
    try:
        response = requests.get("http://localhost:8000/ask", params={"q": question})
        data = response.json()
        st.markdown(data.get("answer", "No answer returned"))
    except Exception as e:
        st.error(f"Connection error: {e}")
