"""
app.py  -  STEP 3: the chat interface employees use.
Run:  streamlit run app.py
"""
import streamlit as st

from rag import PolicyBot

st.set_page_config(page_title="Zenith Policy Assistant", page_icon="🏢")
st.title("🏢 Zenith Policy Assistant")
st.caption("Answers come only from Zenith Corp's official policy documents, with page references.")


@st.cache_resource(show_spinner="Loading policy index...")
def load_bot():
    return PolicyBot()          # loaded once, reused for every question


bot = load_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("Try asking")
    for q in ["How many casual leaves do I get per year?",
              "What's the process for claiming travel reimbursement?",
              "What should I do if I lose my laptop?",
              "What is the hotel limit for a G4 employee in Mumbai?"]:
        st.markdown(f"- {q}")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if question := st.chat_input("Ask about leave, expenses, travel, IT, onboarding..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the policy documents..."):
            result = bot.ask(question, st.session_state.messages[:-1])
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("📄 Sources used"):
                for s in result["sources"]:
                    sim = f" · similarity {s['similarity']:.2f}" if s["similarity"] else ""
                    st.markdown(f"**Page {s['page']}** · {s['chapter']} › {s['section']}{sim}")
                    st.caption(s["text"][:350] + "...")
    st.session_state.messages.append({"role": "assistant", "content": result["answer"]})
