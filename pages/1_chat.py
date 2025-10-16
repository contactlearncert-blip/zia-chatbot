# pages/1_chat.py
import streamlit as st
from utils.chat_engine import get_response

st.set_page_config(page_title="🗨️ Discuter avec Zia", page_icon="🗨️")
st.title("🗨️ Discuter avec Zia")


# Fil de conversation avec historique
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Pose ta question…")

if user_input:
    # Ajouter message utilisateur
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Obtenir réponse
    with st.chat_message("assistant"):
        with st.spinner("Zia réfléchit…"):
            response = get_response(user_input)
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})