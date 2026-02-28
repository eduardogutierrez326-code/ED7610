# Dentro de tu nuevo archivo calendario_menu.py

# ... (Configuración inicial)

# Dividimos el inventario en 2 bloques (Semana 1 y Semana 2)
# Esto asegura que no te acabes toda la RES en los primeros 3 días
random.shuffle(fuertes)
mitad = len(fuertes) // 2
bloque1 = fuertes[:mitad]
bloque2 = fuertes[mitad:]

# El algoritmo irá tomando de bloque1 los primeros 7-8 días 
# y de bloque2 el resto del periodo.
