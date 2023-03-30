import re
from numpy import nan

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
    try:
        return re.search(expression, text).group()
    except AttributeError:
        return nan

##

def address_breakdown(text):

    state_abr_expression = ("""
    AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|
    KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|
    OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY
    """).strip()

    state_expression = ("""
    Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|Hawaii|
    Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|Michigan|
    Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New[ ]Hampshire|New[ ]Jersey|New[ ]Mexico|
    New[ ]York|North[ ]Carolina|North[ ]Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|Rhode[ ]Island|
    South[ ]Carolina|South[ ]Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|West[ ]Virginia|
    Wisconsin|Wyoming
    """).strip()

    city_expression = ("""
    (?:[A-Z][a-z.-]+[ ]?)+
    """).strip()

    zipcode_expression = ("""
    \d{5}(?:-\d{4})?
    """).strip()

    try:
        address_elements = re.search(rf"({city_expression}),[ ](?:({state_abr_expression}))[ ]({zipcode_expression})", text)
        city, state, zipcode = address_elements.groups()
        
        return city, state, zipcode

    except (AttributeError, TypeError):
        return None, None, None



