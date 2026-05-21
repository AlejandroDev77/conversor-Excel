# filepath: src/procesador.py
import pdfplumber
import pandas as pd
import re


# Tu lista exacta de roles
LISTA_ROLES = [
    "OperadorEnvioDocumentos",
    "Operador RegistroDocumentos",
    "ClaveAutorizadade Envio",
    "ClaveAutorizadadeEnvio",
    "Reportes Confidenciales",
    "SRF_Consultas Baja",
    "SRF_ConsultasBaja",
    "ECCA_AutorizadorEntidad",
    "ECCA_OperadorEntidad",
    "RAC_OperadorEntidad_EIF",
    "RII_Operador_EIF",
    "SICA-AdmEntidadAutoriza",
    "SICA-AdmEntidadSolicita",
    "WS-OPERADOR-EIF",
    "WS-OPERADOR-BDP",
    "wsDetalleOperacionesCIRC",
    "AdmEntidadAutoriza",
    "ApruebaAviso",
    "CIS_Operador",
    "Consulta CPOP",
    "HR_OperadorEntidad",
    "NRI_AutorizaEntidad",
    "NRI_OperadorEntidad",
    "OperadorEntidad",
    "OperadorEnvio",
    "OperadorNotificador",
    "OperadorRegistroDocumentos",
    "RecepcionaReclamos",
    "RecibeCitaciones",
    "RegistraAviso",
    "RF_ConsultaEntidad",
    "RP_Operador",
    "AutorizadorEntidad",
    "SCN-OperadorEntidad",
    "SRF_OperadorEIF",
    "sw-riesgo-cartera",
    "WS_EntidadFinanciera",
    "WS_OperadorBDP"
]


LISTA_ROLES = sorted(LISTA_ROLES, key=len, reverse=True)


def escanear_roles_bdp(ruta_pdf):
    """Función para escanear roles del PDF"""
    datos_3_columnas = []
    usuario_actual = ""
    nombre_actual = ""

    with pdfplumber.open(ruta_pdf) as pdf:
        for pagina in pdf.pages:
            texto = pagina.extract_text()
            if not texto:
                continue

            lineas = texto.split('\n')

            for i, linea in enumerate(lineas):
                linea = linea.strip()

               
                if "@bdp.com.bo" in linea:
                    match_usr = re.search(r"([\w.-]+@bdp\.com\.bo)", linea)
                    if match_usr:
                        usuario_actual = match_usr.group(1).strip()

             
                if "Nombre:" in linea:
                    match_nom = re.search(r"Nombre:\s*(.*?)(?:Doc\. Ident|$)", linea)
                    if match_nom:
                        nombre_extraido = match_nom.group(1).strip()

                        if not nombre_extraido:
                            if i > 0:
                                linea_anterior = lineas[i - 1].strip()
                                if linea_anterior and ":" not in linea_anterior:
                                    nombre_extraido = linea_anterior

                        nombre_actual = nombre_extraido

                        if i + 1 < len(lineas):
                            sig_linea = lineas[i + 1].strip()
                            if sig_linea and ":" not in sig_linea and "@" not in sig_linea:
                                nombre_actual = nombre_actual + " " + sig_linea

                
                roles_en_linea = []
                for rol in LISTA_ROLES:
                    rol_escaped = re.escape(rol)
                    patron = r'\b' + rol_escaped + r'\b'
                    if re.search(patron, linea):
                        roles_en_linea.append(rol)

                for rol in roles_en_linea:
                    datos_3_columnas.append({
                        "Usuario": usuario_actual,
                        "Nombre": nombre_actual,
                        "Rol": rol
                    })

    df = pd.DataFrame(datos_3_columnas)
    df = df.drop_duplicates()
    return df