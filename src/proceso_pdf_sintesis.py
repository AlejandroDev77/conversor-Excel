import pandas as pd
import re
import pdfplumber


def procesar_texto_reporte(texto):
    
    corte_final = re.search(r'(CAJERO SUPERVISOR O ADM\.|Totales\s*:|FIN DEL REPORTE)', texto, flags=re.IGNORECASE)
    if corte_final:
        texto = texto[:corte_final.start()]

    texto = texto.replace('|', ' ')
    texto = re.sub(r'\n+', ' ', texto)
    
    
    basura_previa = [
        r'SINTESIS S\.A\.', r'cnrep\d+', r'REPORTE DE O[PF]ERADORES EN LINEA',
        r'CTA\.\s*UNICA', r'CSTA\.\s*UNICA', r'Fecha:\s*[\d=/-]+', r'Hora\s*:\s*[\d/]*',
        r'Pag\s*:\s*\d*', r'Inst\.:\s*\d+', r'Agen\.:\s*\d+',
        r'\bCIU\.', r'\bENTIDAD\b', r'\bAG\b', r'\bCOD\b', r'NRO\.TELF\.', 
        r'\bNOMBRE\b', r'\bROL\b', r'\bEST\b', r'\b0000\b', r'\b00\b',
        r'DPTO:\s*\d+', r'CIUDAD:\s*\d+',
        r'-{3,}',                       
        r'\d{2,3}[=-]?/\d{2}/\d{0,4}',  
        r'\by\s+Pag\s*:\s*\d+',         
        r'\by\s+CTA\.\s*UNICA',        
        r'\by\s+(?=\d)',                
        r'_{3,}'                        
    ]
    
    for b in basura_previa:
        texto = re.sub(b, ' ', texto, flags=re.IGNORECASE)
        
    texto = re.sub(r'\s+', ' ', texto) # Normaliza espacios

    patron_registro = r'\b(\d{3})\s+(880|\d{1,2})\s+(880|\d{1,2})\s+(\d{1,6})\s+(.*?)(?=\s+\d{3}\s+(?:880\s+\d{1,2}|\d{1,2}\s+880)\s+\d{1,6}|\s*$)'
    
    registros = re.findall(patron_registro, texto)
    datos_procesados = []

    roles_posibles = [
        'CREDITOS BDP', 'CONTABILIDAD BDP', 'CONTABILIDAD BDF', 
        'ADM. NACIONAL', 'OPERADOR SFL', 'SUP. AGENCIA', 
        'CARTERA BDP', 'CREDITOS'
    ]

    for ciu, val1, val2, cod, resto in registros:
        entidad = '880'
        ag = val2 if val1 == '880' else val1

        # 1. Extraer CTA.UNICA
        cta_match = re.search(r'\b(\d{6,}[A-Za-z]+\d*)\b', resto)
        cta_unica = cta_match.group(1) if cta_match else ''
        if cta_unica:
            resto = resto.replace(cta_unica, '', 1)
        
        if not cta_unica:
            cta_match = re.search(r'\b((?=\w*[a-z])(?=\w*[A-Z])\w+|\d{3,}[A-Za-z]{1,}|[A-Za-z]{1,}\d+)\b', resto)
            cta_unica = cta_match.group(1) if cta_match else ''
            if cta_unica:
                resto = resto.replace(cta_unica, '', 1)
        
        # 2. Extraer ESTADO (X o V)
        est_match = re.search(r'\b(X|V)\b', resto)
        est = est_match.group(1) if est_match else ''
        if est:
            resto = re.sub(r'\b(X|V)\b', '', resto, count=1)
            
        # 3. Extraer ROL
        rol = ''
        for r in roles_posibles:
            if r in resto:
                rol = r
                resto = resto.replace(r, '', 1)
                break
        
        # 4. Extraer NRO.TELF
        nro_telf_match = re.search(r'\b(\d{7,8})\b', resto)
        nro_telf = nro_telf_match.group(1) if nro_telf_match else ''
        if nro_telf:
            resto = resto.replace(nro_telf, '', 1)
                
       
        resto = re.sub(r'\b\d{2,4}/\d{2}/\d{2,4}\b', '', resto) 
        resto = re.sub(r'\b\d{2}/\d{2}/\d{2}\b', '', resto)
        nombre = re.sub(r'\s+', ' ', resto).strip()
        
        datos_procesados.append({
            'CIU': ciu,
            'ENTIDAD': entidad,
            'AG': ag,
            'COD': cod,
            'NRO.TELF.': nro_telf,
            'NOMBRE': nombre,
            'ROL': rol,
            'CTA.UNICA': cta_unica,
            'EST': est
        })

    return datos_procesados


def procesar_sintesis_pdf(ruta_pdf):
    """Función para procesar PDFs de Síntesis y retornar DataFrame"""
    texto_bruto = ""
    try:
        with pdfplumber.open(ruta_pdf) as pdf:
            for page in pdf.pages:
                texto_bruto += page.extract_text() or ""
    except FileNotFoundError:
        raise Exception(f"No se encontró el archivo '{ruta_pdf}'")
    except Exception as e:
        raise Exception(f"Error al leer el PDF: {e}")
    
    # Procesar el texto del PDF
    datos = procesar_texto_reporte(texto_bruto)
    df = pd.DataFrame(datos)
    df = df[df['NOMBRE'] != '']
    
    return df