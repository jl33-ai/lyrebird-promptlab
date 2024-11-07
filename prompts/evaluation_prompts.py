"""
How it works
'list' implies we count the number of items in the response
'score' implies we let the LLM just provide its own score
"""

# 'notes', 'transcript', or 'both'
CRITERIA = [
    {
        'title': 'num_hallucinations',
        'prompt': '''You are an expert medical documentation specialist obsessed with details. Your task is to compare the medical note with the transcript and identify all hallucinations.
    - You must output each line from the note that you are confident contains a hallucination, exactly as it is
    - You must minimize false positives by triple checking the transcript
    - Your output should be every line of the note that contains a hallucination, verbatim, with nothing else
    Hallucinations: you must list anything that was said in the notes that is not entirely objectively clear in the transcript''',
        'type': 'list',
        'input_required': 'both'
    },
    {
        'title': 'missed_information',
        'prompt': '''You are an expert medical documentation specialist obsessed with details
    - You will be given the transcript for the consult, and the generated notes
    - If something is not in the notes but also not clear in the transcript and theoretically couldnt have been included in the notes, dont mention this
    - Provide your answers in dot point form, quoting the input sources where possible.
    you must evaluate the amount of missed information in the consult note.
    List any and all clinically relevant information or detail in the transcript that was missed in the notes. This can even be specific details that were left out of sections that the clinician would have wanted to known
    - find all examination findings/measurements present in the transcript but not included in the notes
    You must also find all pertinent negatives missed in the notes. A pertinent negative is every time the patient answers in the negative to a specific feeling, symptom or any question by the doctor. You must find any/all that are missed in the notes but occured in the transcript and output them verbatim on a new line''',
        'type': 'list',
        'input_required': 'both'
    },
    {
        'title': 'duplication',
        'prompt': '''You are an expert medical documentat Fix ion specialist obsessed with details
- You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
Find the number of cases where the same information is repeated multiple times in the notes. All similar information should only appear once under a specific heading and should never be repeated. You must find the count of the number of instances where the same information is repeated multiple times in the notes.
- Your output should be every line of the note that is a duplication, verbatim, with nothing else''',
        'type': 'list',
        'input_required': 'notes'
    },
    #     {
    #         'title': 'wrong_sections',
    #         'prompt': '''You are an expert medical documentation specialist obsessed with details
    # - You are comprehensively evaluating a clinical note generated from a consult transcript based on the quality of the output.
    # - Provide your answers in dot point form, quoting the input sources where possible.
    # Read the following medical note and then list out all instances where you believe information has been listed out under the wrong section''',
    #         'type': 'list',
    #         'input_required': 'notes'
    #
    #     },
    # {
    #     'title': 'level_of_detail',
    #     'prompt': 'Rate the level of detail in the note on a scale of 0-100, where 100 is no mistakes, and then subtract one for every sentence with a mistake',
    #     'type': 'score',
    #     'input_required': 'notes'
    # }
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
        {
            'title': criteria['title'],
            'prompt': decorate_criteria_prompts(criteria),
            'type': criteria['type'],
            'input_required': criteria['input_required']
        }
        for criteria in CRITERIA
    ]
