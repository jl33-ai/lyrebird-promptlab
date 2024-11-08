import os
import sys
import re
import concurrent

import pandas as pd
import streamlit as st

from helpers.format import extract_tags

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.llm_service import generate, supported_models

st.set_page_config(page_title='Prompt/Eval Testing', page_icon='🤖', layout='wide')

st.title('Prompt Testing')

SYSTEM_PROMPT_TEXT_BOX_HEIGHT = 300

if 'tag' not in st.session_state:
    st.session_state.tag = False

if 'available_columns' not in st.session_state:
    st.session_state.available_columns = []

if 'dataframe' not in st.session_state:
    st.session_state.dataframe = pd.DataFrame()

with st.sidebar:
    # upload from CSV
    st.subheader("Upload from csv")
    uploaded_file = st.file_uploader("Upload transcripts from .csv")
    if st.button('Populate (warning, will overwrite)'):
        if uploaded_file is not None:
            st.session_state.dataframe = pd.read_csv(uploaded_file)

    st.markdown('---')
    column_to_extract_transcript = st.selectbox(label="Column to extract tag from",
                                                options=st.session_state.dataframe.columns.tolist())
    tag_start = st.text_input(label="Tag start", value="<start_of_transcript>")
    tag_end = st.text_input(label="Tag end", value="<end_of_transcript>")
    column_name_for_extracted_transcript = st.text_input(label="Name of new columns", value="extracted_transcript")

    if st.button('Extract transcript columns'):
        if st.session_state.dataframe is not None:
            if column_name_for_extracted_transcript in st.session_state.dataframe.columns.tolist():
                st.session_state.dataframe[column_name_for_extracted_transcript] = st.session_state.dataframe[
                    column_to_extract_transcript].apply(
                    lambda x: extract_tags(x, tag_start, tag_end))

col_left, col_right = st.columns(2)

st.markdown('---')
st.subheader('All data')
dataframe_container = st.empty()
dataframe_container.dataframe(st.session_state.dataframe, use_container_width=True)

new_transcript = st.text_area('Enter a new transcript', height=100,
                              placeholder='Type a new transcript here...')


def update_dataframe_display():
    dataframe_container.dataframe(st.session_state.dataframe, use_container_width=True)
    with st.sidebar:
        st.subheader("Available columns")
        for column in st.session_state.dataframe.columns.tolist():
            column_string = "{{" + column + "}}"
            st.code(column_string)


if st.button('Add Transcript'):
    if new_transcript:
        st.session_state.dataframe = pd.concat(
            [st.session_state.dataframe, pd.DataFrame({'transcripts': [new_transcript]})],
            ignore_index=True
        )
        update_dataframe_display()
        st.success('Transcript added!')
    else:
        st.warning('Please enter a transcript before adding.')

available_columns = st.session_state.dataframe.columns.tolist()


def update_available_columns():
    st.session_state.available_columns = st.session_state.dataframe.columns.tolist()


def parse_selected_cols(user_prompt):
    return re.findall("{{([a-zA-Z_\s]*)}}", user_prompt)


def generate_text(df, system_prompt, user_prompt, new_col_name, model_type):
    results = df.copy()
    total = len(results)
    progress_bar = st.progress(0)

    if not user_prompt:
        prompt = ''

    selected_cols = parse_selected_cols(user_prompt)

    for selected_col in selected_cols:
        if selected_col not in available_columns:
            st.warning(f'Warning: {selected_col} is not a valid column.')

    def process_row(row):
        interpolated_user_prompt = user_prompt
        for column in selected_cols:
            if column in available_columns:
                interpolated_user_prompt = interpolated_user_prompt.replace("{{" + column + "}}",
                                                                            str(row[column]))

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": interpolated_user_prompt}
        ]

        return generate(messages, model_type)

    with concurrent.futures.ThreadPoolExecutor() as executor:
        results_list = list(executor.map(process_row, [row for _, row in results.iterrows()]))

    progress_bar.progress(1)
    results[new_col_name] = results_list
    progress_bar.empty()
    update_available_columns()

    return results


with col_left:
    gen_system_prompt = st.text_area("System Prompt", height=SYSTEM_PROMPT_TEXT_BOX_HEIGHT,
                                     placeholder="Enter the system prompt here...")
    gen_user_prompt = st.text_area("User Prompt", height=150,
                                   placeholder="Enter the user prompt here...", value="{{transcripts}}")
    gen_model_type = st.radio(
        "Choose a model type:",
        list(supported_models.__args__)
    )

    gen_new_column_name = st.text_input("Enter name for the new column",
                                        placeholder="e.g., Generated_Output_1")

    if st.button('Generate'):
        if not gen_system_prompt:
            st.error("Please enter a system prompt.")
        elif st.session_state.dataframe.empty:
            st.error("Please add at least one transcript.")
        elif not gen_new_column_name:
            st.error("Please enter a name for the new column.")
        else:
            with st.spinner('Generating outputs...'):
                st.session_state.dataframe = generate_text(
                    st.session_state.dataframe,
                    gen_system_prompt,
                    gen_user_prompt,
                    gen_new_column_name,
                    gen_model_type
                )

            st.success("Generation complete!")
            update_dataframe_display()

with col_right:
    eval_system_prompt = st.text_area("System Prompt Eval", height=SYSTEM_PROMPT_TEXT_BOX_HEIGHT,
                                      placeholder="E.g 'Find all pertinent negatives' OR 'Compare the two notes for quality'")
    eval_user_prompt = st.text_area("User Prompt Eval", height=150,
                                    placeholder="{{column_name}}")
    eval_model_type = st.radio(
        "Choose a model type for eval:",
        list(supported_models.__args__)
    )

    eval_new_column_name = st.text_input("Enter name for the eval column",
                                         placeholder="e.g., Generated_Eval_1")

    st.session_state.tag = st.checkbox("Use tagged output")
    if st.button('Run Eval'):
        if not eval_system_prompt:
            st.error("Please enter a system prompt.")
        elif st.session_state.dataframe.empty:
            st.error("Please add at least one transcript.")
        elif not eval_new_column_name:
            st.error("Please enter a name for the new column.")
        else:
            with st.spinner('Generating outputs...'):
                st.session_state.dataframe = generate_text(
                    st.session_state.dataframe,
                    eval_system_prompt,
                    eval_user_prompt,
                    eval_new_column_name,
                    eval_model_type
                )

            st.success("Evaluation complete!")
            update_dataframe_display()

csv = st.session_state.dataframe.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download Results as CSV",
    data=csv,
    file_name="llm_generation_results.csv",
    mime="text/csv",
)
