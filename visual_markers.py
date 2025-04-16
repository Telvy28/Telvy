def visualizar_mapa_grid(driver, x_min=150, y_min=200, x_max=500, y_max=650, grid_size=10):
    """
    Visualiza un área rectangular azul y una cuadrícula de puntos rojos en el mapa.
    
    Args:
        driver: WebDriver de Selenium
        x_min: Coordenada X mínima del área
        y_min: Coordenada Y mínima del área
        x_max: Coordenada X máxima del área
        y_max: Coordenada Y máxima del área
        grid_size: Número de divisiones en cada eje
    """
    print(f"Visualizando área: X({x_min}-{x_max}), Y({y_min}-{y_max}) con cuadrícula {grid_size}x{grid_size}")
    
    # Calcular dimensiones de cada celda
    cell_width = (x_max - x_min) / grid_size
    cell_height = (y_max - y_min) / grid_size
    
    # Limpiar marcadores previos y dibujar contorno azul
    driver.execute_script("""
        // Limpiar marcadores previos
        document.querySelectorAll('div[style*="red"], div[style*="blue"]').forEach(el => el.remove());
        
        // Añadir contorno del área (rectángulo azul)
        var outline = document.createElement('div');
        outline.style.position = 'absolute';
        outline.style.left = '""" + str(x_min) + """px';
        outline.style.top = '""" + str(y_min) + """px';
        outline.style.width = '""" + str(x_max - x_min) + """px';
        outline.style.height = '""" + str(y_max - y_min) + """px';
        outline.style.border = '2px solid blue';
        outline.style.zIndex = '9999';
        outline.style.pointerEvents = 'none';
        document.body.appendChild(outline);
    """)
    
    # Crear puntos rojos en cada celda de la cuadrícula
    for row in range(grid_size):
        for col in range(grid_size):
            # Calcular el centro de esta celda
            center_x = x_min + (col + 0.5) * cell_width
            center_y = y_min + (row + 0.5) * cell_height
            
            # Crear punto rojo
            driver.execute_script(f"""
                var marker = document.createElement('div');
                marker.style.position = 'absolute';
                marker.style.left = '{center_x}px';
                marker.style.top = '{center_y}px';
                marker.style.width = '8px';
                marker.style.height = '8px';
                marker.style.backgroundColor = 'red';
                marker.style.borderRadius = '50%';
                marker.style.zIndex = '10000';
                marker.style.pointerEvents = 'none';
                document.body.appendChild(marker);
            """)
    
    print(f"Visualización completada: {grid_size*grid_size} puntos dibujados")
    return True

# Ejemplo de uso
if __name__ == "__main__":
    print("Este script debe ser importado y usado con un driver válido de Selenium.")
    print("Ejemplo: visualizar_mapa_grid(driver, 150, 200, 500, 650, 10)")