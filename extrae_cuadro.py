def extraer_datos_resumen_provincia(driver):
    """
    Extrae los datos del resumen de la provincia que aparece en el cuadro inferior izquierdo.
    
    Args:
        driver: WebDriver de Selenium inicializado
    
    Returns:
        dict: Diccionario con la información de superficie, rendimiento, producción y participación
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import re
    
    try:
        # Esperar a que se cargue la tabla de resumen
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".celda_resumen"))
        )
        
        # Obtener el nombre de la provincia/departamento
        titulo_elemento = driver.find_element(By.CSS_SELECTOR, ".titulo_celda_resumen")
        nombre_provincia = titulo_elemento.text.replace("PROV.: ", "").replace("DPTO.: ", "").strip()
        
        # Extraer los valores de la tabla
        # Buscar los valores por clase
        valores = driver.find_elements(By.CSS_SELECTOR, ".valor_celda_resumen")
        
        # Crear diccionario para almacenar la información
        datos_resumen = {
            "provincia": nombre_provincia,
            "superficie_ha": None,
            "rendimiento_tha": None,
            "produccion_tm": None,
            "participacion_porcentaje": None
        }
        
        # Leer las etiquetas para asegurar que asignamos los valores correctamente
        etiquetas = driver.find_elements(By.CSS_SELECTOR, "div._ngcontent-ouq-7")
        textos_etiquetas = [etiqueta.text for etiqueta in etiquetas if etiqueta.text]
        
        # Intentar extraer los valores directamente
        for i, valor in enumerate(valores):
            valor_texto = valor.text.strip()
            
            # Buscar la etiqueta correspondiente
            if i < len(textos_etiquetas):
                etiqueta = textos_etiquetas[i].lower()
                
                if "superficie" in etiqueta:
                    datos_resumen["superficie_ha"] = float(valor_texto.replace(' ', '').replace(',', '.'))
                elif "rendimiento" in etiqueta:
                    datos_resumen["rendimiento_tha"] = float(valor_texto.replace(' ', '').replace(',', '.'))
                elif "produccion" in etiqueta:
                    datos_resumen["produccion_tm"] = float(valor_texto.replace(' ', '').replace(',', '.'))
                elif "participacion" in etiqueta:
                    datos_resumen["participacion_porcentaje"] = float(valor_texto.replace(' ', '').replace(',', '.'))
        
        # Si no se pudo extraer con el método anterior, intentar otro enfoque
        if not any(datos_resumen.values()):
            # Intentar extraer toda la tabla como texto
            tabla = driver.find_element(By.CSS_SELECTOR, "table#mytable")
            tabla_texto = tabla.text
            
            # Patrones para extraer los valores
            superficie_match = re.search(r'Superficie\s*\(ha\)\s*:\s*([\d\s.,]+)', tabla_texto)
            rendimiento_match = re.search(r'Rendimiento\s*\(t/ha\)\s*:\s*([\d\s.,]+)', tabla_texto)
            produccion_match = re.search(r'Produccion\s*\(tm\)\s*:\s*([\d\s.,]+)', tabla_texto)
            participacion_match = re.search(r'Participación\s*\(%\)\s*:\s*([\d\s.,]+)', tabla_texto)
            
            if superficie_match:
                datos_resumen["superficie_ha"] = float(superficie_match.group(1).replace(' ', '').replace(',', '.'))
            if rendimiento_match:
                datos_resumen["rendimiento_tha"] = float(rendimiento_match.group(1).replace(' ', '').replace(',', '.'))
            if produccion_match:
                datos_resumen["produccion_tm"] = float(produccion_match.group(1).replace(' ', '').replace(',', '.'))
            if participacion_match:
                datos_resumen["participacion_porcentaje"] = float(participacion_match.group(1).replace(' ', '').replace(',', '.'))
        
        # Método alternativo usando JavaScript
        if not any(datos_resumen.values()):
            datos_js = driver.execute_script("""
                const valores = Array.from(document.querySelectorAll('.valor_celda_resumen')).map(e => e.textContent.trim());
                const provincia = document.querySelector('.titulo_celda_resumen')?.textContent.trim();
                return {
                    provincia: provincia,
                    valores: valores
                };
            """)
            
            if datos_js and 'valores' in datos_js and len(datos_js['valores']) >= 4:
                # Asumiendo el orden: Superficie, Rendimiento, Producción, Participación
                datos_resumen["superficie_ha"] = float(datos_js['valores'][0].replace(' ', '').replace(',', '.'))
                datos_resumen["rendimiento_tha"] = float(datos_js['valores'][1].replace(' ', '').replace(',', '.'))
                datos_resumen["produccion_tm"] = float(datos_js['valores'][2].replace(' ', '').replace(',', '.'))
                datos_resumen["participacion_porcentaje"] = float(datos_js['valores'][3].replace(' ', '').replace(',', '.'))
                datos_resumen["provincia"] = datos_js['provincia']
        
        # Imprimir resultados
        print("\nDatos de resumen para la provincia/departamento:", nombre_provincia)
        print(f"Superficie (ha): {datos_resumen['superficie_ha']}")
        print(f"Rendimiento (t/ha): {datos_resumen['rendimiento_tha']}")
        print(f"Producción (tm): {datos_resumen['produccion_tm']}")
        print(f"Participación (%): {datos_resumen['participacion_porcentaje']}")
        
        return datos_resumen
        
    except Exception as e:
        print(f"Error al extraer datos de resumen: {str(e)}")
        return None