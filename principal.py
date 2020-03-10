# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py - Codigo principal para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #

import funciones as fn
import pandas as pd
df_data = fn.f_leer_archivo(param_archivo='Statement_1.xlsx')
time = fn.f_columns_datos(df_data)
pips = fn.f_columns_pips(df_data)

