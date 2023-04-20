import streamlit as st
import os, pandas as pd, time, datetime as dt
# from dotenv import load_dotenv

from feedback import send_email
from w2m import When2MeetReader

st.set_page_config(page_title="My Streamlit App", layout="wide", initial_sidebar_state="collapsed", page_icon=":guardsman:", 
                   menu_items={"Get Help": "https://www.streamlit.io/docs/"})

# load_dotenv()

@st.cache_data
def load_data():
    ###
    # os.chdir("./streamlit")
    ###
    df = pd.read_csv("./AZ-master.csv")
    df.zipcode = df.zipcode.map(lambda x: pd.NA if pd.isna(x) else int(x))
    df = df[df.state == "AZ"]
    return df

@st.cache_data
def convert_df_for_download(df):
    return df.to_csv(index=None).encode('utf-8')

def run_webapp():
    st.title("Forward Party Arizona")

    page_login()

def page_login():

    logged_in = st.session_state.get("logged_in", False)

    if not logged_in:
        st.write("#### Login")
        username = st.text_input("Username:")
        password = st.text_input("Password:", type="password")
        # if (username, password) == (os.environ["USER"], os.environ["PASS"]):
        if (username, password) == (st.secrets["USER"], st.secrets["PASS"]):
            st.session_state.logged_in = True
            st.success("Welcome")
            st.experimental_rerun()
            # sidebar_pages()
    else:
        sidebar_pages()


def sidebar_pages():
    page_dict = {
        "Welcome": page_welcome,
        "Find Locations": page_filter,
        "Add Volunteering Event": page_survey,
        "Provide feedback": page_feedback
    }

    page_names = list(page_dict.keys())

    page = st.sidebar.radio("Select a page", page_names, label_visibility='collapsed')

    page_dict[page]()


def page_welcome():
    st.write("#### Welcome, amazing volunteer!")

    st.write("Current goal: 55,000 signatures")
    progress_bar = st.progress(0)

    for i in range(100):
        # Perform some long-running computation here
        time.sleep(0.03)
        progress_bar.progress(i + 1)

    time.sleep(1.5)
    st.write("There's a sidebar on the left.")

def page_filter():

    df_filtered = df.copy()

    # TODO
    # don't just filter for exact zipcode; have a ranking system that includes proximal zipcodes
    # zipcode_filter = st.text_input("Zipcode:")
    zipcodes = sorted(df_filtered.zipcode.dropna().unique().tolist())
    zipcode_filter = st.multiselect("Zipcode:", zipcodes)
    if zipcode_filter:
        # mask_zipcode = df_filtered.zipcode == zipcode_filter
        mask_zipcode = df_filtered.zipcode.isin(zipcode_filter)
        df_filtered = df_filtered[mask_zipcode]

    cities = sorted(df_filtered.city.dropna().unique().tolist())
    city_filter = st.multiselect("City:", cities)
    if city_filter:
        mask_city = df_filtered.city.isin(city_filter)
        df_filtered = df_filtered[mask_city]

    location_types = sorted(df_filtered.location_category.unique().tolist())
    # location_types = ["park"]
    # location_bool_filter = st.radio("Location Type:", ["Any", "Choose"])
    # if location_bool_filter == "Choose":
    location_type_filter = st.multiselect("Location Type:", location_types, help="Choose one or more options")
    if location_type_filter:
        df_filtered = df_filtered[df_filtered.location_category.isin(location_type_filter)]
    # location_type_filter.
    # if location_type_filter:
        # mask_location = df_filtered.location_name.isin(location_type_filter)
        # df_filtered = df_filtered[mask_location]

    # TODO
    #### need widget for calendar day
    # days_of_week = ["Any", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    # volunteer_date_of_week = st.selectbox("Day of week:", options=days_of_week)


    # volunteer_start_time = st.time_input("Start time (H:MM)", value=None)
    # volunteer_end_time = st.time_input("End time (H:MM)", value=None)
    # if volunteer_start_time and volunteer_end_time:
        # TODO
        # mask_start_time = df_filtered[f"{day_of_week}_open_time"] 

        # enter range of when you plan to volunteer
        # or
        # enter whenisgood results

        # mask_start_time = True
        # mask_end_time = True
        # df_filtered = df_filtered[mask_start_time & mask_end_time]
        # pass

    with st.form(key="When2Meet"):
        w2m_url = st.text_input("When2Meet URL:")

        submit_button = st.form_submit_button("Add")

        if submit_button:
            if w2m_url:
                reader = When2MeetReader(w2m_url)
                
                if reader.is_valid_url:
                    container = st.container()
                    wip_text = container.text("Retrieving results...")
                    reader.get_dataframe()
                    wip_text.empty()
                    container.empty()

                    st.success("Successfully Added")

                else:
                    st.error("Invalid When2Meet URL")


    df_display = (
        df_filtered
        [['location_id', 'business_name', 'address', 'phone_number', 'location_category', 'href_url']]
        .sort_values(by=["location_category", "business_name"])
        .copy()
        )
    df_display.index = range(1, df_display.shape[0]+1)
    df_display.columns = ["ID", "Name", "Address", "Phone Number", "Category", "Google Maps URL"]

    st.write(f"{df_filtered.shape[0]} records")
    st.write(df_display)

    if df_display.shape[0] != 0:
        csv = convert_df_for_download(df_display)

        today = dt.datetime.today().strftime('%b %d %y')

        st.download_button(
            label=f"Download as .csv",
            data=csv,
            file_name=f'fwd volunteer data {today}.csv',
            mime='text/csv',
        )

