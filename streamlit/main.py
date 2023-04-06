import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    df = pd.read_csv("./maps-search/AZ-master.csv")
    df.zipcode = df.zipcode.map(lambda x: pd.NA if pd.isna(x) else int(x))
    df = df[df.state == "AZ"]
    return df

@st.cache
def convert_df_for_download(df):
    return df.to_csv().encode('utf-8')

def run_webapp():
    st.title("Forward Party Arizona")

    page_dict = {
        # "Welcome": page_welcome,
        "Find Locations": page_filter,
        "Add Volunteering Event": page_survey,
        "Provide feedback": page_feedback
    }

    page_names = list(page_dict.keys())

    page = st.sidebar.radio("Select a page", page_names, label_visibility='collapsed')

    page_dict[page]()


def page_welcome():
    st.write("Find volunteer location recommendations, and share data to make Forward volunteering more effective.")

def page_filter():

    df_filtered = df.copy()

    # TODO
    # don't just filter for exact zipcode; have a ranking system that includes proximal zipcodes
    # zipcode_filter = st.text_input("Zipcode:")
    zipcodes = sorted(df_filtered.zipcode.dropna().unique().tolist())
    zipcode_filter = st.multiselect("Zipcode(s):", zipcodes)
    if zipcode_filter:
        # mask_zipcode = df_filtered.Zipcode == zipcode_filter
        mask_zipcode = df_filtered.zipcode.isin(zipcode_filter)
        df_filtered = df_filtered[mask_zipcode]

    location_types = sorted(df_filtered.location_category.unique().tolist())
    # location_types = ["park"]
    # location_bool_filter = st.radio("Location Type:", ["Any", "Choose"])
    # if location_bool_filter == "Choose":
    location_type_filter = st.multiselect("Location Type(s):", location_types, help="Choose one or more options")
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

    df_display = df_filtered[['location_id', 'business_name', 'address', 'phone_number', 'location_category']].copy()
    df_display.index = range(1, df_display.shape[0]+1)
    df_display.columns = ["ID", "Name", "Address", "Phone Number", "Category"]

    # top_n = 10
    st.write(f"{df_filtered.shape[0]} records")
    st.write(df_display)

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
            with st.form(key="Share volunteer data"):

                survey_bool_setup = st.radio("Were you allowed to set up here?", options=["no", "yes"])
                survey_notes = st.text_area("Please add any notes for future volunteers:", height=150)

                

        # col1 = st.text_input("Column 1")
        # col2 = st.number_input("Column 2", format="%.2f")
        # col3 = st.number_input("Column 3", step=1)

                submit_button = st.form_submit_button("Submit")

                if submit_button:
                    print(survey_bool_setup, survey_notes)
                    st.success("Data added successfully")


def page_feedback():
    st.write("""
    This webapp is in early development. Your feedback is incredibly valuable!\n
    Please share any suggestions.
    """)

    with st.form(key="Feedback"):
        feedback = st.text_area("Feedback:", height=200)

        submit_button = st.form_submit_button("Submit")
        if submit_button:
            ## email Matthew
            st.success("Data added successfully")


if __name__ == "__main__":
    df = load_data()
    run_webapp()