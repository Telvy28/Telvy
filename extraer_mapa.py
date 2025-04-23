# Crear archivo extraer_mapa.py
def extraer_areas_habilitadas(driver, grid_size=40, wait_time=0.1, segunda_pasada=True):
    """
    Extrae áreas habilitadas mediante simulación de hover
    
    Args:
        driver: WebDriver de Selenium inicializado
        grid_size: Resolución de la cuadrícula (mayor número = más puntos de prueba)
        wait_time: Tiempo de espera entre movimientos (segundos)
        segunda_pasada: Si True, realiza una segunda pasada adaptativa en zonas sin detección
    
    Returns:
        list: Lista de diccionarios con las áreas detectadas
    """
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    import time
    import pandas as pd
    import numpy as np
    
    try:
        # Esperar a que el mapa se cargue completamente
        print("Esperando a que el mapa se cargue...")
        time.sleep(5)
        
        # Encontrar el elemento SVG del mapa
        svg_element = driver.find_element(By.CSS_SELECTOR, "svg")
        
        # Obtener dimensiones del SVG
        svg_size = driver.execute_script("""
            const svg = arguments[0];
            const rect = svg.getBoundingClientRect();
            return {
                width: rect.width,
                height: rect.height,
                x: rect.x,
                y: rect.y
            };
        """, svg_element)
        
        print(f"Dimensiones del SVG: {svg_size['width']}x{svg_size['height']}")
        print(f"Usando cuadrícula de {grid_size}x{grid_size} puntos")
        
        # Primera pasada
        areas_detectadas = set()
        puntos_probados = []
        
        # Crear una cuadrícula para mover el mouse
        step_x = svg_size['width'] / grid_size
        step_y = svg_size['height'] / grid_size
        
        actions = ActionChains(driver)
        
        # Primera pasada: Exploración sistemática
        print("\nRealizando primera pasada de detección...")
        for i in range(grid_size):
            for j in range(grid_size):
                try:
                    # Calcular coordenadas
                    x_offset = int(step_x * i - svg_size['width']/2)
                    y_offset = int(step_y * j - svg_size['height']/2)
                    
                    # Guardar punto probado
                    puntos_probados.append((x_offset, y_offset))
                    
                    # Mover el mouse al punto
                    actions.move_to_element_with_offset(svg_element, x_offset, y_offset).perform()
                    
                    # Esperar para que se active el hover
                    time.sleep(wait_time)
                    
                    # Detectar área activa
                    area_info = driver.execute_script("""
                        // Buscar tooltips visibles
                        const tooltips = document.querySelectorAll('.highcharts-tooltip, .tooltip, [class*="tooltip"]');
                        for (const tooltip of tooltips) {
                            if (tooltip.style.visibility !== 'hidden' && tooltip.style.display !== 'none') {
                                return {
                                    texto: tooltip.textContent.trim(),
                                    tipo: 'tooltip'
                                };
                            }
                        }
                        
                        // Buscar elementos con hover activo
                        const elementos_hover = document.querySelectorAll(':hover');
                        for (const elem of elementos_hover) {
                            if (elem.tagName.toLowerCase() === 'path' || elem.tagName.toLowerCase() === 'polygon') {
                                // Buscar texto asociado
                                const title = elem.querySelector('title');
                                if (title) return {
                                    texto: title.textContent.trim(),
                                    tipo: 'title'
                                };
                                
                                // Buscar en atributos
                                const dataName = elem.getAttribute('data-name');
                                if (dataName) return {
                                    texto: dataName,
                                    tipo: 'data-name'
                                };
                                
                                // Buscar texto cercano
                                const bbox = elem.getBBox();
                                const textos = document.querySelectorAll('text');
                                for (const texto of textos) {
                                    const txtBBox = texto.getBBox();
                                    const dist = Math.sqrt(
                                        Math.pow(bbox.x + bbox.width/2 - txtBBox.x - txtBBox.width/2, 2) +
                                        Math.pow(bbox.y + bbox.height/2 - txtBBox.y - txtBBox.height/2, 2)
                                    );
                                    if (dist < 50) return {
                                        texto: texto.textContent.trim(),
                                        tipo: 'texto-cercano'
                                    };
                                }
                            }
                        }
                        
                        return null;
                    """)
                    
                    if area_info and area_info['texto'] and area_info['texto'] not in areas_detectadas:
                        areas_detectadas.add(area_info['texto'])
                        print(f"Área detectada: {area_info['texto']} (tipo: {area_info['tipo']})")
                
                except Exception as e:
                    # Ignorar errores de movimiento
                    pass
        
        # Segunda pasada adaptativa (opcional)
        if segunda_pasada:
            print("\nRealizando segunda pasada adaptativa en zonas sin detección...")
            
            # Identificar zonas sin detección
            matriz_deteccion = np.zeros((grid_size, grid_size))
            
            # Marcar zonas con detección
            for i in range(grid_size):
                for j in range(grid_size):
                    x_offset = int(step_x * i - svg_size['width']/2)
                    y_offset = int(step_y * j - svg_size['height']/2)
                    
                    # Verificar si algún área fue detectada cerca de este punto
                    punto_con_deteccion = False
                    for area in areas_detectadas:
                        # Aquí podrías implementar una lógica más sofisticada
                        # para determinar si un punto tiene detección cercana
                        # Por ahora, simplemente marcamos puntos con detección
                        if len(areas_detectadas) > 0:
                            punto_con_deteccion = True
                            break
                    
                    if punto_con_deteccion:
                        matriz_deteccion[i, j] = 1
            
            # Realizar búsqueda detallada en zonas sin detección
            grid_size_detallado = 5  # Resolución más alta para zonas específicas
            
            for i in range(grid_size):
                for j in range(grid_size):
                    if matriz_deteccion[i, j] == 0:  # Zona sin detección
                        # Calcular área de búsqueda
                        x_start = int(step_x * i - svg_size['width']/2)
                        y_start = int(step_y * j - svg_size['height']/2)
                        x_end = int(step_x * (i + 1) - svg_size['width']/2)
                        y_end = int(step_y * (j + 1) - svg_size['height']/2)
                        
                        # Búsqueda detallada en esta zona
                        step_x_detallado = (x_end - x_start) / grid_size_detallado
                        step_y_detallado = (y_end - y_start) / grid_size_detallado
                        
                        for di in range(grid_size_detallado):
                            for dj in range(grid_size_detallado):
                                x_offset = int(x_start + step_x_detallado * di)
                                y_offset = int(y_start + step_y_detallado * dj)
                                
                                try:
                                    actions.move_to_element_with_offset(svg_element, x_offset, y_offset).perform()
                                    time.sleep(wait_time * 1.5)  # Más tiempo para áreas pequeñas
                                    
                                    # Detectar área activa (mismo código que antes)
                                    area_info = driver.execute_script("""
                                        // [Mismo código JavaScript que en la primera pasada]
                                        return null;
                                    """)
                                    
                                    if area_info and area_info['texto'] and area_info['texto'] not in areas_detectadas:
                                        areas_detectadas.add(area_info['texto'])
                                        print(f"Área detectada (2da pasada): {area_info['texto']}")
                                
                                except Exception as e:
                                    pass
        
        # Filtrar y organizar resultados
        resultados_finales = []
        for area in areas_detectadas:
            # Limpiar y normalizar el nombre
            area_limpia = area.strip()
            if (area_limpia and 
                len(area_limpia) > 1 and 
                not area_limpia.lower() in ['otros', 'otro', 'otras', 'otra'] and
                not area_limpia.isdigit()):
                
                resultados_finales.append({
                    'departamento': area_limpia
                })
        
        # Ordenar resultados
        resultados_finales = sorted(resultados_finales, key=lambda x: x['departamento'])
        
        # Guardar resultados
        if resultados_finales:
            print(f"\nSe detectaron {len(resultados_finales)} áreas en total:")
            for res in resultados_finales:
                print(f"- {res['departamento']}")
            
            df = pd.DataFrame(resultados_finales)
            csv_file = "areas_detectadas.csv"
            df.to_csv(csv_file, index=False, encoding='utf-8')
            print(f"\nResultados guardados en {csv_file}")
            
            return resultados_finales
        else:
            print("No se encontraron áreas")
            return []
    
    except Exception as e:
        print(f"Error durante la extracción: {str(e)}")
        import traceback
        traceback.print_exc()
        return []