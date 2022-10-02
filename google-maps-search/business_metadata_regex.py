import re

def is_website(text):

    expression = r".+[.](com|gov|net|org)"

    return True if bool(re.search(expression, text)) else False

def is_state_address(text, state="AZ"):

    try:
        text_split = text.split(",")
        at_least_two_commas = (len(text_split) >= 3)
        correct_state = (text_split[-1].strip()[:2] == state)
        return True if at_least_two_commas & correct_state else False

    except IndexError:
        return False

def is_phone_number(text):

    expression = r"[(]?\d{3}[)]?\s?\d+[-]?\d+"

    return True if bool(re.search(expression, text)) else False