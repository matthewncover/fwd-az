import pandas as pd, re, os
import secrets, string
import business_metadata_regex as bmr
from geopy.geocoders import Nominatim

def postprocess_addresses(fn):
    df = pd.read_csv(fn)

    df.drop(["state_abr", "nan_opens", "nan_closes"], axis=1, inplace=True)

    df["city"], df["st"], df["zipcode"] = zip(*df.address.map(bmr.address_breakdown))

    def filter_colnames(df, s:str):
        return df.columns[df.columns.map(lambda x: s in x)].tolist()

    non_dow_colnames = [x for x in df.columns if not bool(re.search(r"open|close|traffic", x))]
    dow_colnames = filter_colnames(df, "open") + filter_colnames(df, "close") + filter_colnames(df, "traffic")

    df = df[non_dow_colnames + dow_colnames]

    return df

# def zipcode_to_latlon(df):
#     geolocator = Nominatim(user_agent='fwd_az')

#     def geocode(zipcode):
#         location = geolocator.geocode(zipcode)
#         return location.latitude, location.longitude
    
#     df[""]

def add_location_category(df, csv):
    location_category = csv.split(".")[0].split("_")[-1].replace("+", " ")
    df["location_category"] = location_category
    return df

def generate_code():
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(9))

def add_location_id(df):
    if 'location_id' not in df.columns:
        df["location_id"] = [generate_code() for _ in range(df.shape[0])]
    df.location_id = df.location_id.fillna(generate_code())

    while df.location_id.value_counts().max() > 1:
        duplicates = df[df.duplicated(["location_id"])]

        df.loc[duplicates.index, 'location_id'] = df.loc[duplicates.index].location_id.map(lambda x: generate_code())

    return df

def combine_save_datasets():

    csvs = [x for x in os.listdir() if x.endswith(".csv") and '-master' not in x]

    location_category = csvs[0].strip(".csv").split("_")[-1].replace("+", " ")
    if os.path.exists("./AZ-master.csv"):
        df_master = pd.read_csv("./AZ-master.csv", dtype={"zipcode": str})
        csv_start_index = 0
    else:
        df_master = pd.read_csv(csvs[0], dtype={"zipcode": str})
        csv_start_index = 1
    
    df_master["location_category"] = location_category

    for csv in csvs[csv_start_index:]:
        df = pd.read_csv(csv, dtype={"zipcode": str})
        df = add_location_category(df, csv)
        mask_new = ~df.href_url.isin(df_master.href_url.unique().tolist())
        df_new = df[mask_new]

        df_master = pd.concat([df_master, df_new])

    df_master = df_master.reset_index(drop=True)

    df_master = add_location_id(df_master)



    df_master.to_csv("AZ-master.csv", index=False)


if __name__ == "__main__":
    os.chdir("C:/Users/matthew/OneDrive/Desktop/dev/fwd-az/maps-search")
    # for filename in ["AZ_dispensary.csv"]:
    #     df = postprocess_addresses(filename)

    #     df.to_csv(filename, index=False)

    combine_save_datasets()