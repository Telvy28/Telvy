# zone_a_utils.py
"""
Utilidades para trabajar con una zona específica de la pantalla (Zona A).
Este módulo define las coordenadas de la zona y proporciona funciones
para determinar si un elemento web se encuentra dentro de ella.
"""

from selenium.webdriver.remote.webelement import WebElement

# Definir las coordenadas de la zona A
# Estas coordenadas pueden ajustarse según sea necesario para diferentes páginas
ZONE_A = {
    'x_min': 102,  # Coordenada X mínima (borde izquierdo)
    'y_min': 182,  # Coordenada Y mínima (borde superior)
    'x_max': 651,  # Coordenada X máxima (borde derecho)
    'y_max': 839   # Coordenada Y máxima (borde inferior)
}

def is_element_in_zone_a(element):
    """
    Verifica si un elemento web se encuentra dentro de la zona A definida.
    
    Args:
        element (WebElement): Elemento web de Selenium
        
    Returns:
        bool: True si el elemento está en la zona A, False en caso contrario
    """
    try:
        # Obtener la ubicación y dimensiones del elemento
        location = element.location
        size = element.size
        
        # Calcular el centro del elemento
        center_x = location['x'] + size['width'] / 2
        center_y = location['y'] + size['height'] / 2
        
        # Verificar si el centro está dentro de la zona A
        if (ZONE_A['x_min'] <= center_x <= ZONE_A['x_max'] and 
            ZONE_A['y_min'] <= center_y <= ZONE_A['y_max']):
            return True
        return False
    except Exception:
        # Si hay algún error, asumir que no está en la zona
        return False

def filter_elements_in_zone_a(elements):
    """
    Filtra una lista de elementos y devuelve solo aquellos que están en la zona A.
    
    Args:
        elements (list): Lista de elementos web de Selenium
        
    Returns:
        list: Lista filtrada de elementos dentro de la zona A
    """
    return [elem for elem in elements if is_element_in_zone_a(elem)]

def set_zone_coordinates(x_min, y_min, x_max, y_max):
    """
    Actualiza las coordenadas de la zona A.
    Útil para cambiar la zona dinámicamente sin modificar el código.
    
    Args:
        x_min (int): Coordenada X mínima
        y_min (int): Coordenada Y mínima
        x_max (int): Coordenada X máxima
        y_max (int): Coordenada Y máxima
    """
    global ZONE_A
    ZONE_A = {
        'x_min': x_min,
        'y_min': y_min,
        'x_max': x_max,
        'y_max': y_max
    }
    return ZONE_A