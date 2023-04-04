import pandas as pd, re, os
import business_metadata_regex as bmr

def postprocess_addresses(fn):
    df = pd.read_csv(fn)

    df.drop("state_abr", axis=1, inplace=True)

    df["city"], df["st"], df["zipcode"] = zip(*df.address.map(bmr.address_breakdown))

    def filter_colnames(df, s:str):
        return df.columns[df.columns.map(lambda x: s in x)].tolist()

    non_dow_colnames = [x for x in df.columns if not bool(re.search(r"open|close|traffic", x))]
    dow_colnames = filter_colnames(df, "open") + filter_colnames(df, "close") + filter_colnames(df, "traffic")

    df = df[non_dow_colnames + dow_colnames]

    return df

def combine_save_datasets():

    csvs = [x for x in os.listdir() if x.endswith(".csv")]

    location_category = csvs[0].strip(".csv").split("_")[-1].replace("+", " ")
    df_master = pd.read_csv(csvs[0], dtype={"zipcode": str})
    df_master["location_category"] = location_category

    for csv in csvs[1:]:
        location_category = csv.strip(".csv").split("_")[-1].replace("+", " ")
        df = pd.read_csv(csv, dtype={"zipcode": str})
        df["location_category"] = location_category

        df_master = pd.concat([df_master, df])

    df_master = df_master.reset_index(drop=True)

    df_master.to_csv("AZ-master.csv", index=False)


if __name__ == "__main__":
    for filename in ["AZ_dispensary.csv"]:
        df = postprocess_addresses(filename)

        df.to_csv(filename, index=False)