import numpy as np
import pandas as pd

from scr.scraping.scraper import InfoSUNAT
from scr.data_processing.data_cleaning import CleanInfoSUNAT

def ejecutar_programa():
    path_data_rucs = "../data/raw/rucs_part1.csv"
    data_rucs = pd.read_csv(path_data_rucs, sep="|", header=0)
    rucs_array = np.array(data_rucs)

    info_rucs = []
    for idx, ruc in enumerate(rucs_array):
        num_ruc = ruc[1]
        objSUNAT = InfoSUNAT(num_ruc)
        resultado = objSUNAT.consultar_ruc()
        if resultado:
            info_rucs.append(resultado)

        if idx % 100 == 0:
            print(f"Index: {idx}")

    objCleanSUNAT = CleanInfoSUNAT(info_rucs)
    objCleanSUNAT.save_json(pathToSave="../data/raw/data_info_rucs.json")

    """
    objCleanSUNAT = CleanInfoSUNAT(resultado)
    info_ruc = objCleanSUNAT.get_info_ruc()
    representantes_legales = objSUNAT.representantes_legales(info_ruc[1], info_ruc[0])
    if representantes_legales:
        all_info_represtantes_legales.append(representantes_legales)
    """

    # Tarea: Crear el export.

if __name__ == "__main__":
    ejecutar_programa()


