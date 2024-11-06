import google_sheet.conexion as conexion
from gspread_dataframe import get_as_dataframe, set_with_dataframe
import gspread
from utils.utils import *
from datetime import datetime

class google_sheet_funciones:
    def __init__(self):
        self.client = conexion.conectarse_google_sheet()

    def otorgar_permisos_google_sheet(self, new_sheet):
        email = 'jtrujillo@galgo.com'
        new_sheet.share(email, perm_type='user', role='writer')
        return f"Permisos dados al correo: {email}"

    def crear_google_sheet(self, nombre_hoja):
        new_sheet = self.client.create(nombre_hoja)
        print(f"Google Sheet creado, titulo: {new_sheet.title}")
        sheet_url = f"https://docs.google.com/spreadsheets/d/{new_sheet.id}"
        print(f"URL: {sheet_url}")
        self.otorgar_permisos_google_sheet(new_sheet)

    # Función para eliminar una Google Sheet por ID
    def eliminar_google_sheet(service, file_id):
        try:
            service.files().delete(fileId=file_id).execute()
            print(f"La hoja de Google con ID {file_id} ha sido eliminada correctamente.")
        except Exception as e:
            print(f"Error al eliminar la hoja de Google: {e}")

    def mostrar_hojas(self):
        hojas = self.client.openall()
        print("Hojas disponibles:")
        for hoja in hojas:
            print(f"- {hoja}")

    def seleccionar_hoja(self, nombre_hoja):
        return self.client.open(nombre_hoja)
    
    def leer_datos_google_sheet(self, sheet_name, worksheet_name):
        """Función para leer todas las filas y columnas de una hoja de Google Sheets específica y convertir a DataFrame."""
        try:
            # Abre el archivo de Google Sheets por su nombre
            sheet = self.client.open(sheet_name)
            
            # Selecciona la hoja específica dentro del archivo por nombre
            worksheet = sheet.worksheet(worksheet_name)
            
            # Convertir la hoja a un DataFrame
            df = get_as_dataframe(worksheet, evaluate_formulas=True, header=0)  # `header=0` usa la primera fila como encabezado

            return df  # Devuelve el DataFrame
        except Exception as e:
            print(f"Error al leer los datos de la hoja: {e}")
            return None
    
    # Función para obtener la fecha actual en el formato deseado
    def actual_date(self):
        today = datetime.today()
        return today.strftime("%d/%m")

    # Función para actualizar una hoja específica llamada "Base total"
    def actualizar_hoja_base(self, sheet, df):
        # Generar el nombre de la hoja con la fecha actual
        sheet_name = f"Base total {self.actual_date()}"

        # Buscar una hoja existente que comience con "Base total"
        possible_sheets = [ws for ws in sheet.worksheets() if ws.title.startswith("Base total")]
        
        if possible_sheets:
            # Si encuentra una hoja con "Base total", renómbrala con la nueva fecha
            previous_worksheet = possible_sheets[0]
            previous_worksheet.update_title(sheet_name)
            worksheet = previous_worksheet
        else:
            # Si no encuentra una hoja existente, crea una nueva con el nombre y fecha actual
            worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

        # Limpiar el contenido de la hoja antes de actualizarla
        worksheet.clear()

        # Escribir el nombre de la hoja en la primera fila
        worksheet.update("A1", [[f"{sheet_name}"]])

        # Escribir los datos del DataFrame a partir de la segunda fila
        set_with_dataframe(worksheet, df, row=2, col=1)
        print(f"Updated sheet: {sheet_name}")

    # Función para actualizar múltiples hojas con diferentes países
    def actualizar_todas_las_hojas(self, sheet, dataframes):
        # Iterar sobre cada país, DataFrame y tipo de hoja correspondiente en `dataframes`
        for country, df, tipo_de_hoja in dataframes:
            # Generar el nombre de la hoja utilizando el tipo de hoja específico y la fecha actual
            sheet_name = f"Base {country} {self.actual_date()} {tipo_de_hoja}"

            # Buscar si ya existe una hoja del mismo país y tipo, sin importar la fecha
            possible_sheets = [ws for ws in sheet.worksheets() if ws.title.startswith(f"Base {country}") and ws.title.endswith(tipo_de_hoja)]
            
            if possible_sheets:
                # Si encuentra una hoja que coincide, renómbrala con la nueva fecha
                previous_worksheet = possible_sheets[0]
                previous_worksheet.update_title(sheet_name)
                worksheet = previous_worksheet
            else:
                # Si no encuentra una hoja con el nombre base, crea una nueva
                worksheet = sheet.add_worksheet(title=sheet_name, rows="1000", cols="20")

            # Limpiar el contenido de la hoja antes de actualizarla
            worksheet.clear()

            # Escribir el nombre de la hoja en la primera fila
            worksheet.update("A1", [[f"{sheet_name}"]])

            # Escribir los datos del DataFrame a partir de la segunda fila
            set_with_dataframe(worksheet, df, row=2, col=1)
            print(f"Updated sheet: {sheet_name}")


    def actualizar_estado(self, sheet_name, worksheet_name, fila, nuevo_estado="En proceso"):
            """
            Actualiza el estado de un registro en una hoja de Google Sheets.
            
            Parámetros:
            - sheet_name: Nombre del archivo de Google Sheets.
            - worksheet_name: Nombre de la hoja específica dentro del archivo.
            - fila: Índice de la fila que se quiere actualizar (inicio en 1).
            - nuevo_estado: Nuevo valor del estado, por defecto "Procesado".
            """
            try:
                # Abrir el archivo de Google Sheets y la hoja específica
                sheet = self.client.open(sheet_name)
                worksheet = sheet.worksheet(worksheet_name)

                # Actualizar la celda de "Estado" en la fila especificada (ejemplo: columna "A" para estado)
                worksheet.update(f"A{fila}", [[nuevo_estado]])
                print(f"Estado de la fila {fila} actualizado a '{nuevo_estado}' en {worksheet_name}.")
            except Exception as e:
                print(f"Error al actualizar el estado en la hoja de Google Sheets: {e}")

