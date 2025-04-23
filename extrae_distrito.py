def extraer_datos_distrito_mapa(driver, nombre_distrito):
    """
    Mueve el cursor al distrito especificado en el mapa y extrae sus datos.
    
    Args:
        driver: WebDriver de Selenium inicializado
        nombre_distrito: Nombre del distrito a buscar
    
    Returns:
        dict: Diccionario con la información del distrito
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import time
    
    try:
        # Inicializar el diccionario de resultados
        datos_distrito = {
            "nombre": nombre_distrito,
            "superficie_ha": None,
            "rendimiento_tha": None,
            "produccion_tm": None,
            "participacion_porcentaje": None
        }
        
        # Esperar a que el mapa se cargue
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "path.highcharts-point"))
        )
        
        # Configuración inicial
        time.sleep(2)
        action = ActionChains(driver)
        elementos_mapa = driver.find_elements(By.CSS_SELECTOR, "path.highcharts-point")
        
        print(f"Encontrados {len(elementos_mapa)} elementos en el mapa")
        distrito_encontrado = False
        
        # Buscar el distrito en los elementos del mapa
        for elemento in elementos_mapa:
            try:
                # Mover el cursor al elemento
                action.move_to_element(elemento).perform()
                time.sleep(0.7)
                
                # Verificar si el tooltip contiene el nombre del distrito
                tooltips = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip")
                for tooltip in tooltips:
                    tooltip_text = tooltip.text.strip()
                    print(f"Tooltip encontrado: {tooltip_text}")
                    
                    if nombre_distrito.lower() in tooltip_text.lower():
                        print(f"¡Distrito encontrado en tooltip!: {tooltip_text}")
                        distrito_encontrado = True
                        
                        # Intentar hacer clic usando diferentes métodos
                        try:
                            # Método 1: Clic directo
                            elemento.click()
                            print("Clic directo exitoso")
                        except Exception as e1:
                            print(f"Error en clic directo: {e1}")
                            try:
                                # Método 2: Clic con ActionChains
                                action.click(elemento).perform()
                                print("Clic con ActionChains exitoso")
                            except Exception as e2:
                                print(f"Error en clic con ActionChains: {e2}")
                                try:
                                    # Método 3: Clic con JavaScript y MouseEvent
                                    driver.execute_script("""
                                        arguments[0].dispatchEvent(new MouseEvent('click', {
                                            bubbles: true,
                                            cancelable: true,
                                            view: window
                                        }));
                                    """, elemento)
                                    print("Clic con MouseEvent exitoso")
                                except Exception as e3:
                                    print(f"Error en clic con MouseEvent: {e3}")
                        
                        # Dar tiempo para que la página se actualice
                        time.sleep(1.5)
                        break
                
                # Si se encontró el distrito, salir del bucle
                if distrito_encontrado:
                    break
                    
            except Exception as e:
                print(f"Error al procesar elemento: {e}")
                continue
        
        # Si no se encontró por tooltips, intentar otros métodos
        if not distrito_encontrado:
            print(f"No se encontró el distrito '{nombre_distrito}' en los tooltips del mapa")
            
            # Buscar por etiquetas de texto visibles
            etiquetas = driver.find_elements(By.CSS_SELECTOR, "text.highcharts-text-outline, .highcharts-label text")
            
            for etiqueta in etiquetas:
                try:
                    etiqueta_text = etiqueta.text.strip()
                    if nombre_distrito.lower() in etiqueta_text.lower():
                        print(f"Etiqueta encontrada: {etiqueta_text}")
                        
                        # Intentar hacer clic en la etiqueta
                        try:
                            etiqueta.click()
                            distrito_encontrado = True
                            print("Clic en etiqueta exitoso")
                            time.sleep(1.5)
                            break
                        except Exception as e:
                            print(f"Error al hacer clic en etiqueta: {e}")
                            # Intentar con JavaScript
                            try:
                                driver.execute_script("arguments[0].click();", etiqueta)
                                distrito_encontrado = True
                                print("Clic en etiqueta con JavaScript exitoso")
                                time.sleep(1.5)
                                break
                            except Exception as e2:
                                print(f"Error al hacer clic con JavaScript: {e2}")
                except Exception as e:
                    continue
        
        # Si aún no se encuentra, probar con elementos coloreados
        if not distrito_encontrado:
            print("Buscando elementos coloreados o destacados en el mapa...")
            elementos_destacados = driver.find_elements(By.CSS_SELECTOR, 
                                                      "path.highcharts-point[fill='#FFFF00'], "
                                                      "path.highcharts-point[stroke-width='2']")
            
            print(f"Encontrados {len(elementos_destacados)} elementos destacados")
            
            for elemento in elementos_destacados:
                try:
                    action.move_to_element(elemento).perform()
                    time.sleep(0.7)
                    
                    # Verificar si hay algún tooltip o texto relacionado con el distrito
                    tooltips = driver.find_elements(By.CSS_SELECTOR, ".highcharts-tooltip")
                    for tooltip in tooltips:
                        tooltip_text = tooltip.text.strip()
                        print(f"Tooltip en elemento destacado: {tooltip_text}")
                        
                        if nombre_distrito.lower() in tooltip_text.lower():
                            print(f"Distrito encontrado en elemento destacado")
                            
                            # Intentar hacer clic
                            try:
                                elemento.click()
                                distrito_encontrado = True
                                print("Clic en elemento destacado exitoso")
                            except Exception as e:
                                try:
                                    action.click(elemento).perform()
                                    distrito_encontrado = True
                                    print("Clic con ActionChains exitoso")
                                except Exception as e2:
                                    try:
                                        driver.execute_script("arguments[0].dispatchEvent(new MouseEvent('click', {bubbles: true}));", elemento)
                                        distrito_encontrado = True
                                        print("Clic con MouseEvent exitoso")
                                    except Exception as e3:
                                        print("No se pudo hacer clic en el elemento destacado")
                            
                            time.sleep(1.5)
                            break
                    
                    if distrito_encontrado:
                        break
                except Exception as e:
                    print(f"Error al procesar elemento destacado: {e}")
                    continue
        
        # Extraer datos del distrito
        # Método directo: buscar los valores en el DOM
        print("Intentando método directo de extracción...")
        
        # Buscar título que contenga el nombre del distrito
        textos_titulo = driver.find_elements(By.CSS_SELECTOR, ".titulo_celda_resumen")
        distrito_indice = -1
        
        for i, texto in enumerate(textos_titulo):
            if "DIST.:" in texto.text and nombre_distrito.lower() in texto.text.lower():
                print(f"Título encontrado: {texto.text}")
                distrito_indice = i
                break
        
        if distrito_indice >= 0:
            # Buscar valores correspondientes
            valores = driver.find_elements(By.CSS_SELECTOR, ".valor_celda_resumen")
            
            # Calcular índices para los valores del distrito
            indice_inicio = distrito_indice * 4
            
            if len(valores) >= indice_inicio + 4:
                try:
                    superficie_text = valores[indice_inicio].text.strip()
                    rendimiento_text = valores[indice_inicio + 1].text.strip()
                    produccion_text = valores[indice_inicio + 2].text.strip()
                    participacion_text = valores[indice_inicio + 3].text.strip()
                    
                    print(f"Valores encontrados: {superficie_text}, {rendimiento_text}, {produccion_text}, {participacion_text}")
                    
                    # Convertir a float, eliminando espacios y reemplazando comas por puntos
                    if superficie_text:
                        datos_distrito["superficie_ha"] = float(superficie_text.replace(' ', '').replace(',', '.'))
                    if rendimiento_text:
                        datos_distrito["rendimiento_tha"] = float(rendimiento_text.replace(' ', '').replace(',', '.'))
                    if produccion_text:
                        datos_distrito["produccion_tm"] = float(produccion_text.replace(' ', '').replace(',', '.'))
                    if participacion_text:
                        datos_distrito["participacion_porcentaje"] = float(participacion_text.replace(' ', '').replace(',', '.'))
                except ValueError as e:
                    print(f"Error al convertir valores: {e}")
                except Exception as e:
                    print(f"Error al procesar valores: {e}")
        
        # Método JavaScript si el método directo falló
        if all(v is None for k, v in datos_distrito.items() if k != "nombre"):
            print("Intentando extracción con JavaScript...")
            
            try:
                datos_js = driver.execute_script("""
                    // Intentar encontrar el título del distrito
                    const titulos = Array.from(document.querySelectorAll(".titulo_celda_resumen"));
                    const distritoTitulo = titulos.find(t => t.textContent.includes("DIST.:"));
                    
                    if (!distritoTitulo) return null;
                    
                    // Buscar los valores
                    const valores = Array.from(document.querySelectorAll(".valor_celda_resumen"));
                    
                    // Encontrar el índice del distrito
                    const indiceDistrito = titulos.indexOf(distritoTitulo);
                    
                    // Si no encontramos índice, usar los últimos 4 valores
                    if (indiceDistrito === -1 && valores.length >= 4) {
                        return {
                            superficie_ha: valores[valores.length-4].textContent.trim(),
                            rendimiento_tha: valores[valores.length-3].textContent.trim(),
                            produccion_tm: valores[valores.length-2].textContent.trim(),
                            participacion_porcentaje: valores[valores.length-1].textContent.trim()
                        };
                    }
                    
                    // Si encontramos índice, calcular inicio
                    const indiceInicio = indiceDistrito * 4;
                    
                    if (valores.length >= indiceInicio + 4) {
                        return {
                            superficie_ha: valores[indiceInicio].textContent.trim(),
                            rendimiento_tha: valores[indiceInicio+1].textContent.trim(),
                            produccion_tm: valores[indiceInicio+2].textContent.trim(),
                            participacion_porcentaje: valores[indiceInicio+3].textContent.trim()
                        };
                    }
                    
                    return null;
                """)
                
                if datos_js:
                    print("Datos extraídos con JavaScript:", datos_js)
                    
                    try:
                        if datos_js.get("superficie_ha"):
                            datos_distrito["superficie_ha"] = float(datos_js["superficie_ha"].replace(' ', '').replace(',', '.'))
                        if datos_js.get("rendimiento_tha"):
                            datos_distrito["rendimiento_tha"] = float(datos_js["rendimiento_tha"].replace(' ', '').replace(',', '.'))
                        if datos_js.get("produccion_tm"):
                            datos_distrito["produccion_tm"] = float(datos_js["produccion_tm"].replace(' ', '').replace(',', '.'))
                        if datos_js.get("participacion_porcentaje"):
                            datos_distrito["participacion_porcentaje"] = float(datos_js["participacion_porcentaje"].replace(' ', '').replace(',', '.'))
                    except Exception as e:
                        print(f"Error al convertir valores JS: {e}")
            except Exception as js_error:
                print(f"Error al ejecutar JavaScript: {js_error}")
        
        # Método de análisis de HTML si los anteriores fallaron
        if all(v is None for k, v in datos_distrito.items() if k != "nombre"):
            print("Intentando método de análisis de HTML...")
            
            try:
                # Tomar captura para referencia
                screenshot_path = f"distrito_{nombre_distrito.replace(' ', '_')}.png"
                driver.save_screenshot(screenshot_path)
                
                # Analizar el HTML
                html = driver.page_source
                import re
                
                # Buscar patrones específicos en el HTML
                all_numbers = re.findall(r'valor_celda_resumen[^>]*>([\d\s.,]+)<', html)
                print(f"Números encontrados en HTML: {all_numbers}")
                
                if len(all_numbers) >= 8:  # Asumiendo 4 para provincia y 4 para distrito
                    # Usar los últimos 4 números
                    try:
                        datos_distrito["superficie_ha"] = float(all_numbers[-8].replace(' ', '').replace(',', '.'))
                        datos_distrito["rendimiento_tha"] = float(all_numbers[-7].replace(' ', '').replace(',', '.'))
                        datos_distrito["produccion_tm"] = float(all_numbers[-6].replace(' ', '').replace(',', '.'))
                        datos_distrito["participacion_porcentaje"] = float(all_numbers[-5].replace(' ', '').replace(',', '.'))
                    except ValueError:
                        # Si no funciona, probar con los últimos 4
                        try:
                            datos_distrito["superficie_ha"] = float(all_numbers[-4].replace(' ', '').replace(',', '.'))
                            datos_distrito["rendimiento_tha"] = float(all_numbers[-3].replace(' ', '').replace(',', '.'))
                            datos_distrito["produccion_tm"] = float(all_numbers[-2].replace(' ', '').replace(',', '.'))
                            datos_distrito["participacion_porcentaje"] = float(all_numbers[-1].replace(' ', '').replace(',', '.'))
                        except Exception as e:
                            print(f"Error al convertir últimos valores: {e}")
            except Exception as html_error:
                print(f"Error al analizar HTML: {html_error}")
        
        return datos_distrito
        
    except Exception as e:
        print(f"Error general al extraer datos del distrito {nombre_distrito}: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            "nombre": nombre_distrito,
            "superficie_ha": None,
            "rendimiento_tha": None,
            "produccion_tm": None,
            "participacion_porcentaje": None
        }
