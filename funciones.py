# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: funciones.py - Funciones para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #
import pandas as pd
import numpy as np
from oandapyV20 import API                                # conexion con broker OANDA
import oandapyV20.endpoints.instruments as instruments    # informacion de precios historico
import pandas_datareader.data as web
from datetime import datetime
# ----------------- Funcion para mandar llamar archivo y acomodarlo a mi conveniencia--------------
# -- ------------------------------------------------------------------------------------ -- #
# -- Leer un archivo externo en Excel
def f_leer_archivo(param_archivo):
    '''
       Parameters
       ----------
       param_archivo : str : nombre de archivo a leer
       Returns
       -------
       df_data : pd.DataFrame : con informacion contenida en archivo leido
       Debugging
       ---------
       param_archivo = 'Statement_1.xlsx'
       '''
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

# -- ------------------------FUNCION: Pips por instrumento -------------------------------- #
# -- calcular el tamaño de los pips por instrumento
def f_pip_size(param_ins):
    """
         Parameters
         ----------
         param_ins : str : nombre de instrumento
         Returns
         -------
         Debugging
         -------
         param_ins = 'eurusd-2'
         """
    inst = param_ins
    # Lista de pips por instrumento
    pips_inst = {'usdjpy-2': 100, 'eurusd-2': 10000, 'eurcad-2': 10000, 'eurgbp-2': 10000, 'usdcad-2': 10000,
                 'audusd-2': 10000, 'audjpy-2': 100, 'gbpusd-2': 10000, 'eurjpy-2': 100, 'xauusd': 10000,
                 'eurjpy': 100, 'eurusd': 10000, 'gbpusd': 10000, 'btcusd': 10000, 'eurgbp': 10000,
                 'gbpjpy': 100, 'usdcad': 10000, 'usdjpy': 100, 'usdmxn': 10000, 'audusd': 10000}

    return pips_inst[inst]
# -- ------------------------------------ FUNCION: Columnas de transformaciones de tiempo ------------- #
# -- ------------------------------------------------------------------------------------ -- #
# -- calcular la diferencia entre el tiempo open y close

def f_columns_datos(param_data):
    """
        Parameters
        ----------
        :param param_data: dataframe conteniendo las columnas 'closetime' y 'opentime'
        Returns
        -------
        :return param_data: dataframe ingresado mas columna 'time' que es la diferencia entre close y open
        Debugging
        --------
        param_data = param_data
        """
    # Convertimos todas las fechas en que se abrió y cerró cada operación en el tipo datetime
    param_data['closetime'] = pd.to_datetime(param_data['closetime'])
    param_data['opentime'] = pd.to_datetime(param_data['opentime'])
    # Calculamos el tiempo transcurrido de una operacion
    param_data['tiempo'] = [(param_data.loc[i, 'closetime'] - param_data.loc[i, 'opentime']).delta/1e9
                            for i in param_data.index]

    return param_data
# -- -------------------------------------- FUNCION: Columnas de transformaciones de pips --------- #
# -- ------------------------------------------------------------------------------------ -- #
# -- calcular la cantidad de pips resultantes por cada operación

