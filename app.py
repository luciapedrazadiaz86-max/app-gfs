import streamlit as st
import xarray as xr
from pathlib import Path
import matplotlib.pyplot as plt
st.set_page_config(layout='wide')



@st.cache_resource
def cargar():
    return xr.open_dataset('gfs_recorte.nc')

ds = cargar()

st.title('Condiciones iniciales del GFS')
st.write('Explora las variables del archivo gfs_data.nc')
#st.write(ds)

st.header('Temperatura a lo largo de una columna de la malla')

# Elegir el nivel
nivel = st.slider('Nivel', 1, 64, value = 10, step = 1) # paso default = 1

t = ds['t'].sel(lon=100, lev = nivel)

lat = t['geolat'] # igual que t_10.geolat # las latitudes son iguales en cada nivel vertical, son angulos

fig, ax = plt.subplots(figsize=(2, 2))
ax.plot(t, lat, linewidth = .5)
ax.set_xlabel('Temperatura (K)')
ax.set_ylabel('Latitud')
ax.set_title(f'Nivel {nivel}')
st.pyplot(fig,width='content') # mostrar tamaño sin estirar

st.divider()
# ===================
# perfil vertical
st.header('Perfil vertical en un punto')

i = st.slider('Fila de la malla', 0, 239, value = 100)
j = st.slider('Columna de la malla', min_value = 0, max_value = 239, value=100)

# seleccionar datos en el punto i,j

# sin la capa extra de arriba
#t = ds['t'].sel(lat=i, lon=j, lev=slice(1, 65))

# seleccionamos una variable
variable = st.selectbox('Variable', ['t', 'sphum', 'o3mr'])
perfil = ds[variable].sel(lat=i, lon=j, lev=slice(1, 65))

zh = ds['zh'].isel(lat=i, lon=j)  # 66 interfaces de arriba hacia abajo
techo = zh.sel(levp=slice(1, 65))  
piso = zh.sel(levp=slice(2, 66))  
z = (techo + piso) / 2 / 1000  
# operación vectorizada
# z[0] = (techo[0] + piso[0]) / 2 / 1000      # frontera 1 con frontera 2
# z[1] = (techo[1] + piso[1]) / 2 / 1000      # frontera 2 con frontera 3
lat = ds['geolat'].sel(lat=i, lon=j).values
lon = ds['geolon'].sel(lat=i, lon=j).values

# Graficar
col1, col2, col3 = st.columns(3)

with col1:
    fig, ax = plt.subplots(figsize=(3, 3))
    ax.plot(perfil, z)
    ax.set_xlabel(f"{variable} ")
    ax.set_ylabel('Altura (km)')
    ax.set_title(f'Latitud {lat:.1f}, longitud {lon:.1f}')
    ax.grid(alpha=0.3)
    st.pyplot(fig)

with col2:
    fig2, ax2 = plt.subplots(figsize=(4, 4))
    ds['t'].sel(lev=-1).plot(ax=ax2, x='geolon', y='geolat')
    ax2.plot(lon, lat, '*', color='black', markersize=15)
    ax2.set_title('Punto elegido')
    st.pyplot(fig2)


with col3:
    fig3, ax3 = plt.subplots(figsize=(4, 4))
    ds['t'].sel(lev=64).plot(ax=ax3)
    ax3.plot(j,i, '*', color='red', markersize=15)
    ax3.set_xlabel('Columna de la malla')
    ax3.set_ylabel('Fila de la malla')
    ax3.grid(True, color='white', alpha=0.5)
    ax3.invert_yaxis()
    ax3.invert_xaxis()
    ax3.set_xticks(range(0, 240, 20))
    ax3.set_yticks(range(0, 240, 20))
    ax3.tick_params(axis='x', labelsize=4)
    st.pyplot(fig3)


st.divider()
#===============

st.header('Mapa de un nivel sobre México')

# Rectángulo que cubre México (en este archivo, la longitud va de 0 a 360)
mexico = ((ds['geolat'] >= 14) & (ds['geolat'] <= 33) &
          (ds['geolon'] >= 242) & (ds['geolon'] <= 274))

variable_mapa = st.selectbox('Variable del mapa', ['t', 'sphum', 'o3mr'])
nivel_mapa = st.slider('Nivel del mapa', min_value=1, max_value=64, value=64)
mapa_color = st.selectbox('Mapa de colores', ['viridis', 'magma', 'RdBu_r'])

campo = ds[variable_mapa].sel(lev=nivel_mapa).where(mexico, drop=True) # nuevo

fila_col1, fila_col2, fila_col3 = st.columns(3)

with fila_col1:
    fig4, ax4 = plt.subplots(figsize=(4, 4))
    campo.plot(ax=ax4, x='geolon', y='geolat', cmap=mapa_color)
    ax4.set_title(f'{variable_mapa}, nivel {nivel_mapa}')
    st.pyplot(fig4)

with fila_col2:
    fig5, ax5 = plt.subplots(figsize=(4, 4))
    campo.plot.hist(ax=ax5, bins=50)
    ax5.set_xlabel(variable_mapa)
    ax5.set_ylabel('Número de celdas')
    ax5.set_title(f'{variable_mapa}, nivel {nivel_mapa}')
    st.pyplot(fig5)

with fila_col3:
    st.metric('Mínimo', f'{campo.min().values:.3g}')
    st.metric('Máximo', f'{campo.max().values:.3g}')
    st.metric('Promedio', f'{campo.mean().values:.3g}')
