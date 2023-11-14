## Estructura del proyecto

```bash
sunat/
│
├── data/
│   ├── raw/               # Datos crudos obtenidos del scraping
│   ├── processed/          # Datos procesados y limpios
│
├── src/
│   ├── main.py            # Archivo principal para ejecutar el scraping
│   ├── scraping/          # Módulos para realizar el web scraping
│       ├── scraper.py     # Lógica de scraping
│   ├── data_processing/   # Módulos para procesar los datos
│       ├── data_cleaning.py  # Limpieza y procesamiento de datos
│
├── notebooks/              # Jupyter notebooks para análisis y visualización
│
├── requirements.txt        # Librerías utilizadas
├── README.md               # Documentación del proyecto

```

## Generar el archivo `requirements.txt`

```bash
pip freeze > requirements.txt
```

## Ejecutar el archivo `requirements.txt`

```bash
pip install -r ".\requirements.txt"
```
