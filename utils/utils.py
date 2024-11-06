from datetime import date

# Verificar stock
def verificar_stock(stock):
    return 'true' in stock

def traducir_nombres_columnas(df):
    nombres_columnas = {
        'brand': 'Marca',
        'model': 'Modelo',
        'year': 'Año',
        'price_base': 'Precio Base',
        'price_net': 'Precio neto',
        'published': 'Publicado'
    }

    # Rename the columns
    df = df.rename(columns = nombres_columnas)
    return df

def actual_date():
    today = date.today()
    dia = today.day
    mes = today.month
    fecha = f"{dia}/{mes}"
    return fecha

