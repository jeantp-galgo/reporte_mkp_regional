import json
import pandas as pd
from datetime import datetime
from google_sheet.utils import *
import re
import os

# Función de validación para cada registro con detalles de los campos faltantes
def is_valid_record(row):
    # Solo validar registros con estado "Pendiente"
    if row["Estado"] != "Pendiente":
        return []  # Si no es "Pendiente", retornar lista vacía para omitir este registro

    # Columnas requeridas para los registros con estado "Pendiente"
    required_columns = {
        "Nombre solicitante": True,
        "Fecha solicitud": True,
        "Tipo": True,
        "Marca": True,
        "Modelo": True,
        "Variaciones": True,
        "Precio base": True,
        "Precio neto": True
        }

    # Lista para almacenar los campos faltantes
    missing_fields = []
    
    for column, requirement in required_columns.items():
        value = row[column]
        if value == "Sin datos" or (requirement is True and not value):
            missing_fields.append(column)  # Agrega el nombre de la columna faltante

    return missing_fields  # Devuelve la lista de campos faltantes o incorrectos

# Función de validación para cada registro con detalles de los campos faltantes
def is_valid_record_cars(row):
    # Solo validar registros con estado "Pendiente"
    if row["Estado"] != "Pendiente":
        return []  # Si no es "Pendiente", retornar lista vacía para omitir este registro

    # Columnas requeridas para los registros con estado "Pendiente"
    required_columns = {
        "Nombre solicitante": True,
        "Fecha solicitud": True,
        "Tipo": True,
        "Marca": True,
        "Modelo": True,
        "Condición": True,
        "Variaciones": True,
        "Precio base": True,
        "Precio neto": True,
    }

    # Lista para almacenar los campos faltantes
    missing_fields = []
    
    for column, requirement in required_columns.items():
        value = row[column]
        if value == "Sin datos" or (requirement is True and not value):
            missing_fields.append(column)  # Agrega el nombre de la columna faltante

    return missing_fields  # Devuelve la lista de campos faltantes o incorrectos

def calcular_cuota_y_pie(precio, num_cuotas=36, cae_anual=74.6):
    # Convertir CAE anual a tasa mensual
    tasa_mensual = (1 + cae_anual / 100) ** (1 / 12) - 1
    
    # Calcular cuota mensual
    cuota_mensual = (precio * tasa_mensual) / (1 - (1 + tasa_mensual) ** -num_cuotas)
    
    # Calcular pie inicial (13.74% del precio)
    pie_inicial = precio * 0.1374
    
    return round(cuota_mensual, 2), round(pie_inicial, 2), cae_anual, num_cuotas

def calcular_cuota_y_pie_auto(precio, num_cuotas=64, cae_anual=33.0, porcentaje_pie=0.20):
    # Convertir CAE anual a tasa mensual usando una fórmula alternativa
    tasa_mensual = (1 + cae_anual / 100 / 12) - 1
    
    # Calcular cuota mensual
    cuota_mensual = (precio * (1 - porcentaje_pie) * tasa_mensual) / (1 - (1 + tasa_mensual) ** -num_cuotas)
    
    # Calcular pie inicial como porcentaje del precio base
    pie_inicial = precio * porcentaje_pie
    
    return round(cuota_mensual, 2), round(pie_inicial, 2), cae_anual, num_cuotas

def extraer_anio(modelo):
    # Dividir el texto en partes y tomar el último elemento
    partes = modelo.split()
    anio = partes[-1]  # Último elemento
    
    # Verificar que el último elemento sea un número de 4 dígitos
    if anio.isdigit() and len(anio) == 4:
        return int(anio)  # Convertir a entero para un valor numérico
    else:
        raise ValueError("El modelo no contiene un año válido al final.")

def crear_datos_publicacion(datos, pais):

    cuota_mensual, pie_inicial, cae_anual, num_cuotas = calcular_cuota_y_pie(datos["Precio neto"])

    if datos["Descuento"] == "Sin datos":
        descuento = 0
    else:
        descuento = datos["Descuento"]

    titulo = f'{datos["Marca"]} {datos["Modelo"]}'
    titulo_seo = f'{datos["Marca"]} {datos["Modelo"]} | Galgo México'
    if pais == "MX":
        moneda = "MXN"
    # Convertir variaciones string a lista
    variaciones = [v.strip() for v in datos["Variaciones"].split(",")] if datos["Variaciones"] != "Sin datos" else []

    return {
        "País": pais,
        "Titulo": titulo,
        "Subtitulo": "",
        "Titulo SEO": titulo_seo,
        "Descripción SEO": "",
        "Descripción": "",
        "Precio": datos["Precio neto"],
        "Moneda del precio": moneda,
        "Monto del descuento": descuento,
        "Tipo del descuento": "fixed",
        "Moneda del crédito": moneda,
        "Número de cuotas sugeridas": num_cuotas,
        "Valor de la cuota sugerida": cuota_mensual,
        "Pie/inicial/enganche sugerido": pie_inicial,
        "Pie/inicial/enganche promoción": 1,
        "CAE (o carga anual)": cae_anual,
        "Fotos Contenido": [],
        "Variaciones": variaciones,
        "URL Canonical":"",
        "Garantía": datos["Garantía"],
        "Relevancia": 50
    }

