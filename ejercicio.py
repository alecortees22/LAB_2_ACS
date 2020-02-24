# -- ------------------------------------------------------------------------------------ -- #
# -- Proyecto: Describir brevemente el proyecto en general                                -- #
# -- Codigo: RepasoPython.py - describir brevemente el codigo                             -- #
# -- Repositorio: https://github.com/                                                     -- #
# -- Autor: Nombre de autor                                                               -- #
# -- ------------------------------------------------------------------------------------ -- #

# -- ------------------------------------------------------------- Importar con funciones -- #
import funciones as fn
import visualizaciones as vs

import pandas as pd
import numpy as np
# -- --------------------------------------------------------- Descargar precios de OANDA -- #

# token de OANDA
OA_Ak = 'db61d16ed80a943c9b65769aea7b75e8-dec8e1238889457a886b69e85640efec'
OA_In = "EUR_USD"  # Instrumento
OA_Gn = "D"  # Granularidad de velas
fini = pd.to_datetime("2019-01-06 00:00:00").tz_localize('GMT')  # Fecha inicial
ffin = pd.to_datetime("2019-12-06 00:00:00").tz_localize('GMT')  # Fecha final

df_pe = fn.f_precios_masivos(p0_fini=fini, p1_ffin=ffin, p2_gran=OA_Gn,
                             p3_inst=OA_In, p4_oatk=OA_Ak, p5_ginc=4900)

# -- --------------------------------------------------------------- Graficar OHLC plotly -- #

vs_grafica1 = vs.g_velas(p0_de=df_pe.iloc[0:120, :])
vs_grafica1.show()

# -- ------------------------------------------------------------------- Conteno de velas -- #

df_pe['hora'] = list(df_pe['TimeStamp'][i].hour for i in range(0, len(df_pe['TimeStamp'])))  # nueva columna de hora
df_pe['dia'] = list(df_pe['TimeStamp'][i].weekday() for i in range(0, len(df_pe['TimeStamp'])))
closes = pd.DataFrame(float(i) for i in df_pe['Close'])
opens = pd.DataFrame(float(i) for i in df_pe['Open'])
df_pe['close-open'] = closes-opens
# -- ------------------------------------------------------------ Graficar Boxplot plotly -- #
vs_grafica2 = vs.g_boxplot_varios(p0_data=df_pe[['co']], p1_norm=False)
vs_grafica2.show()
df_pe['mes'] = pd.DataFrame(i.month for i in df_pe['TimeStamp'])
df_pe['oc'] = (closes-opens)*10000
high = pd.DataFrame(float(i) for i in df_pe['High'])
low = pd.DataFrame(float(i) for i in df_pe['Low'])
df_pe['hl'] = (high-low)*10000
sentido = lambda opens, closes: 'Alcista' if closes>=opens else 'Bajista'
df_pe['sentido'] = pd.DataFrame(sentido(df_pe['Open'][i],df_pe['Close'][i]) for i in range(len(df_pe['Open'])))
#s_as = np.array([22, 23, 0, 1, 2, 3, 4, 5, 6, 7])
#s_as_eu = np.array([8])
#s_eu = np.array([9, 10, 11, 12])
#s_eu_am = np.array([13, 14, 15, 16])
#s_am = np.array([17, 18, 19, 20, 21])
#ss = df_pe['Hora'][i]
#df_pe['Sesion'] = pd.DataFrame(
#for i in df_pe['Hora']:
    #if ss[i] == 21:
        #print('America')
    #else:
        #print('None')
