import re

def message_to_text(message):
    """
    Processes text messages (SMS / WhatsApp / chat)
    """
    if not message or not isinstance(message, str):
        return "Invalid message"

    message = message.lower()
    message = re.sub(r"http\S+", "", message)     # remove URLs
    message = re.sub(r"\d+", "", message)         # remove numbers
    message = re.sub(r"[^\w\s]", "", message)     # remove punctuation

    return message.strip()
