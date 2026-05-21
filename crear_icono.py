
from PIL import Image
import os

def crear_icono():
    print("=" * 50)
    print("  CREAR ICONO PARA EL EJECUTABLE")
    print("=" * 50)
    print()
    

    imagenes = [f for f in os.listdir('.') if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    if not imagenes:
        print("No se encontró ninguna imagen PNG o JPG en la carpeta.")
        print("Coloca una imagen en esta carpeta y vuelve a ejecutar.")
        return
    
    print("Imágenes encontradas:")
    for i, img in enumerate(imagenes, 1):
        print(f"   {i}. {img}")
    print()
    
    try:
        opcion = int(input("Selecciona el número de imagen (1-" + str(len(imagenes)) + "): "))
        if opcion < 1 or opcion > len(imagenes):
            print("Opción inválida")
            return
        
        imagen_seleccionada = imagenes[opcion - 1]
        
        
        img = Image.open(imagen_seleccionada)
        
      
        img = img.resize((256, 256), Image.Resampling.LANCZOS)
        
        nombre_icono = "icono.ico"
        img.save(nombre_icono, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)])
        
        print()
        print(f"Icono creado: {nombre_icono}")
        print()
        
        
    except Exception as e:
        print(f" Error: {e}")


if __name__ == "__main__":
    crear_icono()