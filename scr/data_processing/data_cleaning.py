class CleanInfoSUNAT:
    def __init__(self, info_sunat):
        self.info = info_sunat

    def clean_info(self):
        print("En proceso")

    def get_info_ruc(self):
        txt = self.info["Número de RUC"]
        return txt.split(" - ")
