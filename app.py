
import os
import sys
import threading


sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageDraw
import pystray
from src.procesador import escanear_roles_bdp
from src.proceso_pdf_sintesis import procesar_sintesis_pdf, procesar_archivo



def obtener_ruta_icono():
    """Obtener la ruta del icono - funciona tanto en desarrollo como en exe"""
    if getattr(sys, 'frozen', False):
     
        base_path = sys._MEIPASS
    else:
        # Estamos en desarrollo
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, "icono.ico")



def crear_icono_default():
    """Crear un icono simple en memoria"""
    img = Image.new('RGB', (64, 64), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([12, 8, 52, 56], outline='#4CAF50', width=3)
    draw.line([18, 18, 46, 18], fill='#4CAF50', width=2)
    draw.line([18, 26, 40, 26], fill='#4CAF50', width=2)
    draw.line([18, 34, 44, 34], fill='#4CAF50', width=2)
    return img



_icono_tray_global = None


def run_tray_icon(icono_path, app_ref):
    """Ejecutar el icono del tray en un hilo separado"""
    global _icono_tray_global
    
    try:
        # Cargar icono
        if os.path.exists(icono_path):
            imagen = Image.open(icono_path)
            if imagen.mode != 'RGBA':
                imagen = imagen.convert('RGBA')
            imagen = imagen.resize((32, 32), Image.Resampling.LANCZOS)
        else:
            imagen = crear_icono_default()
        
        # Crear menú
        menu = pystray.Menu(
            pystray.MenuItem("Mostrar ventana", lambda _: app_ref.root.after(0, app_ref.mostrar_desde_tray), default=True),
            pystray.MenuItem("Salir", lambda _: app_ref.root.after(0, app_ref.salir_desde_tray)),
            
        )
        
        
        _icono_tray_global = pystray.Icon(
            "EscanerRolesBDP",
            imagen,
            "Escáner de Roles BDP",
            menu
        )
        _icono_tray_global.run()
    except Exception as e:
        print(f"Error en tray: {e}")


class AppEscritorio:
    def __init__(self, root):
        self.root = root
        self.root.title("Escáner de Roles BDP")
        self.root.geometry("500x450")
        self.root.resizable(False, False)
        
        
        icono_path = obtener_ruta_icono()
        if os.path.exists(icono_path):
            self.root.iconbitmap(icono_path)
        
      
        self.root.eval('tk::PlaceWindow . center')
        
        self.archivo_seleccionado = None
        self.icono_path = icono_path
        self.tray_activo = False
        self.tipo_procesamiento = tk.StringVar(value="roles_bdp")  # Por defecto roles BDP
        
     
        self.root.protocol("WM_DELETE_WINDOW", self.minimizar_a_tray)
        
        
        self.root.bind("<Unmap>", self.on_minimizar)
        
        self.crear_interfaz()
    
    def on_minimizar(self, event):
        """Cuando se minimiza con el botón -"""
        
        if self.root.state() == 'iconic':
           
            pass 
    
    def iniciar_tray(self):
        """Iniciar el icono del tray"""
        global _hilo_tray, _icono_tray_global
        
        if not self.tray_activo:
            self.tray_activo = True
         
            if _icono_tray_global:
                try:
                    _icono_tray_global.stop()
                except:
                    pass
            
          
            import time
            _hilo_tray = threading.Thread(target=run_tray_icon, args=(self.icono_path, self), daemon=True)
            _hilo_tray.start()
            time.sleep(0.2)
    
    def detener_tray(self):
        """Detener el icono del tray"""
        global _icono_tray_global
        if _icono_tray_global:
            try:
                _icono_tray_global.stop()
            except:
                pass
        self.tray_activo = False
    
    def minimizar_a_tray(self):
        """Minimizar la ventana al system tray"""
        self.root.withdraw()
        self.iniciar_tray()
    
    def mostrar_desde_tray(self):
        """Mostrar la ventana desde el tray"""
        self.detener_tray()
        self.root.deiconify()
        self.root.state('normal')
        self.root.lift()
        self.root.focus()
    
    def salir_desde_tray(self):
        """Salir de la aplicación desde el tray"""
        self.detener_tray()
        self.root.destroy()
        sys.exit()
    
    def crear_interfaz(self):
        # Título con icono
        titulo = tk.Label(self.root, text="📄 Escáner de PDFs", 
                         font=("Arial", 18, "bold"))
        titulo.pack(pady=15)
        
        # Selector de tipo de procesamiento
        frame_selector = tk.LabelFrame(self.root, text="Selecciona el tipo de procesamiento", 
                                       font=("Arial", 10), padx=10, pady=10)
        frame_selector.pack(pady=10, padx=20, fill="x")
        
        rb_roles = tk.Radiobutton(frame_selector, text="🔐 Roles BDP", 
                                 variable=self.tipo_procesamiento, 
                                 value="roles_bdp",
                                 font=("Arial", 10),
                                 command=self.actualizar_subtitulo)
        rb_roles.pack(anchor="w", pady=5)
        
        rb_sintesis = tk.Radiobutton(frame_selector, text="📊 Síntesis (Operadores)", 
                                    variable=self.tipo_procesamiento, 
                                    value="sintesis",
                                    font=("Arial", 10),
                                    command=self.actualizar_subtitulo)
        rb_sintesis.pack(anchor="w", pady=5)
        
        # Subtítulo
        self.subtitulo = tk.Label(self.root, text="Selecciona un PDF de usuarios BDP\ny obtén el Excel con sus roles",
                           font=("Arial", 10), fg="gray")
        self.subtitulo.pack(pady=5)
        
        # Frame para seleccionar archivo
        frame_archivo = tk.Frame(self.root)
        frame_archivo.pack(pady=15)
        
        self.label_archivo = tk.Label(frame_archivo, text="Ningún archivo seleccionado",
                                     font=("Arial", 10), fg="orange", width=40)
        self.label_archivo.pack(pady=5)
        
        btn_seleccionar = tk.Button(frame_archivo, text="📁 Seleccionar Archivo (PDF/TXT)",
                                   command=self.seleccionar_archivo,
                                   font=("Arial", 11), bg="#e8e8e8",
                                   padx=20, pady=8)
        btn_seleccionar.pack()
        
       
        self.barra_progreso = ttk.Progressbar(self.root, length=300, mode='indeterminate')
        self.barra_progreso.pack(pady=10)
        
        self.label_estado = tk.Label(self.root, text="", font=("Arial", 9), fg="blue")
        self.label_estado.pack()
        
        self.btn_procesar = tk.Button(self.root, text="Procesar PDF",
                                     command=self.procesar_en_hilo,
                                     font=("Arial", 12, "bold"),
                                     bg="#4CAF50", fg="white",
                                     padx=30, pady=10)
        self.btn_procesar.pack(pady=10)
        self.btn_procesar.config(state="disabled")
        
       
        footer = tk.Label(self.root, text="Sistema de extracción de datos de PDFs",
                         font=("Arial", 8), fg="gray")
        footer.pack(side="bottom", pady=10)
    
    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar archivo (PDF o TXT)",
            filetypes=[("PDF files", "*.pdf"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if archivo:
            self.archivo_seleccionado = archivo
            nombre_archivo = os.path.basename(archivo)
            self.label_archivo.config(text=f"📄 {nombre_archivo}", fg="green")
            self.btn_procesar.config(state="normal")
    
    def actualizar_subtitulo(self):
        """Actualizar el subtítulo según el tipo de procesamiento seleccionado"""
        if self.tipo_procesamiento.get() == "roles_bdp":
            self.subtitulo.config(text="Selecciona un PDF de usuarios BDP\ny obtén el Excel con sus roles")
        else:
            self.subtitulo.config(text="Selecciona un PDF o TXT de reporte de Síntesis\ny obtén el Excel con los operadores")
    
    def procesar_en_hilo(self):
        """Ejecutar el procesamiento en un hilo separado para no bloquear la UI"""
        self.btn_procesar.config(state="disabled")
        self.label_estado.config(text="Procesando...")
        self.barra_progreso.start(10)
        
        hilo = threading.Thread(target=self.procesar_pdf)
        hilo.start()
    
    def procesar_pdf(self):
        try:
            
            if self.tipo_procesamiento.get() == "roles_bdp":
                df = escanear_roles_bdp(self.archivo_seleccionado)
                titulo_dialogo = "Roles BDP"
                archivo_defecto = "Roles_BDP.xlsx"
            else:  # sintesis
                df = procesar_archivo(self.archivo_seleccionado)
                titulo_dialogo = "Síntesis"
                archivo_defecto = "Operadores_Sintesis.xlsx"
            
            if df.empty:
                self.root.after(0, lambda: messagebox.showwarning(
                    "Advertencia", f"No se encontraron datos en el PDF"))
                self.root.after(0, self.fin_procesamiento)
                return
            
            
            output_file = filedialog.asksaveasfilename(
                title="Guardar Excel",
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=archivo_defecto
            )
            
            if output_file:
                df.to_excel(output_file, index=False)
                self.root.after(0, lambda: messagebox.showinfo(
                    "Éxito", f"Excel de {titulo_dialogo} generado!\n\nSe encontraron {len(df)} registros.\n\nGuardado en:\n{output_file}"))
            
            self.root.after(0, self.fin_procesamiento)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", f"Error al procesar:\n{str(e)}"))
            self.root.after(0, self.fin_procesamiento)
    
    def fin_procesamiento(self):
        self.barra_progreso.stop()
        self.label_estado.config(text="")
        self.btn_procesar.config(state="normal")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppEscritorio(root)
    root.mainloop()