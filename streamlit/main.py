import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    return pd.read_csv("./maps-search/AZ_park.csv")

@st.cache
def convert_df_for_download(df):
    return df.to_csv().encode('utf-8')

def run_webapp():
    st.title("Forward Party AZ")

    page_dict = {
        "Welcome": page_welcome,
        "Find Locations": page_filter,
        "Add Volunteering Event": page_survey
    }

    page_names = list(page_dict.keys())

    page = st.sidebar.radio("Select a page", page_names, label_visibility='collapsed')

    page_dict[page]()


def page_welcome():
    st.write("Find volunteer location recommendations, and share data to make Forward volunteering more effective.")

def page_filter():

    st.write("Filter data")

    df_filtered = df.copy()

    # TODO
    # don't just filter for exact zipcode; have a ranking system that includes proximal zipcodes
    zipcode_filter = st.text_input("Zipcode:")
    if zipcode_filter:
        mask_zipcode = df_filtered.Zipcode == zipcode_filter
        df_filtered = df_filtered[mask_zipcode]

    # location_types = df_filtered.location_name.unique().tolist()
    location_types = ["park"]
    location_bool_filter = st.radio("Location Type:", ["Any", "Choose"])
    if location_bool_filter == "Choose":
        location_type_filter = st.multiselect("Location Type (select one or more):", location_types, help="Choose one or more options")
    # location_type_filter.
    # if location_type_filter:
        # mask_location = df_filtered.location_name.isin(location_type_filter)
        # df_filtered = df_filtered[mask_location]

    # TODO
    #### need widget for calendar day
    days_of_week = ["Any", "Saturday", "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    volunteer_date_of_week = st.selectbox("Day of week:", options=days_of_week)


    volunteer_start_time = st.time_input("Start time (H:MM)", value=None)
    volunteer_end_time = st.time_input("End time (H:MM)", value=None)
    if volunteer_start_time and volunteer_end_time:
        # TODO
        # mask_start_time = df_filtered[f"{day_of_week}_open_time"] 

        # enter range of when you plan to volunteer
        # or
        # enter whenisgood results

        mask_start_time = True
        mask_end_time = True
        # df_filtered = df_filtered[mask_start_time & mask_end_time]
        pass

    df_display = df_filtered.copy()
    df_display.index = range(1, df_display.shape[0]+1)

    top_n = 10
    st.write(f"Top {top_n} recommendations:")
    st.write(df_display.head(top_n))

def page_survey():

    st.write("Add data")

    with st.form(key="Share volunteer data"):
        col1 = st.text_input("Column 1")
        col2 = st.number_input("Column 2", format="%.2f")
        col3 = st.number_input("Column 3", step=1)

        submit_button = st.form_submit_button("Submit")

    if submit_button:
        print(col1, col2, col3)
        st.success("Data added successfully")

if __name__ == "__main__":
    df = load_data()
    run_webapp()