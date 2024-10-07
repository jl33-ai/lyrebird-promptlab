import streamlit as st

from services.llm_service import supported_models, generate

st.set_page_config(page_title='Basic Generation', page_icon='🤖', layout='wide')
st.title('Basic Generation')

model_type = st.radio(
    "Choose a model type:",
    list(supported_models.__args__)
)

system_msg = st.text_area("System Message")
user_msg = st.text_area("User Message")

if st.button("Generate"):
    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]
    st.markdown(generate(
        messages,
        model_type
    ))
