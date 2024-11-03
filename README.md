# Promptlab

---

Promptlab allows us to experiment with prompts for any use case. It is flexible, allowing us to run batch operations on
tables of data using our language models

# Setup

---

1. `git clone https://github.com/Cipher-AI-health/PromptLab`
2. (Optional) set up
   a [virtual environment](https://www.freecodecamp.org/news/how-to-setup-virtual-environments-in-python/)
2. `pip3 install -r requirements.txt`
3. Copy variables from 'PromptLab' in Bitwarden into `.env` file
3. `streamlit run app.py`

# Features

---

- **Upload Data**: Import transcripts or data from a CSV file.
- **Extract Transcripts**: Extract specific text from a column based on start and end tags.
- **Add Transcripts Manually**: Input new transcripts directly into the app.
- **Generate Outputs**: Use custom prompts to generate outputs using selected models.
- **Evaluate Outputs**: Run evaluations on generated outputs with evaluation prompts.
- **Download Results**: Export the final data as a CSV file.

# How to use

---

### 1. Upload Data

- Go to the sidebar and find **Upload from csv**.
- Click **Browse files** to select your CSV file.
- Click **Populate (warning, will overwrite)** to load the data into the app.

### 2. Extract Transcripts

- In the sidebar, select the column under **Column to extract tag from**.
- Enter the **Tag start** and **Tag end** that enclose your transcript text (defaults are `<start_of_transcript>`
  and `<end_of_transcript>`).
- Provide a name for the new column in **Name of new columns** (e.g., `extracted_transcript`).
- Click **Extract transcript columns** to create the new column.

### 3. Add Transcripts Manually

- In the main area, find **Enter a new transcript**.
- Type your transcript into the text area.
- Click **Add Transcript** to add it to the data.

### 4. Generate Outputs

- Under **System Prompt**, enter your system prompt.
- Under **User Prompt**, enter your user prompt. Use `{{column_name}}` to reference columns (e.g., `{{transcripts}}`).
- Select a model type from **Choose a model type**.
- Enter a name for the output column in **Enter name for the new column**.
- Click **Generate** to produce outputs.

### 5. Evaluate Outputs

- Under **System Prompt Eval**, enter your evaluation system prompt.
- Under **User Prompt Eval**, enter your evaluation user prompt, referencing columns as needed.
- Select a model type from **Choose a model type for eval**.
- Enter a name for the evaluation column in **Enter name for the eval column**.
- (Optional) Check **Use tagged output** if applicable.
- Click **Run Eval** to perform the evaluation.

### 6. Download Results

- Click **Download Results as CSV** at the bottom of the app to save your data.

## Tips

- Use the **Available columns** in the sidebar to see which columns you can reference.
- Always enclose column names in `{{` and `}}` when using them in prompts.
- Ensure new column names are unique to avoid overwriting data.

## Example Workflow

1. **Upload** a CSV file containing a `raw_text` column with transcripts (can be any name)
2. **Extract** transcripts by selecting `raw_text` and specifying tags.
3. **Generate Outputs** by entering prompts and referencing `{{extracted_transcript}}`.
4. **Evaluate** the outputs by creating evaluation prompts and referencing the generated output column.
5. **Download** the final CSV with all your data.
6. **Evaluation** then you could import this csv into our 'Evaluation' page which allows you to pass outputs into our
   Lyrebird
   Evaluation System and get comprehensive evals

# Screenshots

---

![image](https://github.com/user-attachments/assets/544b89b7-06ba-4033-8604-8cefad8904f2)

![image](https://github.com/user-attachments/assets/7ac9b587-3afd-4449-bd3d-514dd0b31020)
