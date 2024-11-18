import pandas as pd
from datetime import datetime
import gspread
from google_sheet.utils import google_sheet_funciones

class ReporteDiario:
    def __init__(self):
        self.gs_func = google_sheet_funciones()

    def normalizar_fecha(self, fecha_str):
        """Normaliza la fecha desde diferentes formatos a un objeto datetime o None si es inválido."""
        formatos = ['%d/%m/%y', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d']
        fecha_str = str(fecha_str).strip()
        for formato in formatos:
            try:
                fecha = datetime.strptime(fecha_str, formato)
                if formato == '%d/%m/%y' and fecha.year < 2000:
                    fecha = fecha.replace(year=fecha.year + 2000)
                return fecha
            except ValueError:
                continue
        return None

    def generar_reporte_para_hojas(self, nombre_hoja_principal, nombres_areas, nombre_hoja_reporte):
        estados = ['Pendiente', 'Espera de informacion', 'En proceso', 
                   'Con información básica', 'Publicacion en espera de imágenes', 'Publicada']
        tipos_solicitud = [
            'Nuevo producto comercial', 'Nuevo producto SEO', 'Nueva version', 
            'Nueva marca', 'Actualizar precios', 'Marcar sin stock', 'Marcar con stock', 
            'Cambiar nombre', 'Sustituir', 'Despublicar (auto)', 'Otro'
        ]
        
        hoy = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        print(f"Fecha actual: {hoy.strftime('%d/%m/%Y')}")

        # Crear o seleccionar el reporte principal
        try:
            sheet_reporte = self.gs_func.seleccionar_hoja(nombre_hoja_reporte)
        except gspread.exceptions.SpreadsheetNotFound:
            sheet_reporte = self.gs_func.client.create(nombre_hoja_reporte)
            self.gs_func.otorgar_permisos_google_sheet(sheet_reporte)
            print(f"Archivo de reporte '{nombre_hoja_reporte}' creado: {sheet_reporte.url}")

        print(f"Link al archivo de reporte: {sheet_reporte.url}")

        # Procesar cada área
        # Fecha personalizada                 'Fecha': ['15/11/2023'] * len(tipos_solicitud),
        for area in nombres_areas:
            reporte_diario = {
                'Fecha': ['15/11/2024'] * len(tipos_solicitud),
                'Tipo solicitud': tipos_solicitud,
                'Nuevas solicitudes': [0] * len(tipos_solicitud),
                'Total acumulado': [0] * len(tipos_solicitud),
                'Total publicadas': [0] * len(tipos_solicitud),
                'Total restantes': [0] * len(tipos_solicitud)
            }
            
            # Leer datos de la hoja principal
            df = self.gs_func.leer_datos_google_sheet(nombre_hoja_principal, area)
            
            if df is None or df.empty:
                print(f"No hay datos para procesar en {area}. Continuando con la siguiente área...")
                continue
            
            # Normalizar las fechas en la columna 'Fecha solicitud'
            df['Fecha solicitud'] = df['Fecha solicitud'].apply(self.normalizar_fecha)
            df['Fecha solicitud'] = pd.to_datetime(df['Fecha solicitud'], errors='coerce')

            # Contar las solicitudes del 15 de noviembre de 2024
            for i, tipo in enumerate(tipos_solicitud):
                solicitudes_tipo = df[df['Tipo'] == tipo]
                #nuevas_solicitudes = solicitudes_tipo[solicitudes_tipo['Fecha solicitud'].dt.date == hoy.date()]
                
                nuevas_solicitudes = solicitudes_tipo[solicitudes_tipo['Fecha solicitud'].dt.date == datetime(2024, 11, 15).date()]
                # Asegúrate de que 'Fecha solicitud' no sea NaT antes de contar
                nuevas_solicitudes = nuevas_solicitudes[nuevas_solicitudes['Fecha solicitud'].notna()]
                reporte_diario['Nuevas solicitudes'][i] = len(nuevas_solicitudes)

                # Total acumulado para este tipo de solicitud
                reporte_diario['Total acumulado'][i] = len(solicitudes_tipo)

                # Contar las publicadas y calcular el total restante
                publicadas = solicitudes_tipo[solicitudes_tipo['Estado'] == 'Publicada']
                reporte_diario['Total publicadas'][i] = len(publicadas)
                reporte_diario['Total restantes'][i] = reporte_diario['Total acumulado'][i] - reporte_diario['Total publicadas'][i]

            # Crear el DataFrame del reporte diario para esta área
            reporte_diario_df = pd.DataFrame(reporte_diario)

            # Agregar el reporte diario al archivo de Google Sheets
            nombre_reporte = f"Reporte Diario - {area}"

            try:
                reporte_sheet = sheet_reporte.worksheet(nombre_reporte)
            except gspread.exceptions.WorksheetNotFound:
                reporte_sheet = sheet_reporte.add_worksheet(title=nombre_reporte, rows="1000", cols="20")

            # Obtener el historial existente y agregar el reporte diario
            historico_datos = reporte_sheet.get_all_records()
            historico_df = pd.DataFrame(historico_datos)
            actualizado_historico_df = pd.concat([historico_df, reporte_diario_df], ignore_index=True)
            actualizado_historico_df = actualizado_historico_df.fillna(0)

            # Actualizar la hoja de reporte
            reporte_sheet.clear()
            reporte_sheet.update([actualizado_historico_df.columns.values.tolist()] + actualizado_historico_df.values.tolist())

            print(f"Reporte diario actualizado para '{area}' en la hoja '{nombre_reporte}' en el archivo de reporte '{nombre_hoja_reporte}'.")

if __name__ == "__main__":
    nombres_areas = [
        "Solicitudes MX Motos", "Solicitudes CL Autos", "Solicitudes CL Motos", "Solicitudes CO Motos", "Solicitudes PE Motos"
    ]
    reporte = ReporteDiario()
    reporte.generar_reporte_para_hojas(
        nombre_hoja_principal="Actualizaciones MKP Regional version 2",
        nombres_areas=nombres_areas,
        nombre_hoja_reporte="Reporte del MKP Regional"
    )