def f_columns_pips(param_data):
    """
        Parameters
        ----------
        param_data:  dataframe conteniendo las columnas 'closeprice' y 'openprice'
        Returns
        -------
        param_data:
        debugging
        ---------
        param_data = param_data
        """
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
# -- -------------------------------------------------------------- FUNCION: Diccionario de estadisticas -- #
# -- ------------------------------------------------------------------------------------ -- #
# -- Un diccionario, dos tablas
def f_estadisticas_ba(param_data):
    """
       Parameters
       ----------
       param_data: dataframe conteniendo las columnas 'profit', 'pips' y 'symbol'
       Returns
       -------
       """
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
# -- -------------------------------------------------------------- FUNCION: Tabla de profit diario -- #
# -- ------------------------------------------------------------------------------------ -- #
# -- ------------------------ Crear tabla con información de datos diarios --- -- #
# -- ------------------------ PARTE 3
def f_profit_diario(param_data):
    """
        Parameters
        ----------
        param_data:  Historico de operaciones
        Returns
        -------
        tabla con información diaria de los datos
        """
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
# -- ---------------------------------------------------- FUNCION: Estadisticas financieras -- #
# -- ------------------------------------------------------------------------------------ -- #
# -- Conjunto de diferentes medidas de atribucion al desempeño
# -- ---------------------------------------------------- FUNCION: Descargar precios de Oanda
def f_precios_masivos(p0_fini, p1_ffin, p2_gran, p3_inst, p4_oatk, p5_ginc):
    """
    Parameters
    ----------
    p0_fini
    p1_ffin
    p2_gran
    p3_inst
    p4_oatk
    p5_ginc
    Returns
    -------
    dc_precios
    Debugging
    ---------
    """

    def f_datetime_range_fx(p0_start, p1_end, p2_inc, p3_delta):
        """
        Parameters
        ----------
        p0_start
        p1_end
        p2_inc
        p3_delta
        Returns
        -------
        ls_resultado
        Debugging
        ---------
        """

        ls_result = []
        nxt = p0_start

        while nxt <= p1_end:
            ls_result.append(nxt)
            if p3_delta == 'minutes':
                nxt += timedelta(minutes=p2_inc)
            elif p3_delta == 'hours':
                nxt += timedelta(hours=p2_inc)
            elif p3_delta == 'days':
                nxt += timedelta(days=p2_inc)

        return ls_result

    # inicializar api de OANDA

    api = API(access_token=p4_oatk)

    gn = {'S30': 30, 'S10': 10, 'S5': 5, 'M1': 60, 'M5': 60 * 5, 'M15': 60 * 15,
          'M30': 60 * 30, 'H1': 60 * 60, 'H4': 60 * 60 * 4, 'H8': 60 * 60 * 8,
          'D': 60 * 60 * 24, 'W': 60 * 60 * 24 * 7, 'M': 60 * 60 * 24 * 7 * 4}

    # -- para el caso donde con 1 peticion se cubran las 2 fechas
    if int((p1_ffin - p0_fini).total_seconds() / gn[p2_gran]) < 4999:

        # Fecha inicial y fecha final
        f1 = p0_fini.strftime('%Y-%m-%dT%H:%M:%S')
        f2 = p1_ffin.strftime('%Y-%m-%dT%H:%M:%S')

        # Parametros pra la peticion de precios
        params = {"granularity": p2_gran, "price": "M", "dailyAlignment": 16, "from": f1,
                  "to": f2}

        # Ejecutar la peticion de precios
        a1_req1 = instruments.InstrumentsCandles(instrument=p3_inst, params=params)
        a1_hist = api.request(a1_req1)

        # Para debuging
        # print(f1 + ' y ' + f2)
        lista = list()

        # Acomodar las llaves
        for i in range(len(a1_hist['candles']) - 1):
            lista.append({'TimeStamp': a1_hist['candles'][i]['time'],
                          'Open': a1_hist['candles'][i]['mid']['o'],
                          'High': a1_hist['candles'][i]['mid']['h'],
                          'Low': a1_hist['candles'][i]['mid']['l'],
                          'Close': a1_hist['candles'][i]['mid']['c']})

        # Acomodar en un data frame
        r_df_final = pd.DataFrame(lista)
        r_df_final = r_df_final[['TimeStamp', 'Open', 'High', 'Low', 'Close']]
        r_df_final['TimeStamp'] = pd.to_datetime(r_df_final['TimeStamp'])

        return r_df_final

    # -- para el caso donde se construyen fechas secuenciales
    else:

        # hacer series de fechas e iteraciones para pedir todos los precios
        fechas = f_datetime_range_fx(p0_start=p0_fini, p1_end=p1_ffin, p2_inc=p5_ginc,
                                     p3_delta='minutes')

        # Lista para ir guardando los data frames
        lista_df = list()

        for n_fecha in range(0, len(fechas) - 1):

            # Fecha inicial y fecha final
            f1 = fechas[n_fecha].strftime('%Y-%m-%dT%H:%M:%S')
            f2 = fechas[n_fecha + 1].strftime('%Y-%m-%dT%H:%M:%S')

            # Parametros pra la peticion de precios
            params = {"granularity": p2_gran, "price": "M", "dailyAlignment": 16, "from": f1,
                      "to": f2}

            # Ejecutar la peticion de precios
            a1_req1 = instruments.InstrumentsCandles(instrument=p3_inst, params=params)
            a1_hist = api.request(a1_req1)

            # Para debuging
            print(f1 + ' y ' + f2)
            lista = list()

            # Acomodar las llaves
            for i in range(len(a1_hist['candles']) - 1):
                lista.append({'TimeStamp': a1_hist['candles'][i]['time'],
                              'Open': a1_hist['candles'][i]['mid']['o'],
                              'High': a1_hist['candles'][i]['mid']['h'],
                              'Low': a1_hist['candles'][i]['mid']['l'],
                              'Close': a1_hist['candles'][i]['mid']['c']})

            # Acomodar en un data frame
            pd_hist = pd.DataFrame(lista)
            pd_hist = pd_hist[['TimeStamp', 'Open', 'High', 'Low', 'Close']]
            pd_hist['TimeStamp'] = pd.to_datetime(pd_hist['TimeStamp'])

            # Ir guardando resultados en una lista
            lista_df.append(pd_hist)

        # Concatenar todas las listas
        r_df_final = pd.concat([lista_df[i] for i in range(0, len(lista_df))])

        # resetear index en dataframe resultante porque guarda los indices del dataframe pasado
        r_df_final = r_df_final.reset_index(drop=True)

        return r_df_final