def page_survey():

    location_id = st.text_input("Location ID")

    if not location_id:
        pass

    elif location_id not in df.location_id.unique():
        st.error("Invalid location ID")

    else:
        df_location = df[df.location_id == location_id]
        location_name = df_location.business_name.iloc[0]
        location_address = df_location.address.iloc[0]
        location_info = f"""
        {location_name}\n
        {location_address}
        """
        st.write(location_info)
        correct_business = st.radio("Is this correct?", options=["no", "yes"])
    
        if correct_business == "yes":
            survey_bool_setup = st.radio("Were you allowed to set up here?", options=["no", "yes"])

            with st.form(key="Share volunteer data"):

                if survey_bool_setup == "yes":
                    survey_num_signatures = int(st.number_input("How many signatures were collected?", format="%d", value=0))
                    survey_num_volunteers = int(st.number_input("How many volunteers?", format="%d", value=0))
                    survey_num_hours = st.number_input("How many hours did you / your team collect signatures for? (best estimate)")
                
                survey_notes = st.text_area("Please add any notes for future volunteers:", height=150)

                submit_button = st.form_submit_button("Submit")

                if submit_button:
                    ### add to a second table, connect to location_id
                    # TODO
                    raise NotImplementedError
                    st.success("Data added successfully")


def page_feedback():
    st.write("""
    This webapp is in early development. Your feedback is incredibly valuable!\n
    Note: will log you out
    """)

    with st.form(key="Feedback"):
        feedback = st.text_area("Please share any suggestions:", height=200)

        submit_button = st.form_submit_button("Submit")
        if submit_button:
            ## email Matthew
            container = st.container()
            sending_message = container.text("Sending...")
            subject = "Streamlit Feedback - Forward Arizona"

            try:
                send_email(subject, feedback)
                sending_message.empty()
                container.empty()
                st.success("Thank you!! Feedback shared. Logging out...")
            
            except:
                sending_message.empty()
                container.empty()
                st.error("Something went wrong, apologies.")

            time.sleep(2)
            
            st.session_state.logged_in = False        
            page_login()
            st.experimental_rerun()

if __name__ == "__main__":
    df = load_data()
    run_webapp()