# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - Funciones para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #
import pandas as pd

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
                 'audusd-2': 10000, 'audjpy-2': 100, 'gbpusd-2': 10000, 'eurjpy-2': 100}

    return pips_inst[inst]

def f_columns_datos(param_data):
    param_data['closetime'] = pd.to_datetime(param_data['closetime'])
    param_data['opentime'] = pd.to_datetime(param_data['opentime'])
    # Tiempo transcurrido de una operacion
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] - param_data.loc[i, 'opentime']).delta/1e9
                            for i in param_data.index]

    return param_data

def f_columns_pips(param_data):
    if param_data['type'] == 'buy':
        param_data['pips'] = [(param_data.loc[i, 'closeprice'] - param_data.loc[i, 'openprice'])*multiplicador
                              for i in param_data.index]
    else:
        param_data['pips'] = [(param_data.loc[i, 'openprice'] - param_data.loc[i, 'closeprice']) * multiplicador
                              for i in param_data.index]

    return 1