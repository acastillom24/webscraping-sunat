from bs4 import BeautifulSoup
import requests

BASE_URL = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-type": "application/x-www-form-urlencoded",
}

proxy = {'https': 'https://10.112.244.80:8080', 'http': 'http://10.112.244.80:8080'}

class InfoSUNAT:
    def __init__(self, num_ruc):
        self.num_ruc = num_ruc

        if self.validar_ruc:
            self.sunat = self.establish_connection()
        else:
            print("El RUC ingresado no es valido.")

    def validar_ruc(self):
        suma_total, k, t = 0, 5, 7
        for idx, num in enumerate(self.num_ruc):
            peso = k if idx <= 3 else t
            suma_total += int(num) * peso
            k, t = k - 1 if idx <= 3 else k, t - 1

        resto = suma_total % 11
        complemento = '0' if resto == 1 else str(11 - resto)[0]

        return self.num_ruc[-1] == complemento

    def establish_connection(self):
        payload = {"accion": "consPorRazonSoc", "razSoc": "Alin"}
        sunat = requests.session()
        try:
            response = sunat.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                return sunat
            else:
                print(f"La solicitud falló. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")
            return None

    def getRandom(self):
        payload = {"accion": "consPorRazonSoc", "razSoc": "Alin"}
        try:
            response = self.sunat.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                numRndInput = soup.find("input", {"name": "numRnd"})
                return numRndInput.get("value")
            else:
                print(f"La solicitud falló. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")
            return None

    def consultar_ruc(self):
        try:
            key = self.getRandom()
            if not key:
                print("No se pudo obtener el número aleatorio")
                return None

            payload = {
                "accion": "consPorRuc",
                "actReturn": "1",
                "modo": "1",
                "nroRuc": self.num_ruc,
                "numRnd": key
            }

            response = self.sunat.post(BASE_URL, data=payload, headers=headers)

            if response.status_code == 200:
                return self.parse_response(response.text)
            else:
                print(f"Error en la solicitud a la SUNAT. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")
            return None

    def parse_response(self, html_text):
        data = {}
        soup = BeautifulSoup(html_text, "html.parser")
        div_tags = soup.find_all("div", {"class": "list-group-item"})

        if div_tags:
            for div_tag in div_tags:
                h4_tag = div_tag.find("h4", {"class": "list-group-item-heading"})
                if h4_tag:
                    keys, values, value = [], [], []
                    key = h4_tag.get_text().strip(":")
                    if key == "Número de RUC":
                        h4_tags = div_tag.find_all("h4", {"class": "list-group-item-heading"})
                        value = h4_tags[1].get_text().strip()
                    elif key in ["Fecha de Inscripción", "Sistema Emisión de Comprobante"]:
                        h4_tags = div_tag.find_all("h4", {"class": "list-group-item-heading"})
                        keys = [h4.get_text().strip(":") for h4 in h4_tags]
                        values = self.extract_value(div_tag)
                    else:
                        value = self.extract_value(div_tag)

                    try:
                        if keys:
                            data.update(dict(zip(keys, values)))
                        elif value is None:
                            data[key] = '-'
                        elif len(value) > 1:
                            data[key] = value
                        else:
                            data[key] = value[0]
                    except Exception as e:
                        print(f"Error en el ruc: {self.num_ruc}")
        return data

    def extract_value(self, div_tag):
        p_tags = div_tag.find_all("p", {"class": "list-group-item-text"})
        td_elements = div_tag.find_all("td")

        if p_tags:
            return [p.get_text().strip() for p in p_tags]
        elif td_elements:
            return [td.get_text().strip() for td in td_elements]

        return None

    def getRepresentantesLegales(self, des_ruc, nro_ruc):
        try:
            payload = {
                "accion": "getRepLeg",
                "contexto": "ti-it",
                "modo": "1",
                "desRuc": des_ruc,
                "nroRuc": nro_ruc
            }
            response = self.sunat.post(BASE_URL, data=payload, headers=headers, proxies=proxy, verify=False)
            if response.status_code == 200:
                data = []
                soup = BeautifulSoup(response.text, "html.parser")

                thead = soup.find("thead")
                if thead:
                    th_elements = thead.find_all("th")
                    keys = [th.get_text() for th in th_elements]
                    keys.append('nro_ruc')

                    tbody = soup.find("tbody")
                    if tbody:
                        tr_elements = tbody.find_all("tr")
                        for tr in tr_elements:
                            td_elements = tr.find_all("td")
                            td_values = [td.get_text().strip() for td in td_elements]
                            td_values.append(nro_ruc)
                            data.append(dict(zip(keys, td_values)))
                return data
            else:
                print(f"Error, no se puedo obtener los representantes. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")

    def getCantidadTrabajadores(self, des_ruc, nro_ruc):
        try:
            payload = {
                "accion": "getCantTrab",
                "contexto": "ti-it",
                "modo": "1",
                "nroRuc": nro_ruc,
                "desRuc": des_ruc
            }
            response = self.sunat.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                data = []
                soup = BeautifulSoup(response.text, "html.parser")

                thead = soup.find("thead")
                if thead:
                    th_elements = thead.find_all("th")
                    keys = [th.get_text() for th in th_elements]
                    keys.append('nro_ruc')

                    tbody = soup.find("tbody")
                    if tbody:
                        tr_elements = tbody.find_all("tr")
                        for tr in tr_elements:
                            td_elements = tr.find_all("td")
                            td_values = [td.get_text().strip() for td in td_elements]
                            td_values.append(nro_ruc)
                            data.append(dict(zip(keys, td_values)))
                return data
            else:
                print(f"Error, no se puedo obtener el número de trabajadores. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")

    def getDeudaCoactiva(self, des_ruc, nro_ruc):
        try:
            payload = {
                "accion": "getInfoDC",
                "contexto": "ti-it",
                "modo": "1",
                "nroRuc": nro_ruc,
                "desRuc": des_ruc
            }
            response = self.sunat.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                data = []
                soup = BeautifulSoup(response.text, "html.parser")

                thead = soup.find("thead")
                if thead:
                    th_elements = thead.find_all("th")
                    keys = [th.get_text() for th in th_elements]
                    keys.append('nro_ruc')

                    tbody = soup.find("tbody")
                    if tbody:
                        tr_elements = tbody.find_all("tr")
                        for tr in tr_elements:
                            td_elements = tr.find_all("td")
                            td_values = [td.get_text().strip() for td in td_elements]
                            td_values.append(nro_ruc)
                            data.append(dict(zip(keys, td_values)))
                return data
            else:
                print(f"Error, no se puedo obtener el número de trabajadores. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")

    def getEstablecimientosAnexos(self, des_ruc, nro_ruc):
        try:
            payload = {
                "accion": "getLocAnex",
                "contexto": "ti-it",
                "modo": "1",
                "nroRuc": nro_ruc,
                "desRuc": des_ruc
            }
            response = self.sunat.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                data = []
                soup = BeautifulSoup(response.text, "html.parser")

                thead = soup.find("thead")
                if thead:
                    th_elements = thead.find_all("th")
                    keys = [th.get_text() for th in th_elements]
                    keys.append('nro_ruc')

                    tbody = soup.find("tbody")
                    if tbody:
                        tr_elements = tbody.find_all("tr")
                        for tr in tr_elements:
                            td_elements = tr.find_all("td")
                            td_values = [td.get_text().strip() for td in td_elements]
                            td_values.append(nro_ruc)
                            data.append(dict(zip(keys, td_values)))
                return data
            else:
                print(f"Error, no se puedo obtener el número de trabajadores. Código de estado: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error al conectar: {e}")