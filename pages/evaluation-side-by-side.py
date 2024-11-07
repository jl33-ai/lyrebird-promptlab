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

if 'criteria' not in st.session_state:
    st.session_state['criteria'] = get_criteria()

if 'models' not in st.session_state:
    st.session_state['models'] = list(supported_models.__args__)

with st.sidebar:
    st.subheader("Model Selection")
    selected_model = st.selectbox("Choose a model:", st.session_state['models'])
    st.subheader("Settings")
    num_iters = st.number_input("Number of iterations", min_value=1, value=1)

st.session_state['transcript'] = st.text_area("Enter your transcript")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Version A")
    notes_a = st.text_area("Enter notes for Version A")

with col2:
    st.subheader("Version B")
    notes_b = st.text_area("Enter notes for Version B")


def get_user_prompt(input_required, notes, transcript):
    match input_required:
        case 'notes':
            return f'''NOTES: {notes}'''
        case 'transcript':
            return f'''TRANSCRIPT: {transcript}'''
        case 'both':
            return f'''NOTES: {notes}
TRANSCRIPT: {transcript}'''


def evaluate_notes_versions(notes_dict, transcript, criteria_list, model_type, num_iters):
    results = {}
    for version_label, notes in notes_dict.items():
        print(transcript, notes)
        version_results = {}
        for criterion in criteria_list:
            title = criterion['title']
            response_type = criterion['type']  # 'list' or 'score'

            total_score = 0
            total_responses = []
            for _ in range(num_iters):
                messages = [
                    {
                        "role": "system", "content": criterion['prompt']
                    },
                    {
                        "role": "user", "content": get_user_prompt(criterion['input_required'], notes, transcript)
                    }
                ]
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

                if score is not None:
                    total_score += score
                total_responses.append(response)

            average_score = total_score / num_iters if total_score is not None else None
            version_results[title] = {'score': average_score, 'responses': total_responses}
        results[version_label] = version_results
    return results


def display_results_versions(version_label, version_results):
    for criterion_title, criterion_result in version_results.items():
        average_score = criterion_result['score']
        responses = criterion_result['responses']
        st.write(f"**{criterion_title}** - Average Score: {average_score}")
        with st.expander(f"Responses for {criterion_title}"):
            for i, response in enumerate(responses):
                st.markdown(f"Iteration {i + 1}:")
                st.markdown(response)
        st.markdown("---")


if st.session_state['transcript'] and notes_a and notes_b:
    if st.button("Run Evaluation"):
        with st.spinner("Evaluating..."):
            notes_dict = {'A': notes_a, 'B': notes_b}
            results = evaluate_notes_versions(
                notes_dict,
                st.session_state['transcript'],
                st.session_state['criteria'],
                selected_model,
                num_iters
            )
            st.session_state['results'] = results
            st.success("Evaluation complete!")

    if 'results' in st.session_state:
        result_items = list(st.session_state['results'].items())

        with col1:
            display_results_versions(result_items[0][0], result_items[0][1])
        with col2:
            display_results_versions(result_items[1][0], result_items[1][1])

        # Prepare data for CSV export
        data = {'Criteria': []}
        versions = st.session_state['results'].keys()
        for version_label in versions:
            data[version_label] = []
        for criterion in st.session_state['criteria']:
            title = criterion['title']
            data['Criteria'].append(title)
            for version_label in versions:
                score = st.session_state['results'][version_label][title]['score']
                data[version_label].append(score)
        results_df = pd.DataFrame(data)
        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name="evaluation_results.csv",
            mime="text/csv",
        )
else:
    st.warning("Please enter the transcript and notes for both versions to proceed.")