def f_estadisticas_mad(param_data):
    """
       Parameters
       ----------
       param_data: Historico de operaciones, información diaria
       rf: tasa libre de riesgo
       mar: retorno esperado
       Returns
       -------
       df_mad: dataframe Medidas de Atribución al Desempeño
       """
    df = f_profit_diario(param_data)
    sell = param_data.loc[param_data['type'] == 'sell']
    buy = param_data.loc[param_data['type'] == 'buy']
    profit_v = f_profit_diario(sell)
    profit_c = f_profit_diario(buy)
    # Calculamos rendimientos logarítmicos del acumulado diario obtenido
    ren_log = np.log(df['profit_acm_d'] / df['profit_acm_d'].shift(1)).iloc[1:]
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
    # Calculamos el DrawDown del Capital en formato fecha inicial, valor, fecha final
    # Método obtenido de bibliografía consultada
    v_min = df.profit_acm_d.min()
    rel = df.loc[df['profit_acm_d'] == df.profit_acm_d.min()]
    index = rel.index.tolist()
    val = df.loc[0:index[0]]
    val_max = val.max()
    val_min = val.min()
    val_total = val_max['profit_acm_d'] - v_min
    drawdown_capi = list([val_min['timestamp'], val_max['timestamp'], val_total])
    val_2 = df.loc[index[0]:]
    val_max_2 = val_2.max()
    val_min_2 = val_2.min()
    val_total_2 = val_max_2['profit_acm_d'] - v_min
    drawup_capi = list([val_min_2['timestamp'], val_max_2['timestamp'], val_total_2])
    # Calculamos el information Ratio
    # Descarga precios  de Benchmark utilizando función vista en portafolios de inversión
   # def get_adj_closes(tickers, start_date=None, end_date=None):
        #closes = web.DataReader(name=tickers, data_source='yahoo', start=start_date, end=end_date)
        #closes = closes['Adj Close']
        # Ordenamos el indice de menor a mayor
        #closes.sort_index(inplace=True)
        #return closes
    # -- --------------------------------------------------------- Descargar precios de OANDA -- #

    # token de OANDA
    OA_Ak = 'db61d16ed80a943c9b65769aea7b75e8-dec8e1238889457a886b69e85640efec'
    OA_In = "SPX500_USD"  # Instrumento
    OA_Gn = "D"  # Granularidad de velas
    fini = pd.to_datetime(param_data['dates'].min()).tz_localize('GMT')  # Fecha inicial
    ffin = pd.to_datetime(param_data['dates'].max()).tz_localize('GMT')  # Fecha final

    df_pe = f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                              p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)

    #start = param_data['dates'].min()
    #end = param_data['dates'].max()
    #closes = get_adj_closes(tickers='^GSPC', start_date=start, end_date=end)
    # Utilizamos la información obtenida para obtener el information Ratio
    # Sacamos rendimientos de S&P y su promedio
    close = pd.DataFrame(float(i) for i in df_pe['Close'])
    r_sp = np.log(close / close.shift(1)).iloc[1:]
    rp_sp = r_sp.mean()
    # Eliminamos los trades realizados en domingo y sabado por que S&P solo opera de lunes a viernes
    df['weekday'] = '-'
    for i in range(len(df)):
        new_date = df['timestamp'][i]
        new_date = pd.to_datetime(new_date)
        df['weekday'][i] = new_date.weekday()
    df = df.loc[(df['weekday'] != 6) & (df['weekday'] != 5)]
    df = df.reset_index(drop=True)
    r_weekday = np.log(df['profit_acm_d'] / df['profit_acm_d'].shift(1)).iloc[1:]
    rp_weekday = r_weekday.mean()
    # Utilizamos rendimientos de la cuenta de históricos anteriormente calculados
    r_weekday_t = [str(i)[1:] for i in r_weekday]
    comp = [float(i) for i in r_weekday_t]
    for i in range(len(comp)):
        benchmark = comp[i] - r_sp
    benchmark = benchmark.std()
    info_ratio = (rp_weekday - rp_sp) / benchmark
    # Creamos DataFrame con la informacion y descripción
    mad_data = {'Metrica': ['Sharpe', 'Sortino_c', 'Sortino_v', 'Drawdown_capi', 'Drawup_capi', 'Information_r'],
                'Valor': [sharpe, sortino_c, sortino_v, drawdown_capi, drawup_capi, info_ratio],
                'Descripción': ['Sharpe Ratio', 'Sortino Ratio para posiciones de compra',
                                'Sortino Ratio para posiciones de venta', 'DrawDown de Capital', 'DrawUp de Capital',
                                'Information Ratio']}
    df_mad = pd.DataFrame(mad_data)
    return df_mad

