import concurrent
import os
import sys
import re
import pandas as pd
import streamlit as st
from services.llm_service import generate, supported_models
from prompts.evaluation_prompts import get_criteria

st.set_page_config(page_title='Lyrebird Note Evaluation', page_icon='', layout='wide')

st.title('Lyrebird Note Evaluation')

if 'dataframe' not in st.session_state:
    st.session_state['dataframe'] = pd.DataFrame()

if 'results' not in st.session_state:
    st.session_state['results'] = pd.DataFrame()

if 'criteria' not in st.session_state:
    st.session_state['criteria'] = get_criteria()

if 'models' not in st.session_state:
    st.session_state['models'] = list(supported_models.__args__)

with st.sidebar:
    st.subheader("Model Selection")
    selected_model = st.selectbox("Choose a model:", st.session_state['models'])

    st.subheader("Upload Data")
    uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
    if uploaded_file is not None:
        st.session_state['dataframe'] = pd.read_csv(uploaded_file)
        st.success("Data uploaded successfully!")

    if not st.session_state['dataframe'].empty:
        st.subheader("Column Selection")
        columns = st.session_state['dataframe'].columns.tolist()
        notes_column = st.selectbox("Select the notes column", columns)
        transcript_column = st.selectbox("Select the transcript column", columns)
        st.session_state['notes_column'] = notes_column
        st.session_state['transcript_column'] = transcript_column
    else:
        st.warning("Please upload data to select columns.")


def get_user_prompt(input_required, notes, transcript):
    match input_required:
        case 'notes':
            return f'''NOTES: {notes}'''
        case 'transcript':
            return f'''TRANSCRIPT: {transcript}'''
        case 'both':
            return f'''NOTES: {notes}
TRANSCRIPT: {transcript}'''


def evaluate_notes(df, notes_col, transcript_col, criteria_list, model_type):
    results = df.copy()

    def process_criteria(criterion):
        title = criterion['title']
        response_type = criterion['type']  # 'list' or 'score'

        def process_row(row):
            notes = row[notes_col]
            transcript = row[transcript_col]

            messages = [
                {
                    "role": "system", "content": criterion['prompt']
                },
                {
                    "role": "user", "content": get_user_prompt(criterion['input_required'], notes, transcript)
                }
            ]

            print(messages)

            response = generate(messages, model_type)

            if response_type == 'list':
                num_items = len([line for line in response.strip().split('\n') if line.strip()])
                score = num_items
            elif response_type == 'score':
                try:
                    score = int(re.findall(r'\d+', response)[-1])
                except:
                    score = None
            else:
                score = None

            return score, response

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results_list = list(executor.map(process_row, [row for _, row in df.iterrows()]))

        scores = [res[0] for res in results_list]
        raw_responses = [res[1] for res in results_list]

        results[f"{title} Score"] = scores
        results[f"{title} Response"] = raw_responses

        return scores, raw_responses

    with concurrent.futures.ThreadPoolExecutor() as executor:
        criteria_results_list = list(executor.map(process_criteria, criteria_list))

    for i, criteria in enumerate(criteria_list):
        results[criteria['title'] + ' score'] = criteria_results_list[i][0]
        results[criteria['title'] + ' response'] = criteria_results_list[i][0]

    return results


def display_results(results_df, notes_col):
    st.write("Evaluation Results")

    for idx, row in results_df.iterrows():
        with st.expander(f"**Note {idx + 1}:**"):
            st.write(row[notes_col])
        for criterion in st.session_state['criteria']:
            title = criterion['title']
            score_col = f"{title} Score"
            response_col = f"{title} Response"
            score = row[score_col]
            with st.expander(f"{title} - Score: {score}"):
                st.write(row[response_col])
        st.markdown("---")


if not st.session_state['dataframe'].empty:
    st.write("Data Preview")
    st.dataframe(st.session_state['dataframe'].head())

    if st.button("Run Evaluation"):
        with st.spinner("Evaluating..."):
            results = evaluate_notes(
                st.session_state['dataframe'],
                st.session_state['notes_column'],
                st.session_state['transcript_column'],
                st.session_state['criteria'],
                selected_model
            )
            st.session_state['results'] = results
            st.success("Evaluation complete!")

    if not st.session_state['results'].empty:
        display_results(st.session_state['results'], st.session_state['notes_column'])

        csv = st.session_state['results'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="evaluation_results.csv",
            mime="text/csv",
        )
