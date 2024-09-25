
import numpy as np
import pandas as pd
import sqlite3 as sql
import plotly.graph_objs as go ### para gráficos
import plotly.express as px
import a_funciones as fn

conn = sql.connect('data/db_movies')
cur = conn.cursor()