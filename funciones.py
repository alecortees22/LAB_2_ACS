# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - Funciones para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #
import pandas as pd
import numpy as np
from datetime import datetime
# ----------------- Funcion para mandar llamar archivo y acomodarlo a mi conveniencia--------------
def f_leer_archivo(param_archivo):
    param_archivo = 'archivo_profe.xlsx'
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
    # Convertimos todas las fechas en que se abrió y cerró cada operación en el tipo datetime
    param_data['closetime'] = pd.to_datetime(param_data['closetime'])
    param_data['opentime'] = pd.to_datetime(param_data['opentime'])
    # Calculamos el tiempo transcurrido de una operacion
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] - param_data.loc[i, 'opentime']).delta/1e9
                            for i in param_data.index]

    return param_data

def f_columns_pips(param_data):
    # Obtenemos la función para calcular el total de pips en cada operación dependiendo de la posición tomada
    def pips_by_trade(trade):
        pips = 0
        if trade['type'] == "buy":
            pips = (trade['closeprice'] - trade['openprice']) * f_pip_size(trade['symbol'])
        else:
            pips = (trade['openprice'] - trade['closeprice']) * f_pip_size(trade['symbol'])
        return pips
    # Agreamos una columna con el total de pips calculados
    param_data['pips'] = list([pips_by_trade(param_data.iloc[i]) for i in range(len(param_data))])
    # Obtenemos una suma acumulativa de estos pips obtenidos y los agregamos a una columna nueva
    param_data['pips_acm'] = param_data['pips'].cumsum()
    #Obtenemos la suma acumulativa de los profits obtenidos en cada operación y agregamos a una nueva columna
    param_data['profit_acm'] = param_data['profit'].cumsum()
    return param_data

def f_estadisticas_ba(param_data):
    # Creacion de las funciones y DataFrame para tabla estadística
    # Primero obtenemos todas las operaciones y los cálculos necesarios para obtenerlas
    ops_totales = len(param_data)
    # Dividimos las operaciones en ganadoras, ganadoras de compra, de venta
    ganadoras = np.sum(param_data['profit'] > 0)
    ganadoras_c = (np.where(param_data['profit'] > 0, param_data['type'] == 'buy', 0).sum())
    ganadoras_v = (np.where(param_data['profit'] > 0, param_data['type'] == 'sell', 0).sum())
    # Misma división aplicada para las operaciones de pérdida
    perdedoras = np.sum(param_data['profit'] < 0)
    perdedoras_c = (np.where(param_data['profit'] < 0, param_data['type'] == 'buy', 0).sum())
    perdedoras_v = (np.where(param_data['profit'] < 0, param_data['type'] == 'sell', 0).sum())
    # Obtenemos la mediana de profit y de pips para obtener estádistica básica
    media_p = np.trunc(param_data['profit'].median())
    media_pips = np.trunc(param_data['pips'].median())
    # sacamos ratios que nos dan distinta información de los datos presentados
    r_efectividad = (ops_totales/ganadoras)
    r_proporcion = (ganadoras/perdedoras)
    r_efectividad_c = (ops_totales/ganadoras_c)
    r_efectividad_v = (ops_totales/ganadoras_v)
    # por último acomodamos la información obtenida en un DataFrame
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
# Parte 3)
def f_profit_diario(param_data):
    # Creamos una columna en el DataFrame que calcule el valor de la cuenta en cada movimiento iniciandola en 5000 y (+/-) el profit acumulado
    param_data['capital_acm'] = param_data['profit_acm']+5000
    ###############################################################
    # Para la obtención de información diaria tenemos que comparar la suma obtenida en cada día de cierre de operación
    # contra un rango de fechas iniciado en el primer trade y cerrado en el último día de cierre de operación
    param_data['dates'] = list(param_data['closetime'].astype(str).str[0:10])
    # Ordenamos nuestro DataFrame según la fecha de cierre y volvemos a acomodar el índice
    param_data.sort_values(by='closetime', inplace=True, ascending=True)
    param_data.reset_index(inplace=True, drop=True)
    start = str(param_data['closetime'].min())[0:10]
    end = str(param_data['closetime'].max())[0:10]
    total_days = pd.date_range(start=start, end=end, freq='D')
    param_data['closetime'] = list([str(i)[0:10] for i in param_data['closetime']])
    # Creamos el DataFrame que nos permita observar la información diaria y la evolución del capital en el tiempo
    df = pd.DataFrame()
    df['timestamp'] = list(str(i)[0:10] for i in total_days)
    df['profit_d'] = 0
    profit_d = param_data.groupby('closetime')['profit'].sum()
    for i in range(len(df)):
        for j in range(len(profit_d)):
            if df['timestamp'][i] == profit_d.index[j]:
                df['profit_d'][i] = float(profit_d[j])
    # Calculamos el comportamiento del capital obtenido en cada día de operación y los días de no operación dentro de ese rango de fechas
    df['profit_acm_d'] = df['profit_d'].cumsum()+5000
    return df

def f_estadisticas_mad(param_data):
    df = f_profit_diario(param_data)
    sell = param_data.loc[param_data['type'] == 'sell']
    buy = param_data.loc[param_data['type'] == 'buy']
    profit_v = f_profit_diario(sell)
    profit_c = f_profit_diario(buy)
    # Calculamos rendimientos logarítmicos del acumulado diario obtenido
    ren_log = np.log(df['profit_acm_d'] / df['profit_acm_d'].shift(1))
    # Calculamos rendimientos logaritmicos de venta y de compra
    ren_log_v = np.log(profit_v['profit_acm_d'] / profit_v['profit_acm_d'].shift(1))
    ren_log_c = np.log(profit_c['profit_acm_d'] / profit_c['profit_acm_d'].shift(1))
    # Sacamos el promedio de esos logaritmos calculados
    rp = np.mean(ren_log)
    rp_v = np.mean(ren_log_v)
    rp_c = np.mean(ren_log_c)
    # Sacamos la desviación estándar de los rendimientos
    sdp = ren_log.std()
    # Volvemos diaria la rf (8%) (utilizamos 300 dias)
    rf = .08 / 300
    # Volvemos diario el mar (30%)
    mar = .3/300
    # Sacamos los valores de los rendimientos por debajo de mar segun corresponda
    tdd_v = ren_log_v[ren_log_v <= mar]
    tdd_c = ren_log_c[ren_log_c <= mar]
    # Calculamos un nuevo profit_acm_d para compra
    # Calculamos Sharpe Ratio
    sharpe = (rp - rf) / sdp
    #  Calculamos sortino ratio para compra
    sortino_c = (rp_c-mar)/(tdd_c.std())
    # Calculamos sortino ratio para venta
    sortino_v = (rp_v-mar)/(tdd_v.std())


    # Creamos DataFrame con la informacion y descripción
    mad_data = {'Metrica': ['Sharpe', 'Sortino_c', 'Sortino_v'],
                'Valor': [sharpe, sortino_c, sortino_v],
                'Descripción': ['Sharpe Ratio', 'Sortino Ratio para posiciones de compra',
                                'Sortino Ratio para posiciones de venta']}
    df_mad = pd.DataFrame(mad_data)
    return df_mad

