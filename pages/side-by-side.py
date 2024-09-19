import streamlit as st
from llm_service import generate
import pandas as pd

st.set_page_config(layout="wide")

st.title("Model Side-by-Side Comparison")

with st.sidebar:
    st.header("Input Parameters")
    prompt = st.text_area(label="System Prompt")
    transcript = st.text_area(label="User Input")
    num_iterations = st.number_input(label="Number of iterations", min_value=1, max_value=5, value=1)

    available_models = ["gpt-4", "gpt-4-preview", "gpt-4-2024", "gpt-4-o1-preview", "gpt-4o", "anthropic"]
    selected_models = st.multiselect("Select models to compare", available_models, default=["gpt-4", "gpt-4-preview"])

    generate_button = st.button('Generate Responses')

if generate_button:
    if not prompt or not transcript or not selected_models:
        st.error("Please fill in all fields and select at least one model.")
    else:
        progress_bar = st.progress(0)

        results = {model: [] for model in selected_models}

        total_iterations = len(selected_models) * num_iterations
        current_iteration = 0

        for model in selected_models:
            for i in range(num_iterations):
                messages = [
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": transcript}
                ]
                response = generate(messages, model_type=model)
                results[model].append(response)

                current_iteration += 1
                progress_bar.progress(current_iteration / total_iterations)

        st.header("Comparison Results")

        tab1, tab2 = st.tabs(["Side-by-Side View", "Tabular View"])

        with tab1:
            cols = st.columns(len(selected_models))
            for idx, model in enumerate(selected_models):
                with cols[idx]:
                    st.subheader(model)
                    for i, response in enumerate(results[model]):
                        st.write(f"Iteration {i + 1}")
                        st.text_area(f"{model} - Iteration {i + 1}", value=response, height=200, key=f"{model}_{i}")

        with tab2:
            df_data = []
            for i in range(num_iterations):
                row = {"Iteration": i + 1}
                for model in selected_models:
                    row[model] = results[model][i]
                df_data.append(row)

            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)

        csv = df.to_csv(index=False)
        st.download_button(
            label="Download results as CSV",
            data=csv,
            file_name="model_comparison_results.csv",
            mime="text/csv",
        )

st.sidebar.markdown("---")
st.sidebar.header("Instructions")
st.sidebar.markdown("""
1. Enter a system prompt and user input in the sidebar.
2. Select the number of iterations (1-5).
3. Choose the models you want to compare.
4. Click 'Generate Responses' to see the results.
5. View the results in either Side-by-Side or Tabular format.
6. Download the results as a CSV file if needed.
""")
