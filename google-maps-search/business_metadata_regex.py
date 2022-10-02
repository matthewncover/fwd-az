import re

def is_website(text):

    expression = r".+[.](com|gov|net|org)"

    return True if bool(re.search(expression, text)) else False

def is_address(text):

    try:
        text_split = text.split(",")
        at_least_two_commas = (len(text_split) >= 3)
        state_zip_exists = bool(re.search(r"\w{2}\s\d{5}", text_split[-1]))
        return True if at_least_two_commas & state_zip_exists else False

    except IndexError:
        return False

def get_state_from_address(text):

    return re.search(r"\w{2}\s\d{5}", text.split(',')[-1]).group().strip()[:2]

def is_state_address(text, state="AZ"):

    try:
        text_split = text.split(",")
        at_least_two_commas = (len(text_split) >= 3)
        state_zip_exists = bool(re.search(r"\w{2}\s\d{5}", text_split[-1]))
        correct_state = (text_split[-1].strip()[:2] == state)
        return True if at_least_two_commas & correct_state & state_zip_exists else False

    except IndexError:
        return False

def is_phone_number(text):

    expression = r"[(]?\d{3}[)]?\s?\d+[-]?\d+"

    return True if bool(re.search(expression, text)) else False

def find_day_of_week(text, days_of_week):

    expression = rf"({'|'.join(days_of_week)})"
    return re.search(expression, text).group()