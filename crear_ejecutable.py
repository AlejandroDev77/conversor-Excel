

import os
import subprocess
import sys

def crear_ejecutable():
    print("=" * 50)
    print("  CREANDO EJECUTABLE BDP")
    print("=" * 50)
    print()
    
   
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller no está instalado")
        print("Ejecuta: pip install pyinstaller")
        return
    
    
    comando = [
        "pyinstaller",
        "--onefile",           
        "--windowed",          
        "--name=EscanerRolesBDP",  
        "--icon=icono.ico",         
        "--clean",             
        "app.py"
    ]
    
    print("Generando ejecutable")
    print()
    
    try:
        subprocess.run(comando, check=True)
        print()
        print("=" * 50)
        print("EJECUTABLE CREADO")
        print("=" * 50)
        print()
        print("Ubicación:")
        print("dist/EscanerRolesBDP.exe")
        print()
        
        
    except subprocess.CalledProcessError as e:
        print(f"Error al crear ejecutable: {e}")


if __name__ == "__main__":
    crear_ejecutable()