# -- -------------------------- FUNCION: Disposition Effect - Sesgos cognitivos ------------ #
# -- ------------------------------------------------------------------------------------ -- #
# -- ------------------------ Presencia de sesgos cognitivos del trader ----------------- -- #
# -- ------------------------ PARTE 4

def f_be_de(param_data):
    """
    Parameters
    ----------
    param_data: Histórico de operaciones en el ejercicio
    Returns
    -------
    Diccionario con parámetros de estudio
    """

    # Siguiendo las recomendaciones del profesor calculamos el ratio de ganadoras y perdedoras respecto al capital
    # Trabajamos en el mismo DataFrame que contiene el histórico de operaciones
    param_data['ratio_capital_acm'] = 0
    param_data['ratio_capital_acm'] = [(param_data['profit'][i] / 5000) * 100 if i == 0 else
                                       (param_data['profit'][i] / param_data['capital_acm'][i - 1]) * 100
                                       for i in range(len(param_data))]

    # Separamos las operaciones en perdedoras y ganadoras en close y open respectivamente
    ganadoras = param_data[param_data['profit'] > 0]
    perdedoras = param_data[param_data['profit'] < 0]
    close_g = param_data[param_data['profit'] > 0]['closetime']
    close_p = param_data[param_data['profit'] < 0]['closetime']
    open_g = param_data[param_data['profit'] > 0]['opentime']
    open_p = param_data[param_data['profit'] < 0]['opentime']

    # Como sabemos que nuestra ancla van a ser las operaciones ganadoras las separamos del resto y creamos un DF
    # Pero primero reseteamos el índice para futuros problemas de indexación
    ganadoras.reset_index(inplace=True, drop=True)
    # Ahora encontramos las ocurrencias del sesgo en nuestra ancla
    param_data['opentime'] = param_data['opentime'].astype(str).str[0:10]
    ganadoras['opentime'] = ganadoras['opentime'].astype(str).str[0:10]
    ganadoras['closetime'] = ganadoras['closetime'].astype(str).str[0:10]
    oc = 0
    oc = [[param_data.iloc[i, :] for i in range(len(param_data)) if param_data['opentime'][i]
          < ganadoras['opentime'][j] and param_data['closetime'][i] > ganadoras['closetime'][j] or
          ganadoras['opentime'][j] < param_data['opentime'][i] < ganadoras['closetime'][j] <
          param_data['closetime'][i]] for j in range(len(ganadoras))]



    return oc