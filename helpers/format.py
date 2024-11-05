import re


def extract_tags(text, tag_start, tag_end):
    pattern = rf'{tag_start}(.*?){tag_end}'
    match = re.search(pattern, text, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return None
