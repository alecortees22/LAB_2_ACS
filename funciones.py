# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - Funciones para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #
import pandas as pd
import numpy as np

# ----------------- Funcion para mandar llamar archivo y acomodarlo a mi conveniencia--------------
def f_leer_archivo(param_archivo):
    param_archivo = 'Statement_1.xlsx'
    df_data = pd.read_excel('archivos/' + param_archivo, sheet_name='Statement')
    # elegir solo renglones en los que la columna type == buy | type == 'sell'
    df_data = df_data.loc[df_data['type']!='balance']
    # para poner en minusculas los titulos de las columnas de mi archivo
    df_data_columns = [list(df_data.columns)[i].lower() for i in range(0, len(df_data.columns))]

    # asegurar que ciertas columnas son del tipo numerico_
    # Cambiar tipo de datos en columnas a numerico
    numcols = ['order', 's/l', 't/p', 'closeprice', 'commission', 'size', 'taxes', 'swap', 'profit', 'openprice']
    df_data[numcols] = df_data[numcols].apply(pd.to_numeric)

    return df_data


def f_pip_size(param_ins):
    inst = param_ins
    # Lista de pips por instrumento
    pips_inst = {'usdjpy-2': 100, 'eurusd-2': 10000, 'eurcad-2': 10000, 'eurgbp-2': 10000, 'usdcad-2': 10000,
                 'audusd-2': 10000, 'audjpy-2': 100, 'gbpusd-2': 10000, 'eurjpy-2': 100, 'xauusd': 10000,
                 'eurjpy': 100, 'eurusd': 10000, 'gbpusd': 10000, 'btcusd': 10000, 'eurgbp': 10000,
                 'gbpjpy': 100, 'usdcad': 10000, 'usdjpy': 100, 'usdmxn': 10000, 'audusd': 10000}

    return pips_inst[inst]

def f_columns_datos(param_data):
    param_data['closetime'] = pd.to_datetime(param_data['closetime'])
    param_data['opentime'] = pd.to_datetime(param_data['opentime'])
    # Tiempo transcurrido de una operacion
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] - param_data.loc[i, 'opentime']).delta/1e9
                            for i in param_data.index]

    return param_data

def f_columns_pips(param_data):
    def pips_by_trade(trade):
        pips = 0
        if trade['type'] == "buy":
            pips = (trade['closeprice'] - trade['openprice']) * f_pip_size(trade['symbol'])
        else:
            pips = (trade['openprice'] - trade['closeprice']) * f_pip_size(trade['symbol'])
        return pips
    param_data['pips'] = list([pips_by_trade(param_data.iloc[i]) for i in range(len(param_data))])
    param_data['pips_acm'] = param_data['pips'].cumsum()
    param_data['profit_acm'] = param_data['profit'].cumsum()
    return param_data

def f_estadisticas_ba(param_data):
    # Creacion de las funciones y DataFrame para tabla estadística
    ops_totales = len(param_data)
    ganadoras = np.sum(param_data['profit'] > 0)
    ganadoras_c = (np.where(param_data['profit'] > 0, param_data['type'] == 'buy', 0).sum())
    ganadoras_v = (np.where(param_data['profit'] > 0, param_data['type'] == 'sell', 0).sum())
    perdedoras = np.sum(param_data['profit'] < 0)
    perdedoras_c = (np.where(param_data['profit'] < 0, param_data['type'] == 'buy', 0).sum())
    perdedoras_v = (np.where(param_data['profit'] < 0, param_data['type'] == 'sell', 0).sum())
    media_p = np.trunc(param_data['profit'].median())
    media_pips = np.trunc(param_data['pips'].median())
    r_efectividad = (ops_totales/ganadoras)
    r_proporcion = (ganadoras/perdedoras)
    r_efectividad_c = (ops_totales/ganadoras_c)
    r_efectividad_v = (ops_totales/ganadoras_v)
    pd_data = {'Medida': ['Ops Totales', 'Ganadoras', 'Ganadoras_c', 'Ganadoras_v', 'Perdedoras',
                               'Perdedoras_c', 'Perdedoras_v', 'Media(Profit)', 'Media(Pips)', 'r_efectividad',
                               'r_proporcion', 'r_efectividad_c', 'r_efectividad_v'],
               'Valor': [ops_totales, ganadoras, ganadoras_c, ganadoras_v, perdedoras, perdedoras_c, perdedoras_v,
                              media_p, media_pips, r_efectividad, r_proporcion, r_efectividad_c, r_efectividad_v],
               'Descripción': ['Operaciones totales', 'Operaciones ganadas', 'Operaciones ganadoras de compra',
                               'Operaciones ganadoras de venta', 'Operaciones perdedoras',
                               'Operaciones perdedoras de compra', 'Operaciones perdedoras de venta',
                               'Mediana de profit de operaciones', 'Mediana de pips de operaciones',
                               'Ganadoras Totales/Operaciones Totales', 'Perdedoras Totales/Ganadoras Totales',
                               'Ganadoras Compras/Operaciones Totales', 'Ganadoras Ventas/Operaciones Totales']}
    df_1_tabla = pd.DataFrame(pd_data)
    # Creacion de DataFrame para los rankings
    # Primero obtenemos un array que nos indique todos los tipos de instrumentos que tiene nuestro archivo
    instrumentos = np.unique(param_data['symbol'])
    # Después, indicamos que nuestra variable va a ser un DataFrame y vamos a rellenar los espacios
    df_1_ranking = pd.DataFrame(columns=['Symbol', 'Rank'], index=np.array([i for i in range(0, len(instrumentos))]))
    # Rellenamos la columna con los nombres de los simbolos
    df_1_ranking['Symbol'] = [instrumentos[i] for i in range(0, len(instrumentos))]
    # Ahora creamos los rankings
    i = 0
    for Symbol in instrumentos:
        Ops_ganadas= sum(1 for i in param_data.index if param_data.loc[i, 'profit'] >= 0
                      and param_data.loc[i, 'symbol'] == Symbol)
        Ops_totales = sum(1 for i in param_data.index if param_data.loc[i, 'symbol'] == Symbol)

        df_1_ranking.loc[i, 'Rank'] = str(np.round(Ops_ganadas / Ops_totales, 2)*100) + '%'
        i += 1

    # Creacion del diccionario
    dictionary = {'df_1_tabla': df_1_tabla, 'df_1_ranking': df_1_ranking}
    return dictionary

def f_estadisticas_mad(param_data):
    # Creamos una columna en el DataFrame que calcule el valor de la cuenta en cada movimiento iniciandola en 5000 y (+/-) el profit acumulado
    param_data['capital_acm'] = param_data['profit_acm']+5000
    return param_data