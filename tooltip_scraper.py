# tooltip_scraper.py
"""
Librería para extraer tooltips de mapas web usando Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import matplotlib.pyplot as plt
import numpy as np
from PIL import ImageGrab
import cv2
import csv

def visualizar_puntos_mapa(x_min, y_min, x_max, y_max, filas, columnas):
    """
    Visualiza los puntos donde se posicionará el cursor en el mapa
    """
    # Tomar screenshot de la pantalla
    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # Dibujar rectángulo del área de trabajo
    cv2.rectangle(screenshot, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
    
    # Calcular tamaño de cada celda
    ancho_celda = (x_max - x_min) / columnas
    alto_celda = (y_max - y_min) / filas
    
    # Dibujar puntos en cada intersección
    puntos = []
    for fila in range(filas + 1):
        for columna in range(columnas + 1):
            x = int(x_min + columna * ancho_celda)
            y = int(y_min + fila * alto_celda)
            cv2.circle(screenshot, (x, y), 5, (0, 0, 255), -1)
            puntos.append((x, y))
    
    # Mostrar imagen con matplotlib
    plt.figure(figsize=(12, 8))
    plt.imshow(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
    plt.title('Puntos de intersección en el mapa')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('mapa_puntos.png')
    plt.show()
    
    return puntos

def simular_hover(driver, x, y):
    """Función para simular hover en una posición específica"""
    driver.execute_script(f"""
        var elemento = document.elementFromPoint({x}, {y});
        if (elemento) {{
            ['mousemove', 'mouseover', 'mouseenter'].forEach(function(eventType) {{
                var evento = new MouseEvent(eventType, {{
                    view: window, bubbles: true, cancelable: true,
                    clientX: {x}, clientY: {y}
                }});
                elemento.dispatchEvent(evento);
            }});
        }}
    """)

def generar_mapa_resultados(x_min, y_min, x_max, y_max, filas, columnas, mapa_resultados, puntos_visitados):
    """
    Genera una visualización de los resultados obtenidos
    
    Args:
        puntos_visitados: conjunto de tuplas (fila, columna) que indica puntos donde se posicionó el cursor
    """
    # Tomar screenshot para usar como fondo
    screenshot = ImageGrab.grab()
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    
    # Crear una imagen más grande para incluir las etiquetas
    altura, anchura = screenshot.shape[:2]
    imagen_resultado = np.zeros((altura + 200, anchura, 3), dtype=np.uint8)
    imagen_resultado[:altura, :] = screenshot
    imagen_resultado[altura:, :] = (255, 255, 255)  # Fondo blanco para las etiquetas
    
    # Dibujar rectángulo del área de trabajo
    cv2.rectangle(imagen_resultado, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
    
    # Calcular tamaño de cada celda
    ancho_celda = (x_max - x_min) / columnas
    alto_celda = (y_max - y_min) / filas
    
    # Dibujar puntos y etiquetas
    for fila in range(filas + 1):
        for columna in range(columnas + 1):
            x = int(x_min + columna * ancho_celda)
            y = int(y_min + fila * alto_celda)
            
            # Obtener el tooltip para esta posición
            tooltip = mapa_resultados.get((fila, columna))
            
            # Verificar si el punto fue visitado (cursor pasó por ahí)
            punto_visitado = (fila, columna) in puntos_visitados
            
            # Color del punto según si se encontró un tooltip y si fue visitado
            if tooltip:
                # Verde si se encontró tooltip
                cv2.circle(imagen_resultado, (x, y), 5, (0, 255, 0), -1)
                
                # Añadir etiqueta pequeña sobre el punto
                texto_corto = tooltip[:10] + "..." if len(tooltip) > 10 else tooltip
                cv2.putText(
                    imagen_resultado,
                    texto_corto,
                    (x + 5, y - 5),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (0, 0, 0),
                    1
                )
            elif punto_visitado:
                # Amarillo si fue visitado pero no se encontró tooltip
                cv2.circle(imagen_resultado, (x, y), 5, (0, 255, 255), -1)
            else:
                # Rojo si no fue visitado
                cv2.circle(imagen_resultado, (x, y), 5, (0, 0, 255), -1)
            
            # Añadir etiqueta detallada en la parte inferior
            if tooltip:
                y_pos = altura + 20 + ((fila * (columnas + 1) + columna) % 10) * 18
                x_pos = 10 + ((fila * (columnas + 1) + columna) // 10) * 250
                cv2.putText(
                    imagen_resultado, 
                    f"({columna},{fila}): {tooltip[:30]}", 
                    (x_pos, y_pos), 
                    cv2.FONT_HERSHEY_SIMPLEX, 
                    0.5, 
                    (0, 0, 0), 
                    1
                )
    
    # Guardar imagen
    cv2.imwrite('resultados_mapa.png', imagen_resultado)
    
    # Mostrar con matplotlib
    plt.figure(figsize=(12, 10))
    plt.imshow(cv2.cvtColor(imagen_resultado, cv2.COLOR_BGR2RGB))
    plt.title('Resultados del mapeo de tooltips')
    plt.axis('off')
    plt.tight_layout()
    plt.savefig('resultados_mapa_plt.png')
    plt.show()
    
    return imagen_resultado

def scrape_tooltips_mapa(driver, x_min, y_min, x_max, y_max, filas=20, columnas=20, 
                         mostrar_visualizacion=True, tiempo_espera=1.0):
    """
    Función para extraer nombres de elementos desde tooltips en mapas web.
    
    Args:
        driver: WebDriver de Selenium inicializado
        x_min: Coordenada X mínima del área a analizar
        y_min: Coordenada Y mínima del área a analizar
        x_max: Coordenada X máxima del área a analizar
        y_max: Coordenada Y máxima del área a analizar
        filas: Número de filas de la cuadrícula (default: 20)
        columnas: Número de columnas de la cuadrícula (default: 20)
        mostrar_visualizacion: Si es True, muestra visualizaciones (default: True)
        tiempo_espera: Tiempo en segundos para esperar a que aparezca el tooltip (default: 1.0)
        
    Returns:
        tuple: (set de tooltips únicos, diccionario con posiciones y tooltips)
    """
    # Conjunto para almacenar tooltips encontrados (elimina duplicados automáticamente)
    tooltips_encontrados = set()
    
    # Mapeo para guardar qué tooltip se encontró en cada posición
    mapa_resultados = {}
    
    # Conjunto para registrar qué puntos fueron visitados por el cursor
    puntos_visitados = set()
    
    # Visualizar puntos si se solicita
    if mostrar_visualizacion:
        visualizar_puntos_mapa(x_min, y_min, x_max, y_max, filas, columnas)
    
    # Calcular tamaño de cada celda
    ancho_celda = (x_max - x_min) / columnas
    alto_celda = (y_max - y_min) / filas
    
    # Generar lista de puntos
    puntos = []
    for fila in range(filas + 1):
        for columna in range(columnas + 1):
            x = int(x_min + columna * ancho_celda)
            y = int(y_min + fila * alto_celda)
            puntos.append((x, y, fila, columna))
    
    # Variable para llevar un seguimiento del tooltip anterior
    ultimo_tooltip = None
    
    print("Iniciando captura de tooltips...")
    
    # Lista de selectores comunes para tooltips
    tooltip_selectors = [
        ".highcharts-tooltip",  # Selector del código original
        "[role='tooltip']",     # Común en muchos mapas
        ".tooltip",             # Clase común
        ".mapTooltip",          # Otra clase común
        ".map-tooltip"          # Variante con guión
    ]
    
    # Para cada punto de la cuadrícula
    for x, y, fila, columna in puntos:
        try:
            # Marcar este punto como visitado
            puntos_visitados.add((fila, columna))
            
            # Simular hover en la posición actual
            simular_hover(driver, x, y)
            
            # Esperar a que aparezca el tooltip
            time.sleep(tiempo_espera)
            
            # Intentar obtener el tooltip con los diferentes selectores
            tooltip_text = None
            
            for selector in tooltip_selectors:
                try:
                    tooltip = WebDriverWait(driver, 0.5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    tooltip_text = tooltip.text.strip()
                    if tooltip_text:  # Si encontramos texto, salimos del bucle
                        break
                except Exception:
                    continue
            
            # Verificar si se encontró un tooltip válido
            if tooltip_text and tooltip_text != ultimo_tooltip:
                # Actualizar el tooltip más reciente
                ultimo_tooltip = tooltip_text
                
                # Limpieza básica del texto
                cleaned_text = tooltip_text.strip()
                
                # Guardar el tooltip y su posición
                mapa_resultados[(fila, columna)] = cleaned_text
                
                # Agregar al conjunto si es nuevo
                tooltips_encontrados.add(cleaned_text)
                
                print(f"Encontrado en ({fila},{columna}): {cleaned_text}")
            else:
                # No es un tooltip válido o es repetido, marcar como None
                mapa_resultados[(fila, columna)] = None
                        
        except Exception as e:
            print(f"Error al procesar punto ({fila},{columna}): {e}")
            # Error al procesar el punto, marcar como None
            mapa_resultados[(fila, columna)] = None
            # Resetear el último tooltip para evitar arrastrar valores
            ultimo_tooltip = None
    
    # Generar mapa visual de resultados
    if mostrar_visualizacion:
        generar_mapa_resultados(x_min, y_min, x_max, y_max, filas, columnas, mapa_resultados, puntos_visitados)
    
    # Imprimir resumen final
    print("\n===== RESUMEN FINAL =====")
    print(f"Total de tooltips encontrados: {len(tooltips_encontrados)}")
    
    print("\nLista de tooltips encontrados:")
    for i, tooltip in enumerate(sorted(tooltips_encontrados), 1):
        print(f"{i}. {tooltip}")
    
    # Guardar en un archivo CSV
    with open('tooltips_encontrados.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Número', 'Tooltip'])
        for i, tooltip in enumerate(sorted(tooltips_encontrados), 1):
            writer.writerow([i, tooltip])
    
    print("\nLos resultados han sido guardados en 'tooltips_encontrados.csv'")
    
    return tooltips_encontrados, mapa_resultados