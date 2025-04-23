def extraer_datos_grafico_calendario(driver, titulo_grafico=None):
    """
    Extrae datos de un gráfico de calendario de cosechas del SIEA.
    
    Args:
        driver: WebDriver de Selenium inicializado
        titulo_grafico: Título del gráfico para verificación (opcional)
    
    Returns:
        dict: Diccionario con información del departamento y datos mensuales
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    import time
    import re
    
    # Lista de meses del año
    meses = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Set', 'Oct', 'Nov', 'Dic']
    
    try:
        # Esperar a que cargue el gráfico
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".highcharts-column-series .highcharts-point"))
        )
        
        # Obtener el título del gráfico
        titulo_elemento = driver.find_element(By.CSS_SELECTOR, ".highcharts-title")
        titulo_actual = titulo_elemento.text
        
        # Extraer departamento del título
        departamento = titulo_actual.split(':')[0].replace('Departamento de', '').strip()
        
        # Buscar las barras del gráfico
        barras = driver.find_elements(By.CSS_SELECTOR, ".highcharts-column-series .highcharts-point")
        
        # Obtener etiquetas del eje X
        etiquetas_x = driver.find_elements(By.CSS_SELECTOR, ".highcharts-xaxis-labels text")
        
        # Mapear las etiquetas con sus posiciones
        meses_posiciones = {}
        for etiqueta in etiquetas_x:
            texto = etiqueta.text
            if texto in meses:
                pos_x = etiqueta.rect['x']
                meses_posiciones[texto] = pos_x
        
        # Crear diccionario para almacenar datos por mes
        datos_por_mes = {mes: {"porcentaje": None, "tm": None} for mes in meses}
        
        # Crear ActionChains para mover el mouse
        action = ActionChains(driver)
        
        # Analizar cada barra y asociarla con el mes correcto
        for barra in barras:
            try:
                # Obtener la posición X central de la barra
                pos_x_barra = barra.rect['x'] + (barra.rect['width'] / 2)
                altura = float(barra.get_attribute("height") or 0)
                
                # Encontrar el mes más cercano a esta posición X
                mes_cercano = None
                menor_distancia = float('inf')
                
                for mes, pos_x in meses_posiciones.items():
                    distancia = abs(pos_x - pos_x_barra)
                    if distancia < menor_distancia:
                        menor_distancia = distancia
                        mes_cercano = mes
                
                # Solo procesar si la barra tiene altura (es visible)
                if altura > 0 and mes_cercano:
                    # Mover el cursor a la barra para mostrar el tooltip
                    action.move_to_element(barra).perform()
                    time.sleep(0.5)  # Esperar a que aparezca el tooltip
                    
                    # Intentar obtener el texto del tooltip
                    tooltip_elementos = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip text, .highcharts-tooltip-box + text")
                    
                    tooltip_texto = ""
                    for elem in tooltip_elementos:
                        texto = elem.text
                        if texto and ("%" in texto or "tm:" in texto.lower()):
                            tooltip_texto = texto
                            break
                    
                    # Si no se encontró con selectores específicos, usar JavaScript
                    if not tooltip_texto:
                        tooltip_texto = driver.execute_script("""
                            const textos = Array.from(document.querySelectorAll('.highcharts-tooltip text tspan'));
                            return textos.map(t => t.textContent).join('\\n');
                        """)
                    
                    # Extraer porcentaje y tm del tooltip
                    porcentaje = None
                    tm = None
                    
                    # Patrones para extraer porcentaje y tm
                    porcentaje_match = re.search(r'([\d\s.,]+)\s*%', tooltip_texto)
                    tm_match = re.search(r'tm:\s*([\d\s.,]+)', tooltip_texto)
                    
                    if porcentaje_match:
                        porcentaje = float(porcentaje_match.group(1).replace(' ', '').replace(',', '.'))
                    
                    if tm_match:
                        tm = float(tm_match.group(1).replace(' ', '').replace(',', '.'))
                    
                    # Guardar datos para este mes
                    datos_por_mes[mes_cercano] = {
                        "porcentaje": porcentaje,
                        "tm": tm,
                        "altura": altura,
                        "tooltip": tooltip_texto
                    }
                    
                    # Imprimir lo que se encontró para cada mes (opcional)
                    print(f"Mes {mes_cercano}: Porcentaje={porcentaje}%, TM={tm}")
                    
            except Exception as e:
                # Error silencioso
                pass
        
        # Convertir el diccionario a una lista ordenada por los meses
        datos_mensuales = []
        for mes in meses:
            if mes in datos_por_mes:
                datos = datos_por_mes[mes]
                if datos.get("porcentaje") is not None or datos.get("tm") is not None:
                    datos_mensuales.append({
                        "mes": mes,
                        "porcentaje": datos.get("porcentaje"),
                        "tm": datos.get("tm")
                    })
        
        # Imprimir los datos extraídos
        print(f"\nDatos extraídos para {departamento} - Maiz Amarillo Duro:")
        print("Mes | Porcentaje | Toneladas Métricas")
        print("----|------------|------------------")
        for dato in datos_mensuales:
            porcentaje_str = f"{dato['porcentaje']}%" if dato['porcentaje'] is not None else "N/A"
            tm_str = f"{dato['tm']}" if dato['tm'] is not None else "N/A"
            print(f"{dato['mes']} | {porcentaje_str} | {tm_str}")
        
        # Devolver los resultados en un formato estructurado
        return {
            "departamento": departamento,
            "cultivo": "Maiz Amarillo Duro",  # Se podría parametrizar más adelante
            "datos_mensuales": datos_mensuales
        }
        
    except Exception as e:
        print(f"Error al extraer datos del gráfico: {str(e)}")
        return None