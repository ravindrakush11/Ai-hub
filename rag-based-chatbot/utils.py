import re

# def clean_text(text: str):
#     cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
#     return cleaned_text.strip()



import re

def clean_text(text):
    if not isinstance(text, str):
        return str(text)  # Fallback for safety
    cleaned_text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned_text.strip()
