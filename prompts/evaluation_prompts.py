"""
How it works
'list' implies we count the number of items in the response
'score' implies we let the LLM just provide its own score
"""

CRITERIA = [
    {
        'title': 'num_hallucinations',
        'prompt': '''You are an expert medical documentation specialist obsessed with details
- You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
- You will also be given the prompt for how the notes should have been written and are evaluating any instructions that were not followed in generating the supplied notes.
- You will be given the transcript for the consult, generated notes, and the prompt used to generate the notes.
- If something is not in the notes but also not clear in the transcript and theoretically couldnt have been included in the notes, dont mention this
- Provide your answers in dot point form, quoting the input sources where possible.

you must evaluate the hallucination levels of the consult note. Give a count of the instances of each issue that occur with referenced proof below quoting where it occured:
Hallucinations: you must list anything that was said in the notes that is not entirely objectively clear in the transcript, this can also include where the notes have even slightly altered or applied interpretation to the transcript''',
        'type': 'list',
        'input_required': 'both'  # 'notes', 'transcript', or 'both'
    },
    {
        'title': 'missed_information',
        'prompt': '''You are an expert medical documentation specialist obsessed with details
- You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
- You will also be given the prompt for how the notes should have been written and are evaluating any instructions that were not followed in generating the supplied notes.
- You will be given the transcript for the consult, generated notes, and the prompt used to generate the notes.
- If something is not in the notes but also not clear in the transcript and theoretically couldnt have been included in the notes, dont mention this
- Provide your answers in dot point form, quoting the input sources where possible.

you must evaluate the amount of missed information in the consult note. Give a count of the instances of each issue that occur with referenced proof below quoting where it occured:
List any and all clinically relevant information or detail in the transcript that was missed in the notes. This can even be specific details that were left out of sections that the clinician would have wanted to known
- find all examination findings/measurements present in the transcript but not included in the notes
You must also find all pertinent negatives missed in the notes. A pertinent negative is every time the patient answers in the negative to a specific feeling, symptom or any question by the doctor. You must find any/all that are missed in the notes but occured in the transcript''',
        'type': 'list',
        'input_required': 'both'
    },
    {
        'title': 'duplication',
        'prompt': '''You are an expert medical documentation specialist obsessed with details
- You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
- You will also be given the prompt for how the notes should have been written and are evaluating any instructions that were not followed in generating the supplied notes.
- You will be given the transcript for the consult, generated notes, and the prompt used to generate the notes.
- If something is not in the notes but also not clear in the transcript and theoretically couldnt have been included in the notes, dont mention this
- Provide your answers in dot point form, quoting the input sources where possible.
Find the number of cases where the same information is repeated multiple times in the notes. All similar information should only appear once under a specific heading and should never be repeated. You must find the count of the number of instances where the same information is repeated multiple times in the notes.''',
        'type': 'list',
        'input_required': 'notes'
    },
    {
        'title': 'wrong_sections',
        'prompt': '''You are an expert medical documentation specialist obsessed with details
- You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
- You will also be given the prompt for how the notes should have been written and are evaluating any instructions that were not followed in generating the supplied notes.
- You will be given the transcript for the consult, generated notes, and the prompt used to generate the notes.
- If something is not in the notes but also not clear in the transcript and theoretically couldnt have been included in the notes, dont mention this
- Provide your answers in dot point form, quoting the input sources where possible.
Read the following medical note and then list out all instances where you believe information has been listed out under the wrong section''',
        'type': 'list',
        'input_required': 'notes'

    },
    {
        'title': 'level_of_detail',
        'prompt': 'Rate the level of detail in the note on a scale of 0-100, where 100 is no mistakes, and then subtract one for every sentence with a mistake',
        'type': 'score',
        'input_required': 'notes'
    }
]


def decorate_criteria_prompts(criteria):
    if criteria['type'] == 'list':
        return f'''{criteria['prompt']}
        You must not preamble your response whatsoever, simply output the list straight away, with each new point on it's own newline, no space separation
        '''
    elif criteria['type'] == 'score':
        return f'''{criteria['prompt']}
        Ratings must be done on a scale of [0-100]
        You must first justify your score, explaining the reasoning behind how you arrived at the number, and then output the number. The number should only be mentioned once. 
        '''


def get_criteria():
    return [
        {'title': criteria['title'], 'prompt': decorate_criteria_prompts(criteria), 'type': criteria['type']}
        for criteria in CRITERIA]
