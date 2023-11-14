from scr.scraping.scraper import InfoSUNAT
from scr.data_processing.data_cleaning import CleanInfoSUNAT
def ejecutar_programa():
    num_ruc = "20202380621"
    objSUNAT = InfoSUNAT(num_ruc)
    resultado = objSUNAT.consultar_ruc()
    if resultado:
        objCleanSUNAT = CleanInfoSUNAT(resultado)
        info_ruc = objCleanSUNAT.get_info_ruc()
        representantes_legales = objSUNAT.representantes_legales(info_ruc[1], info_ruc[0])
    print(representantes_legales)

if __name__ == "__main__":
    ejecutar_programa()


