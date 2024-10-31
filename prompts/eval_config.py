"""
How it works
'list' implies we count the number of items in the response
'score' implies we let the LLM just provide its own score
"""

CRITERIA = [
    {
        'title': 'num_hallucinations',
        'prompt': '''You are a professional medical note evaluator. Your task is to read a medical note and the corresponding transcript and then perform a detailed analysis on it by searching for and listing out all hallucinations. Read the transcript, and then list all hallucinations that occurred in the note. A hallucination is a made up piece of information that was never mentioned in the transcript but appeared in the note:
        TRANSCRIPT: {transcript}
        NOTES: {notes}''',
        'type': 'list'
    },
    {
        'title': 'missed_information',
        'prompt': '''You are a professional medical note evaluator. Your task is to read a medical note and the corresponding transcript, and then search for and list out all missed information. Read the transcript, and then list all discrete pieces of missed information that occurred in the note. For example, if the transcript mentioned that the patient got a vaccination last year, but the note omitted this:
        TRANSCRIPT: {transcript}
        NOTES: {notes}''',
        'type': 'list'
    },
    {
        'title': 'duplication',
        'prompt': '''You are a professional medical note evaluator. Read the following medical note and then list out all instances of repetition, duplication, or redundancy. You should list each repeated part ona new line. Repetition may occur in a medical note where the same information is listed more than once under a different heading. This is very bad and it is your task to find and list out all instances where this has happened:
             NOTES: {notes}''',
        'type': 'list'
    },
    {
        'title': 'wrong_sections',
        'prompt': '''You are a professional medical note evaluator. Read the following medical note and then list out all instances where information has been listed out under the wrong section
            NOTES: {notes}''',
        'type': 'list'
    },
    {
        'title': 'level_of_detail',
        'prompt': 'Rate the level of detail in the note compared to the transcript on a scale of 0-100.\n\nNote:\n{notes}\n\nTranscript:\n{transcript}',
        'type': 'score'
    }
]


def decorate_criteria_prompts(criteria):
    if criteria['type'] == 'list':
        return f'''{criteria['prompt']}
        You must not preamble your response whatsoever, simply output the list straight away, with each new point on it's own newline, no space separation
        '''
    elif criteria['type'] == 'score':
        return f'''You are a professional medical note evaluator. Your task is to read a medical note and then perform a detailed analysis on it, and provide one number
        {criteria['prompt']}
        You must first justify your score, explaining the reasoning behind how you arrived at the number, and then output the number. The number should only be mentioned once. 
        '''


def get_criteria():
    return [
        {'title': criteria['title'], 'prompt': decorate_criteria_prompts(criteria), 'type': criteria['type']}
        for criteria in CRITERIA]
