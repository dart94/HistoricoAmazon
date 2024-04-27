from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Función para obtener el precio de un producto en Amazon


def obtener_precio_amazon(url):
    # Configurar el navegador
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url)

    # Esperar a que la página cargue completamente y obtener el HTML
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'a-price-whole')))
    html = driver.page_source
    driver.quit()

    # Analizar el HTML con BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Encontrar el primer elemento que contiene el precio
    price_element = soup.find(class_='a-price-whole')
    if price_element:
        return price_element.get_text().replace(',', '')  # Convertir a string
    else:
        return None


# URL de búsqueda del Google Pixel 8 Pro en Amazon
url_busqueda = 'https://www.amazon.com.mx/s?k=pixel+8+pro&crid=Y5BI0E5124Y1&sprefix=pixel+8%2Caps%2C168&ref=nb_sb_ss_ts-doa-p_1_7'

# Obtener la URL del primer resultado de búsqueda
options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)
driver.get(url_busqueda)

# Esperar a que el elemento esté presente en la página
primer_resultado = WebDriverWait(driver, 15).until(EC.presence_of_element_located(
    (By.CSS_SELECTOR, '.widgetId\\=search-results_1 > span:nth-child(1) > div:nth-child(1) > div:nth-child(1)')))
url_producto = primer_resultado.find_element(
    By.CSS_SELECTOR, 'a').get_attribute('href')
driver.quit()

# Obtener el precio actual
precio_actual = obtener_precio_amazon(url_producto)

# Crear un DataFrame para el historial de precios si no existe
try:
    historial_precios = pd.read_csv('historial_precios_pixel_8_pro.csv')
except FileNotFoundError:
    historial_precios = pd.DataFrame(columns=['Fecha', 'Precio'])

# Crear un nuevo registro para el historial de precios
nuevo_registro = pd.DataFrame({'Fecha': [datetime.now().date()],
                               'Precio': [precio_actual]})

# Concatenar el nuevo registro al historial de precios
historial_precios = pd.concat(
    [historial_precios, nuevo_registro], ignore_index=True)

# Guardar el historial de precios en un archivo CSV
historial_precios.to_csv('historial_precios_pixel_8_pro.csv', index=False)

# Mostrar el historial de precios
print("Historial de precios del Google Pixel 8 Pro:")
print(historial_precios)

# Convertir la columna 'Precio' a tipo numérico y eliminar los valores NaN o no numéricos
historial_precios['Precio'] = pd.to_numeric(
    historial_precios['Precio'], errors='coerce')
historial_precios.dropna(subset=['Precio'], inplace=True)

# Convertir la columna de Fecha a datetime
historial_precios['Fecha'] = pd.to_datetime(historial_precios['Fecha'])

# Ordenar por Precio de forma ascendente
historial_precios.sort_values(by='Precio', inplace=True)

# Graficar el historial de precios
plt.figure(figsize=(10, 6))

# Plotear los datos
plt.plot(historial_precios['Fecha'], historial_precios['Precio'], marker='o')

# Añadir una anotación para resaltar la tendencia del precio
# Calcular el promedio del precio
tendencia_precio = historial_precios['Precio'].mean()
# Línea horizontal para la tendencia
plt.axhline(y=tendencia_precio, color='r', linestyle='--')
plt.text(historial_precios['Fecha'].iloc[-1], tendencia_precio, f'Tendencia: {round(tendencia_precio, 2)} MXN',
         horizontalalignment='right', verticalalignment='bottom')

# Personalizar la apariencia de la gráfica
plt.title('Historial de precios del Google Pixel 8 Pro')
plt.xlabel('Fecha')
plt.ylabel('Precio (MXN)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()

# Mostrar la gráfica
plt.show()
