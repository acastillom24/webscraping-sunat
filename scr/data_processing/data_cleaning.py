import pandas as pd
import json

class CleanInfoSUNAT:
    def __init__(self, info_sunat):
        self.info = info_sunat

    def clean_info(self):
        print("En proceso")

    def get_info_ruc(self):
        txt = self.info["Número de RUC"]
        return txt.split(" - ")

    def save_json(self, pathToSave):
        try:
            with open(pathToSave, 'w', encoding='utf-8') as json_file:
                json.dump(self.info, json_file, ensure_ascii=False, indent=4)
            print(f"Los datos han sido respaldados en {pathToSave}")
        except Exception as e:
            print(f"Error al respaldar los datos: {str(e)}")

    def save_csv(self, path):
        keys = {
            "data": [
                "Número de RUC",
                "Tipo Contribuyente",
                "Nombre Comercial",
                "Fecha de Inscripción",
                "Fecha de Inicio de Actividades",
                "Estado del Contribuyente",
                "Condición del Contribuyente",
                "Domicilio Fiscal",
                "Sistema Emisión de Comprobante",
                "Actividad Comercio Exterior",
                "Sistema Contabilidad",
                "Emisor electrónico desde",
                "Comprobantes Electrónicos",
                "Afiliado al PLE desde"
            ],
            "actividad_economica": [
                "Número de RUC",
                "Actividad(es) Económica(s)"
            ],
            "comprobantes_pago": [
                "Número de RUC",
                "Comprobantes de Pago c/aut. de impresión (F. 806 u 816)"
            ],
            "sistemas_emision": [
                "Número de RUC",
                "Sistema de Emisión Electrónica"
            ],
            "padron": [
                "Número de RUC",
                "Padrones"
            ]
        }

        for key, value in keys.items():
            obj_select = {el: self.info[el] for el in value}

            dfs = []
            for col, values in obj_select.items():
                if isinstance(values, list):
                    df_list = pd.DataFrame({col: values})
                    df_data = pd.DataFrame({key: [obj_select[key]] * len(df_list) for key in obj_select if key != col})
                    df = pd.concat([df_data, df_list], axis=1)
                    dfs.append(df)

            result_df = pd.concat(dfs, axis=1) if dfs else pd.DataFrame([obj_select])
            path_complete = path + "\\" + key + ".csv"
            result_df.to_csv(
                path_or_buf=path_complete,
                index=False,
                sep="|",
                encoding='utf-8'
            )