def crear_datos_publicacion_auto(datos, pais):

    print(pais)

    cuota_mensual, pie_inicial, cae_anual, num_cuotas = calcular_cuota_y_pie_auto(datos["Precio neto"])

    titulo = f'{datos["Marca"]} {datos["Modelo"]}'
    titulo_seo = f'{datos["Marca"]} {datos["Modelo"]} Galgo Chile'
    if pais == "CL":
        moneda = "CLP"

    if datos["Descuento"] == "Sin datos":
        descuento = 0
    else:
        descuento = datos["Descuento"]

    # Convertir variaciones string a lista
    variaciones = [v.strip() for v in datos["Variaciones"].split(",")] if datos["Variaciones"] != "Sin datos" else []

    return {
        "País": pais,
        "Titulo": titulo,
        "Subtitulo": "Mecánica" if re.search(r'MT|mt', datos["Modelo"]) else "Automática" if re.search(r'AT|at|CVT|cvt', datos["Modelo"]) else "",
        "Titulo SEO": titulo_seo,
        "Descripción SEO": "",
        "Descripción": "",
        "Precio": datos["Precio neto"],
        "Moneda del precio": moneda,
        "Monto del descuento": datos["Descuento"],
        "Tipo del descuento": "fixed",
        "Moneda del crédito": moneda,
        "Número de cuotas sugeridas": datos.get("Número de cuotas sugeridas", num_cuotas),
        "Valor de la cuota sugerida": datos.get("Valor de la cuota sugerida", cuota_mensual),
        "Pie/inicial/enganche sugerido": datos.get("Pie/inicial/enganche sugerido", pie_inicial),
        "Pie/inicial/enganche promoción": 1,
        "CAE (o carga anual)": datos.get("CAE (o carga anual)", cae_anual),
        "Fotos Contenido": [],
        "Variaciones": variaciones,
        "URL Canonical":"",
        "Garantía": datos["Garantía"],
        "Relevancia": 50
    }

def crear_datos_producto(datos, pais):

    return {
        "País": pais,
        "Marca": "",
        "Modelo": datos["Modelo"].replace(".", "-"),
        "Tipo": [],
        "Año": int(extraer_anio(datos["Modelo"])),
        "Fotos": [],
        "tabla_ficha_tecnica": "",
        "Cilindrada": ""
    }

def crear_datos_producto_auto(datos, pais):

    return {
        "País": pais,
        "Marca": "",
        "Modelo": datos["Modelo"].replace(".", "-") if re.search(r'\d{4}$', datos["Modelo"]) else f'{datos["Modelo"].replace(".", "-")} {datos["Año"]}',
        "Tipo": [],
        "Año": int(datos["Año"]),
        "Fotos": [],
        "tabla_ficha_tecnica": "",
        "Cilindrada": "",
        "Condición": datos["Condición"],
        "Transmisión": "Mecánica" if re.search(r'MT|mt', datos["Modelo"]) else "Automática" if re.search(r'AT|at|CVT|cvt', datos["Modelo"]) else "",
        "Localización": "Santiago",
        "Kilometraje": "",
        "Tracción": "",
        "Tipo de combustible": ""
    }

def crear_ruta_ficha_tecnica(tipo):
    """
    Tipo: Moto o Auto
    """
    return {"ruta_ficha_tecnica": "./solicitudes/",
            "tipo": tipo
            }

