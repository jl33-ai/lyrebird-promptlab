import pandas as pd
import streamlit as st

from services.llm_service import generate, supported_models

from annotated_text import annotated_text

st.set_page_config(page_title='Prompt/Eval Testing', page_icon='🤖', layout='wide')
st.title('Prompt/Eval Testing')


def parse_animated_text(text):
    parsed = []
    current_phrase = []
    in_parentheses = False

    words = text.split()

    for word in words:
        if '(' in word and not in_parentheses:
            in_parentheses = True
            current_phrase.append(word.split('(')[0])
        elif ')' in word and in_parentheses:
            in_parentheses = False
            current_phrase.append(word.split(')')[0])
            pos = word.split(')')[-1].strip('()')
            parsed.append((' '.join(current_phrase), pos))
            current_phrase = []
        elif in_parentheses:
            current_phrase.append(word)
        else:
            parsed.append(word)

    return parsed


if 'tag' not in st.session_state:
    st.session_state.tag = False

with st.sidebar:
    # upload from CSV
    uploaded_file = st.file_uploader("Upload transcripts from .csv")
    if st.button('Populate (warning, will overwrite)'):
        if uploaded_file is not None:
            st.session_state.dataframe = pd.read_csv(uploaded_file)

if 'dataframe' not in st.session_state:
    st.session_state.dataframe = pd.DataFrame()

col_left, col_right = st.columns(2)

st.markdown('---')
st.subheader('All data')
dataframe_container = st.empty()
dataframe_container.dataframe(st.session_state.dataframe, use_container_width=True)

new_transcript = st.text_area('Enter a new transcript', height=100,
                              placeholder='Type a new transcript here...')


def update_dataframe_display():
    dataframe_container.dataframe(st.session_state.dataframe, use_container_width=True)


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


def generate_text(df, selected_cols, system_prompt, user_prompt, new_col_name):
    results = df.copy()
    total = len(results)
    progress_bar = st.progress(0)

    if not user_prompt:
        prompt = ''

    # TODO preprocess and interpolate the prompts

    new_column = []
    for idx, row in results.iterrows():
        if len(selected_cols) == 1:
            transcript = str(row[selected_cols[0]])
            user_prompt = user_prompt.replace("{{column}}", transcript)
            if st.session_state.tag:
                system_prompt += """
                                 Your response should be annotated as follows. Use the following format:
                                - For single words: word(PERT_NEG)
                                - For multi-word phrases: "multiple words"(PERT_NEG)
                                 For example: "I do not have an allergy"(PERT_NEG) I also have a cold
                                 Do not preface your response
                             """
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
        elif len(selected_cols) == 2:
            transcriptA = str(row[selected_cols[0]])
            transcriptB = str(row[selected_cols[1]])
            user_prompt = user_prompt.replace("{{columnA}}", transcriptA).replace("{{columnB}}", transcriptB)

            messages = [
                {"role": "system", "content": "Perform a comparison. "},
                {"role": "user",
                 "content": (system_prompt + user_prompt)}
            ]

        generated_text = generate(messages, gen_model_type)
        if st.session_state.tag:
            print(generated_text)
            parsed_text = parse_animated_text(generated_text)
            annotated_text(*parsed_text)

        new_column.append(generated_text)
        progress_bar.progress((idx + 1) / total)

    results[new_col_name] = new_column
    progress_bar.empty()
    return results


available_columns = st.session_state.dataframe.columns.tolist()

with col_left:
    gen_system_prompt = st.text_area("System Prompt", height=150,
                                     placeholder="Enter the system prompt here...")
    gen_user_prompt = st.text_area("User Prompt", height=150,
                                   placeholder="Enter the user prompt here...", value="{{column}}")
    gen_model_type = st.radio(
        "Choose a model type:",
        list(supported_models.__args__)
    )

    selected_columns = st.multiselect("Select column for input", available_columns, max_selections=2)

    gen_new_column_name = st.text_input("Enter name for the new column",
                                        placeholder="e.g., Generated_Output_1")

    if st.button('Generate'):
        if not gen_system_prompt:
            st.error("Please enter a system prompt.")
        elif st.session_state.dataframe.empty:
            st.error("Please add at least one transcript.")
        elif not selected_columns:
            st.error("Please select at least one column for input.")
        elif not gen_new_column_name:
            st.error("Please enter a name for the new column.")
        else:
            with st.spinner('Generating outputs...'):
                st.session_state.dataframe = generate_text(
                    st.session_state.dataframe,
                    selected_columns,
                    gen_system_prompt,
                    gen_user_prompt,
                    gen_new_column_name
                )

            st.success("Generation complete!")
            update_dataframe_display()

with col_right:
    eval_system_prompt = st.text_area("System Prompt Eval", height=150,
                                      placeholder="E.g 'Find all pertinent negatives' OR 'Compare the two notes for quality'")
    eval_user_prompt = st.text_area("User Prompt Eval", height=150,
                                    placeholder="{{column}} OR {{columnA}} vs. {{columnB}}")
    eval_model_type = st.radio(
        "Choose a model type for eval:",
        list(supported_models.__args__)
    )

    eval_selected_columns = st.multiselect("Select columns for input (max 2)", available_columns, max_selections=2)

    eval_new_column_name = st.text_input("Enter name for the eval column",
                                         placeholder="e.g., Generated_Eval_1")

    st.session_state.tag = st.checkbox("Use tagged output")
    if st.button('Run Eval'):
        if not eval_system_prompt:
            st.error("Please enter a system prompt.")
        elif st.session_state.dataframe.empty:
            st.error("Please add at least one transcript.")
        elif not eval_selected_columns:
            st.error("Please select at least one column for input.")
        elif not eval_new_column_name:
            st.error("Please enter a name for the new column.")
        else:
            with st.spinner('Generating outputs...'):
                st.session_state.dataframe = generate_text(
                    st.session_state.dataframe,
                    eval_selected_columns,
                    eval_system_prompt,
                    eval_user_prompt,
                    eval_new_column_name
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
