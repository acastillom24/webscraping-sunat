import numpy as np
import pandas as pd
from tqdm import tqdm

from scr.scraping.scraper import InfoSUNAT
from scr.data_processing.data_cleaning import CleanInfoSUNAT


def split_csv(input_path, output_prefix, chunk_size=5000):
    df = pd.read_csv(input_path, sep="|", header=0)

    total_records = len(df)
    num_chunks = total_records // chunk_size + (1 if total_records % chunk_size != 0 else 0)

    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = (i + 1) * chunk_size
        chunk_df = df.iloc[start_idx:end_idx]

        output_path = f"{output_prefix}_{i + 1}.csv"
        chunk_df.to_csv(output_path, index=False, sep="|")  # Ajusta el separador según tus preferencias

        print(f"Archivo {i + 1}/{num_chunks} creado: {output_path}")


def get_check_ruc(input_path, output_path):
    df = pd.read_csv(input_path, sep="|", header=0)
    arr = np.array(df)

    info = []
    num_random = None
    for idx, el in tqdm(enumerate(arr), total=len(arr), desc="Processing RUCs"):
        num_ruc = el[1]
        obj = InfoSUNAT(num_ruc)
        result = obj.check_ruc(num_random)
        if result:
            num_random = result["num_random"]
            info.append(result["data"])

    obj_clean = CleanInfoSUNAT(info)
    obj_clean.save_json(pathToSave=output_path)


if __name__ == "__main__":
    # split_csv("../data/raw/rucs.csv", "../data/processed/df")
    get_check_ruc("../data/processed/df_1.csv", "../data/processed/df_1.json")