# Función para crear los registros JSON
def crear_registros_json(df, pais, codigo_hoja):   
    google_sheet_func = google_sheet_funciones()

    # Reemplazar NaN con "Sin datos" para evitar errores en JSON
    df = df.fillna("Sin datos")

    i = 0
    # Guardar cada registro válido como JSON separado
    for index, row in df.iterrows():
        # Verificar y obtener campos faltantes solo si "Estado" es "Pendiente"
        if row["Estado"] == "Pendiente":
            missing_fields = is_valid_record(row)  # Verifica los campos faltantes
            
            if not missing_fields:  # Si no faltan campos, procesa el registro
                i += 1
                try:
                    # Intentar primero formato DD/MM/YYYY, si falla, intentar MM/DD/YYYY
                    try:
                        fecha_solicitud = datetime.strptime(row["Fecha solicitud"], "%d/%m/%Y")
                    except ValueError:
                        fecha_solicitud = datetime.strptime(row["Fecha solicitud"], "%m/%d/%Y")
                    
                    # Convertir al formato deseado
                    fecha_solicitud = fecha_solicitud.strftime("%d%m%Y")
                    
                    datos_publicacion = crear_datos_publicacion(row, pais)
                    datos_producto = crear_datos_producto(row, pais)
                    datos_ficha_tecnica = crear_ruta_ficha_tecnica("Moto")

                    # Crear el nombre de archivo usando la fecha, país y modelo
                    modelo = row["Modelo"].replace(" ", "_")  # Reemplaza espacios en el nombre del modelo
                    file_name = f"./solicitudes/{codigo_hoja}/Noviembre 2024/{fecha_solicitud}-{pais}-{modelo}.json"
                    
                    # Convertir la fila a un diccionario
                    row_dict = row.to_dict()
                    
                    # Agregar datos_publicacion al diccionario
                    row_dict['datos_publicacion'] = datos_publicacion
                    row_dict['datos_producto'] = datos_producto
                    row_dict['ficha_tecnica_ruta'] = datos_ficha_tecnica
                    
                    # Guardar el diccionario en un archivo JSON con caracteres especiales y sin Unicode
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(row_dict, f, indent=4, ensure_ascii=False)
                    print(f"Archivo {file_name} guardado.")
                
                except Exception as e:
                    print(f"Error al procesar el registro {index + 2}: {e}")
            else:
                # Imprimir los detalles del registro incompleto si el estado es "Pendiente"
                print(f"Registro {index + 2} incompleto. Faltan los siguientes campos: {', '.join(missing_fields)}")
    
    print(f"Total de registros válidos procesados: {i}")

# Función para crear los registros JSON
def crear_registros_json_auto(df, pais, codigo_hoja):   
    """
    pais: CL, CO, MX y PE
    codigo_hoja: CL Autos, CL Motos, CO, PE y MX
    """
    google_sheet_func = google_sheet_funciones()

    # Reemplazar NaN con "Sin datos" para evitar errores en JSON
    df = df.fillna("Sin datos")
    
    # Convertir la columna Año a integer
    df["Año"] = df["Año"].apply(lambda x: int(x) if x != "Sin datos" else "Sin datos")

    i = 0
    # Guardar cada registro válido como JSON separado
    for index, row in df.iterrows():
        # Verificar y obtener campos faltantes solo si "Estado" es "Pendiente"
        if row["Estado"] == "Pendiente":
            missing_fields = is_valid_record_cars(row)  # Verifica los campos faltantes
            
            if not missing_fields:  # Si no faltan campos, procesa el registro
                print(row)
                i += 1
                try:
                    # Intentar primero formato DD/MM/YYYY, si falla, intentar MM/DD/YYYY
                    try:
                        fecha_solicitud = datetime.strptime(row["Fecha solicitud"], "%d/%m/%Y")
                    except ValueError:
                        fecha_solicitud = datetime.strptime(row["Fecha solicitud"], "%m/%d/%Y")
                    
                    # Convertir al formato deseado
                    fecha_solicitud = fecha_solicitud.strftime("%d%m%Y")
                    
                    datos_publicacion = crear_datos_publicacion_auto(row, pais)
                    datos_producto = crear_datos_producto_auto(row, pais)
                    datos_ficha_tecnica = crear_ruta_ficha_tecnica("Auto")

                    # Crear el nombre de archivo usando la fecha, país y modelo
                    modelo = row["Modelo"].replace(" ", "_")  # Reemplaza espacios en el nombre del modelo
                    file_name = f"./solicitudes/{codigo_hoja}/Noviembre 2024/{fecha_solicitud}-{pais}-{modelo}.json"
                    
                    # Convertir la fila a un diccionario
                    row_dict = row.to_dict()
                    
                    # Agregar datos_publicacion al diccionario
                    row_dict['datos_publicacion'] = datos_publicacion
                    row_dict['datos_producto'] = datos_producto
                    row_dict['ficha_tecnica_ruta'] = datos_ficha_tecnica
                    
                    # Guardar el diccionario en un archivo JSON con caracteres especiales y sin Unicode
                    with open(file_name, "w", encoding="utf-8") as f:
                        json.dump(row_dict, f, indent=4, ensure_ascii=False)
                    print(f"Archivo {file_name} guardado.")
                
                except Exception as e:
                    print(f"Error al procesar el registro {index + 2}: {e}")
            else:
                # Imprimir los detalles del registro incompleto si el estado es "Pendiente"
                print(f"Registro {index + 2} incompleto. Faltan los siguientes campos: {', '.join(missing_fields)}")
    
    print(f"Total de registros válidos procesados: {i}")
