# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py - Codigo principal para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #

import funciones as fn
df_data = fn.f_leer_archivo(param_archivo='Statement_1.xlsx')

df_data = fn.f_pip_size(df_data)
#df_data = fn.f_columns_dats(df_data)

#tiempo = fn.f_columns_datos(param_data=)
