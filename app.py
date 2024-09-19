import streamlit as st
import pandas as pd
from llm_service import generate

st.set_page_config(page_title='LLM Output Generator', page_icon='🤖', layout='wide')
st.title('LLM Output Generator')

with st.sidebar:
    st.header("Configuration")
    model_type = st.radio(
        "Choose a model type:",
        ("gpt-4", "gpt-4-preview", "gpt-4-2024", "gpt-4-o1-preview", "gpt-4o", "anthropic")
    )

    system_prompt = st.text_area("System Prompt", height=150,
                                 placeholder="Enter the system prompt here...")

st.header("User Inputs")

if 'transcripts_df' not in st.session_state:
    st.session_state.dataframe = pd.DataFrame(columns=['transcripts'])

new_transcript = st.text_area('Enter a new transcript', height=100,
                              placeholder='Type a new transcript here...')
if st.button('Add Transcript'):
    if new_transcript:
        st.session_state.dataframe = pd.concat(
            [st.session_state.dataframe, pd.DataFrame({'transcripts': [new_transcript]})],
            ignore_index=True
        )
        st.success('Transcript added!')
    else:
        st.warning('Please enter a transcript before adding.')

st.subheader("All Transcripts")
st.dataframe(st.session_state.dataframe, use_container_width=True)


# wrapper
def generate_text():
    results = []
    total = len(st.session_state.dataframe)
    progress_bar = st.progress(0)

    for idx, row in st.session_state.dataframe.iterrows():
        transcript = row['transcripts']
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": transcript}
        ]

        generated_text = generate(messages, model_type)
        results.append({'Transcript': transcript, 'Generated Output': generated_text})
        progress_bar.progress((idx + 1) / total)

    progress_bar.empty()
    return pd.DataFrame(results)


if st.button('Generate Outputs'):
    if not system_prompt:
        st.error("Please enter a system prompt.")
    elif st.session_state.dataframe.empty:
        st.error("Please add at least one transcript.")
    else:
        with st.spinner('Generating outputs...'):
            results_df = generate_text()

        st.success("Generation complete!")
        st.subheader("Results")
        st.dataframe(results_df, use_container_width=True)

        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="llm_generation_results.csv",
            mime="text/csv",
        )

st.sidebar.markdown("---")
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Select a model type from the sidebar.
2. Enter a system prompt in the sidebar.
3. Add one or more transcripts in the main area.
4. Click 'Generate Outputs' to process all transcripts.
5. View the results in the table.
6. Download the results as a CSV file if needed.
""")
