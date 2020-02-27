# -- ------------------------------------------------------------------------------------ -- #
# -- proyecto: Microestructura y Sistemas de Trading - Laboratorio 2 - Behavioral Finance
# -- archivo: principal.py - Codigo principal para el proyecto
# -- mantiene: Alejandra Cortes
# -- repositorio: https://github.com/alecortees22/LAB_2_ACS
# -- ------------------------------------------------------------------------------------ -- #

import funciones as fn
datos = fn.f_leer_archivo(param_archivo='Statement_1.xlsx')

pip_size = fn.f_pip_size(param_ins='eurusd')
