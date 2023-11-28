from bs4 import BeautifulSoup
import requests

BASE_URL = "https://e-consultaruc.sunat.gob.pe/cl-ti-itmrconsruc/jcrS00Alias"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Content-type": "application/x-www-form-urlencoded",
}

proxy = {'https': 'https://10.112.244.80:8080', 'http': 'http://10.112.244.80:8080'}


def establish_connection():
    payload = {
        "accion": "consPorRazonSoc",
        "razSoc": "Alin"
    }
    req = requests.session()
    try:
        response = req.post(BASE_URL, data=payload, headers=headers)
        if response.status_code == 200:
            return req
        else:
            print(f"The request failed. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error connecting: {e}")
        return None


def extract_value(div_tag):
    p_tags = div_tag.find_all("p", {"class": "list-group-item-text"})
    td_elements = div_tag.find_all("td")

    if p_tags:
        return [p.get_text().strip() for p in p_tags]
    elif td_elements:
        return [td.get_text().strip() for td in td_elements]

    return None


class InfoSUNAT:
    def __init__(self, num_ruc):
        self.num_ruc = num_ruc

        if self.validate_ruc:
            self.req = establish_connection()
        else:
            print("The entered RUC is not valid.")

    def validate_ruc(self):
        total_sum, k, t = 0, 5, 7
        for idx, num in enumerate(self.num_ruc):
            weight = k if idx <= 3 else t
            total_sum += int(num) * weight
            k, t = k - 1 if idx <= 3 else k, t - 1

        rest = total_sum % 11
        complement = '0' if rest == 1 else str(11 - rest)[0]

        return self.num_ruc[-1] == complement

    def get_random(self):
        payload = {
            "accion": "consPorRazonSoc",
            "razSoc": "Alin"
        }
        try:
            response = self.req.post(BASE_URL, data=payload, headers=headers)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                num_rnd_input = soup.find("input", {"name": "numRnd"})
                return num_rnd_input.get("value")
            else:
                print(f"The request failed. Status code: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Error connecting: {e}")
            return None

    def check_ruc(self, num_random=None):
        try:
            key = num_random
            num_iter_max = 0

            while num_iter_max < 3 and key is None:
                key = self.get_random()
                num_iter_max += 1

            if num_iter_max == 3:
                print("Failed to obtain the random number.")
                return None

            payload = {
                "accion": "consPorRuc",
                "actReturn": "1",
                "modo": "1",
                "nroRuc": self.num_ruc,
                "numRnd": key
            }

            retry_count = 0
            while retry_count < 3:
                try:
                    response = self.req.post(BASE_URL, data=payload, headers=headers)
                    if response.status_code == 200:
                        return self.parse_response(response.text)
                    else:
                        print(f"The request failed. Status code: {response.status_code}")
                    retry_count += 1
                except requests.exceptions.RequestException as e:
                    print(f"Error Connecting: {e}")
                    retry_count += 1
                    self.req = establish_connection()
        except requests.exceptions.RequestException as e:
            print(f"Error Connecting: {e}")
            return None

    def parse_response(self, html_text):
        data = {}
        soup = BeautifulSoup(html_text, "html.parser")
        div_tags = soup.find_all("div", {"class": "list-group-item"})
        num_rnd_input = soup.find("input", {"name": "numRnd"})

        if num_rnd_input is not None:
            num_random = num_rnd_input.get("value")
        else:
            num_random = None

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
                        values = extract_value(div_tag)
                    else:
                        value = extract_value(div_tag)

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
                        print(f"Error Connecting: {self.num_ruc}\n{e}")
        return {"data": data, "num_random": num_random}

    def get_legal_representatives(self, des_ruc, nro_ruc):
        try:
            payload = {
                "accion": "getRepLeg",
                "contexto": "ti-it",
                "modo": "1",
                "desRuc": des_ruc,
                "nroRuc": nro_ruc
            }
            response = self.req.post(BASE_URL, data=payload, headers=headers)
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