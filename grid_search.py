# grid_search.py
"""
Sistema de búsqueda por cuadrícula para web scraping.
Este módulo implementa una estrategia de búsqueda sistemática que 
divide una zona definida en celdas y explora cada una de ellas.
"""

from selenium.webdriver.common.action_chains import ActionChains
import time

# Importar las coordenadas de zona_a_utils.py
from zone_a_utils import ZONE_A

class GridSearch:
    """
    Clase que implementa una búsqueda sistemática por cuadrícula en una zona definida.
    """
    
    def __init__(self, driver, grid_size=10, zone=None):
        """
        Inicializa el sistema de búsqueda por cuadrícula.
        
        Args:
            driver: WebDriver de Selenium
            grid_size (int): Número de divisiones en cada eje (grid_size x grid_size)
            zone (dict, opcional): Diccionario con las coordenadas de la zona.
                                  Si es None, usa ZONE_A de zone_a_utils.py
        """
        self.driver = driver
        self.action = ActionChains(driver)
        self.grid_size = grid_size
        
        # Usar la zona proporcionada o la zona A por defecto
        self.zone = zone or ZONE_A
        
        # Extraer coordenadas de la zona
        self.x_min = self.zone['x_min']
        self.x_max = self.zone['x_max']
        self.y_min = self.zone['y_min']
        self.y_max = self.zone['y_max']
        
        # Calcular el tamaño de cada celda
        self.cell_width = (self.x_max - self.x_min) / grid_size
        self.cell_height = (self.y_max - self.y_min) / grid_size
        
        # Para seguimiento de elementos encontrados
        self.found_items = set()
        
        # Para visualización (opcional)
        self.visualization_enabled = False
    
    def get_cell_center(self, row, col):
        """
        Obtiene las coordenadas del centro de una celda específica.
        
        Args:
            row (int): Fila de la celda (0 a grid_size-1)
            col (int): Columna de la celda (0 a grid_size-1)
            
        Returns:
            tuple: (coordenada_x, coordenada_y) del centro de la celda
        """
        # Calcular las coordenadas del centro de la celda
        center_x = self.x_min + (col + 0.5) * self.cell_width
        center_y = self.y_min + (row + 0.5) * self.cell_height
        
        return (center_x, center_y)
    
    def move_to_cell(self, row, col):
        """
        Mueve el cursor al centro de una celda específica.
        
        Args:
            row (int): Fila de la celda
            col (int): Columna de la celda
            
        Returns:
            bool: True si el movimiento fue exitoso, False en caso contrario
        """
        try:
            # Obtener coordenadas del centro de la celda
            center_x, center_y = self.get_cell_center(row, col)
            
            # Visualización opcional
            if self.visualization_enabled:
                self._highlight_cell(row, col)
            
            # Mover el cursor a esas coordenadas usando JavaScript
            script = f"""
                var evt = new MouseEvent('mousemove', {{
                    bubbles: true,
                    cancelable: true,
                    view: window,
                    clientX: {center_x},
                    clientY: {center_y}
                }});
                document.elementFromPoint({center_x}, {center_y}).dispatchEvent(evt);
            """
            self.driver.execute_script(script)
            
            return True
        except Exception as e:
            print(f"Error al mover a celda [{row},{col}]: {e}")
            return False
    
    def search_grid(self, tooltip_selector=".highcharts-tooltip", 
                  process_tooltip_func=None, expected_items=None, 
                  wait_time=0.3, verbose=True):
        """
        Busca elementos recorriendo toda la cuadrícula de manera sistemática.
        
        Args:
            tooltip_selector (str): Selector CSS del tooltip
            process_tooltip_func (callable, opcional): Función para procesar el tooltip.
                                                     Si es None, se usa una función básica.
            expected_items (set, opcional): Conjunto de elementos que se están buscando
            wait_time (float): Tiempo de espera en cada celda
            verbose (bool): Si es True, muestra información detallada
            
        Returns:
            set: Conjunto de elementos encontrados
        """
        if verbose:
            print(f"Iniciando búsqueda por cuadrícula {self.grid_size}x{self.grid_size}...")
            print(f"Zona: X({self.x_min}-{self.x_max}), Y({self.y_min}-{self.y_max})")
            print(f"Tamaño de celda: {self.cell_width:.1f}x{self.cell_height:.1f} píxeles")
            print("-" * 50)
        
        # Si no se proporciona una función de procesamiento, usar la básica
        if not process_tooltip_func:
            process_tooltip_func = self._default_process_tooltip
        
        start_time = time.time()
        
        # Iterar por cada celda de la cuadrícula
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # Si ya encontramos todos los elementos esperados, terminar
                if expected_items and self.found_items.issuperset(expected_items):
                    if verbose:
                        print(f"\n¡Se encontraron todos los {len(expected_items)} elementos buscados!")
                    break
                
                if verbose:
                    print(f"Explorando celda [{row},{col}]", end="")
                
                # Mover a la celda actual
                if self.move_to_cell(row, col):
                    # Esperar un momento para que aparezca el tooltip
                    time.sleep(wait_time)
                    
                    # Procesar tooltip
                    item = process_tooltip_func(tooltip_selector, expected_items)
                    
                    if verbose:
                        if item:
                            print(f" → {item}")
                        else:
                            print(" → Nada encontrado")
            
            # Si ya encontramos todos los elementos, terminar
            if expected_items and self.found_items.issuperset(expected_items):
                break
        
        # Mostrar tiempo total
        duration = time.time() - start_time
        if verbose:
            print(f"\nBúsqueda completa en {duration:.2f} segundos")
            print(f"Elementos encontrados: {len(self.found_items)}/{len(expected_items) if expected_items else 'desconocido'}")
        
        return self.found_items
    
    def _default_process_tooltip(self, tooltip_selector, expected_items=None):
        """
        Función básica para procesar tooltips.
        
        Args:
            tooltip_selector (str): Selector CSS del tooltip
            expected_items (set, opcional): Conjunto de elementos que se están buscando
            
        Returns:
            str: Texto del tooltip si se encontró, None en caso contrario
        """
        try:
            # Buscar tooltips visibles
            tooltips = self.driver.find_elements("css selector", tooltip_selector)
            
            for tooltip in tooltips:
                if tooltip.is_displayed():
                    tooltip_text = tooltip.text.strip()
                    
                    # Si encontramos texto en el tooltip
                    if tooltip_text:
                        # Si es un elemento nuevo que estamos buscando
                        is_expected = expected_items is None or tooltip_text in expected_items
                        is_new = tooltip_text not in self.found_items
                        
                        if is_expected and is_new:
                            self.found_items.add(tooltip_text)
                            return tooltip_text
            
            return None
        except Exception as e:
            print(f"Error al procesar tooltip: {e}")
            return None
    
    def enable_visualization(self, enable=True):
        """
        Activa o desactiva la visualización de la cuadrícula.
        
        Args:
            enable (bool): Si es True, activa la visualización
        """
        self.visualization_enabled = enable
        
        if enable:
            self._draw_grid()
        else:
            self._remove_visualizations()
    
    def _draw_grid(self):
        """Dibuja una cuadrícula visual sobre la zona definida"""
        grid_js = """
        // Eliminar cuadrícula anterior si existe
        const oldGrid = document.getElementById('scraper-grid');
        if (oldGrid) oldGrid.remove();
        
        // Crear nuevo contenedor para la cuadrícula
        const gridContainer = document.createElement('div');
        gridContainer.id = 'scraper-grid';
        gridContainer.style.position = 'absolute';
        gridContainer.style.top = '0';
        gridContainer.style.left = '0';
        gridContainer.style.width = '100%';
        gridContainer.style.height = '100%';
        gridContainer.style.pointerEvents = 'none';
        gridContainer.style.zIndex = '9999';
        
        // Crear líneas horizontales
        for (let i = 0; i <= %d; i++) {
            const y = %d + (i * %f);
            const line = document.createElement('div');
            line.style.position = 'absolute';
            line.style.left = '%dpx';
            line.style.top = y + 'px';
            line.style.width = '%dpx';
            line.style.height = '1px';
            line.style.backgroundColor = 'red';
            gridContainer.appendChild(line);
        }
        
        // Crear líneas verticales
        for (let i = 0; i <= %d; i++) {
            const x = %d + (i * %f);
            const line = document.createElement('div');
            line.style.position = 'absolute';
            line.style.left = x + 'px';
            line.style.top = '%dpx';
            line.style.width = '1px';
            line.style.height = '%dpx';
            line.style.backgroundColor = 'red';
            gridContainer.appendChild(line);
        }
        
        // Agregar números a las celdas
        for (let row = 0; row < %d; row++) {
            for (let col = 0; col < %d; col++) {
                const label = document.createElement('div');
                const x = %d + (col * %f) + 5;
                const y = %d + (row * %f) + 5;
                label.style.position = 'absolute';
                label.style.left = x + 'px';
                label.style.top = y + 'px';
                label.style.padding = '2px';
                label.style.backgroundColor = 'rgba(255, 255, 255, 0.7)';
                label.style.border = '1px solid red';
                label.style.fontSize = '10px';
                label.style.color = 'red';
                label.textContent = `${row},${col}`;
                gridContainer.appendChild(label);
            }
        }
        
        // Agregar al documento
        document.body.appendChild(gridContainer);
        
        return true;
        """ % (
            self.grid_size, self.y_min, self.cell_height, self.x_min, self.x_max - self.x_min,
            self.grid_size, self.x_min, self.cell_width, self.y_min, self.y_max - self.y_min,
            self.grid_size, self.grid_size, self.x_min, self.cell_width, self.y_min, self.cell_height
        )
        
        # Ejecutar el script JavaScript
        return self.driver.execute_script(grid_js)
    
    def _highlight_cell(self, row, col, color='yellow'):
        """Resalta una celda específica para mostrar la progresión"""
        # Calcular las coordenadas de la celda
        x = self.x_min + (col * self.cell_width)
        y = self.y_min + (row * self.cell_height)
        
        # JavaScript para resaltar la celda
        highlight_js = """
        // Crear elemento para resaltar
        const highlight = document.createElement('div');
        highlight.style.position = 'absolute';
        highlight.style.left = '%dpx';
        highlight.style.top = '%dpx';
        highlight.style.width = '%dpx';
        highlight.style.height = '%dpx';
        highlight.style.backgroundColor = '%s';
        highlight.style.opacity = '0.3';
        highlight.style.pointerEvents = 'none';
        highlight.style.zIndex = '9998';
        highlight.className = 'cell-highlight';
        
        // Eliminar resaltados anteriores
        document.querySelectorAll('.cell-highlight').forEach(el => el.remove());
        
        // Agregar al documento
        document.body.appendChild(highlight);
        """ % (x, y, self.cell_width, self.cell_height, color)
        
        # Ejecutar el script JavaScript
        return self.driver.execute_script(highlight_js)
    
    def _remove_visualizations(self):
        """Elimina todas las visualizaciones"""
        js = """
        // Eliminar cuadrícula
        const grid = document.getElementById('scraper-grid');
        if (grid) grid.remove();
        
        // Eliminar resaltados de celdas
        document.querySelectorAll('.cell-highlight').forEach(el => el.remove());
        """
        return self.driver.execute_script(js)