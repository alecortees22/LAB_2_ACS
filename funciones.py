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
    def pips_by_trade(trade):
        pips = 0
        if trade['type'] == "buy":
            pips = (trade['closeprice'] - trade['openprice']) * f_pip_size(trade['symbol'])
        else:
            pips = (trade['openprice'] - trade['closeprice']) * f_pip_size(trade['symbol'])
        return pips
    param_data['pips'] = list([pips_by_trade(param_data.iloc[i]) for i in range(len(param_data))])
    return param_data

def f_estadisticas_ba(param_data):
    ops_totales = len(param_data)
    ganadoras = np.sum(param_data['profit'] > 0)
    ganadoras_c = (np.where(param_data['profit'] > 0, param_data['type'] == 'buy', 0).sum())
    ganadoras_v = (np.where(param_data['profit'] > 0, param_data['type'] == 'sell', 0).sum())
    perdedoras = np.sum(param_data['profit'] < 0)
    perdedoras_c = (np.where(param_data['profit'] < 0, param_data['type'] == 'buy', 0).sum())
    perdedoras_v = (np.where(param_data['profit'] < 0, param_data['type'] == 'sell', 0).sum())
    media_p = param_data['profit'].median()
    media_pips = param_data['pips'].median()

    return media_pips