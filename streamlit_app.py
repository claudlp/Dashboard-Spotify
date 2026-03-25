import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import os

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Spotify",
    page_icon="🎵",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
    <style>
    .main {
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

# Cargar datos
@st.cache_data
def load_and_clean_data():
    """Cargar y limpiar los datos de Spotify"""
    file_path = "spotify_user_behavior_realistic_50000_rows.csv"
    
    # Cargar dataset
    df = pd.read_csv(file_path)
    
    # Renombrar columnas a español
    column_mapping = {
        'user_id': 'id_usuario',
        'country': 'pais',
        'age': 'edad',
        'signup_date': 'fecha_registro',
        'subscription_type': 'tipo_suscripcion',
        'subscription_status': 'estado_suscripcion',
        'months_inactive': 'meses_inactivo',
        'inactive_3_months_flag': 'bandera_inactivo_3_meses',
        'ad_interaction': 'interaccion_anuncio',
        'ad_conversion_to_subscription': 'conversion_anuncio_a_suscripcion',
        'music_suggestion_rating_1_to_5': 'calificacion_sugerencia_musica_1_a_5',
        'avg_listening_hours_per_week': 'horas_escucha_promedio_por_semana',
        'favorite_genre': 'genero_favorito',
        'most_liked_feature': 'caracteristica_mas_gustada',
        'desired_future_feature': 'caracteristica_futura_deseada',
        'primary_device': 'dispositivo_principal',
        'playlists_created': 'playlists_creadas',
        'avg_skips_per_day': 'saltos_promedio_por_dia'
    }
    df.rename(columns=column_mapping, inplace=True)
    
    # Rellenar valores nulos
    if 'horas_escucha_promedio_por_semana' in df.columns:
        df.loc[:, 'horas_escucha_promedio_por_semana'] = df['horas_escucha_promedio_por_semana'].fillna(
            df['horas_escucha_promedio_por_semana'].mean()
        )
    
    # Convertir fecha_registro a datetime
    df['fecha_registro'] = pd.to_datetime(df['fecha_registro'])
    
    # Eliminar duplicados
    df.drop_duplicates(subset=['id_usuario'], inplace=True)
    
    return df

# Cargar datos
df = load_and_clean_data()

# =======================
# HEADER
# =======================
col1, col2 = st.columns([1, 4])
with col1:
    st.image("https://img.icons8.com/color/96/000000/spotify.png", width=80)
with col2:
    st.title("🎵 Dashboard de Comportamiento de Usuarios Spotify")
    st.markdown("*Análisis y visualización del comportamiento e interacciones de usuarios*")

st.divider()

# =======================
# SIDEBAR - FILTROS
# =======================
st.sidebar.header("📊 Filtros")

# Filtro de país
paises = ['Todos'] + sorted(df['pais'].unique().tolist())
pais_seleccionado = st.sidebar.selectbox("País", paises)

# Filtro de tipo de suscripción
suscripciones = ['Todos'] + sorted(df['tipo_suscripcion'].unique().tolist())
suscripcion_seleccionada = st.sidebar.selectbox("Tipo de Suscripción", suscripciones)

# Filtro de rango de edad
edad_min, edad_max = st.sidebar.slider("Rango de Edad", 
                                        int(df['edad'].min()), 
                                        int(df['edad'].max()), 
                                        (int(df['edad'].min()), int(df['edad'].max())))

# Aplicar filtros
df_filtrado = df.copy()

if pais_seleccionado != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['pais'] == pais_seleccionado]

if suscripcion_seleccionada != 'Todos':
    df_filtrado = df_filtrado[df_filtrado['tipo_suscripcion'] == suscripcion_seleccionada]

df_filtrado = df_filtrado[(df_filtrado['edad'] >= edad_min) & (df_filtrado['edad'] <= edad_max)]

# =======================
# MÉTRICAS PRINCIPALES
# =======================
st.sidebar.divider()
st.sidebar.subheader("📈 Resumen de Datos")
st.sidebar.metric("Total de Usuarios", len(df_filtrado))
st.sidebar.metric("Usuarios Activos", (df_filtrado['estado_suscripcion'] == 'Active').sum())
st.sidebar.metric("Tasa de Conversión", 
                  f"{(df_filtrado['conversion_anuncio_a_suscripcion'] == 'Yes').sum() / len(df_filtrado) * 100:.1f}%")

# =======================
# MÉTRICAS KPI
# =======================
st.header("📊 Métricas Principales")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    usuarios_activos = (df_filtrado['estado_suscripcion'] == 'Active').sum()
    st.metric("Usuarios Activos", usuarios_activos)

with col2:
    edad_promedio = df_filtrado['edad'].mean()
    st.metric("Edad Promedio", f"{edad_promedio:.1f} años")

with col3:
    horas_promedio = df_filtrado['horas_escucha_promedio_por_semana'].mean()
    st.metric("Horas Escucha/Semana", f"{horas_promedio:.2f}h")

with col4:
    playlists_promedio = df_filtrado['playlists_creadas'].mean()
    st.metric("Playlists Promedio", f"{playlists_promedio:.1f}")

with col5:
    calificacion_promedio = df_filtrado['calificacion_sugerencia_musica_1_a_5'].mean()
    st.metric("Calificación Promedio", f"{calificacion_promedio:.2f}/5")

st.divider()

# =======================
# ROW 1: GRÁFICOS PRINCIPALES
# =======================
st.header("📈 Análisis Detallado")

col1, col2 = st.columns(2)

# Gráfico 1: Distribución por Tipo de Suscripción
with col1:
    st.subheader("Usuarios por Tipo de Suscripción")
    suscripcion_counts = df_filtrado['tipo_suscripcion'].value_counts()
    fig1 = px.pie(
        values=suscripcion_counts.values,
        names=suscripcion_counts.index,
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig1.update_layout(height=400)
    st.plotly_chart(fig1)

# Gráfico 2: Estado de Suscripción
with col2:
    st.subheader("Estado de Suscripción")
    estado_counts = df_filtrado['estado_suscripcion'].value_counts()
    colors_estado = ['#1DB954', '#FF6B6B']  # Verde Spotify, Rojo
    fig2 = px.bar(
        x=estado_counts.index,
        y=estado_counts.values,
        color=estado_counts.index,
        color_discrete_map={'Active': '#1DB954', 'Inactive': '#FF6B6B'},
        labels={'x': 'Estado', 'y': 'Cantidad'}
    )
    fig2.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig2)

# =======================
# ROW 2: ANÁLISIS DE COMPORTAMIENTO
# =======================
col1, col2 = st.columns(2)

# Gráfico 3: Distribución de Edad
with col1:
    st.subheader("Distribución de Edad")
    fig3 = px.histogram(
        df_filtrado,
        x='edad',
        nbins=30,
        color_discrete_sequence=['#1DB954']
    )
    fig3.update_layout(height=400, xaxis_title="Edad", yaxis_title="Cantidad de Usuarios")
    st.plotly_chart(fig3)

# Gráfico 4: Horas de Escucha por Semana
with col2:
    st.subheader("Horas de Escucha Promedio por Semana")
    fig4 = px.box(
        df_filtrado,
        y='horas_escucha_promedio_por_semana',
        color_discrete_sequence=['#1DB954']
    )
    fig4.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig4)

# =======================
# ROW 3: GÉNEROS Y DISPOSITIVOS
# =======================
col1, col2 = st.columns(2)

# Gráfico 5: Top Géneros Favoritos
with col1:
    st.subheader("Top 10 Géneros Favoritos")
    generos_top = df_filtrado['genero_favorito'].value_counts().head(10)
    fig5 = px.bar(
        x=generos_top.values,
        y=generos_top.index,
        orientation='h',
        color_discrete_sequence=['#1DB954']
    )
    fig5.update_layout(height=400, xaxis_title="Cantidad", yaxis_title="Género")
    st.plotly_chart(fig5)

# Gráfico 6: Dispositivos Principales
with col2:
    st.subheader("Dispositivos Principales Utilizados")
    dispositivos = df_filtrado['dispositivo_principal'].value_counts()
    fig6 = px.pie(
        values=dispositivos.values,
        names=dispositivos.index,
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig6.update_layout(height=400)
    st.plotly_chart(fig6)

# =======================
# ROW 4: INTERACCIONES Y CONVERSIONES
# =======================
col1, col2 = st.columns(2)

# Gráfico 7: Interacción con Anuncios vs Conversión
with col1:
    st.subheader("Interacción vs Conversión de Anuncios")
    interaction_conversion = pd.crosstab(
        df_filtrado['interaccion_anuncio'],
        df_filtrado['conversion_anuncio_a_suscripcion']
    )
    fig7 = px.bar(
        interaction_conversion,
        barmode='group',
        color_discrete_sequence=['#FF6B6B', '#1DB954']
    )
    fig7.update_layout(height=400, xaxis_title="Interacción", yaxis_title="Cantidad")
    st.plotly_chart(fig7)

# Gráfico 8: Calificación de Sugerencias Musicales
with col2:
    st.subheader("Distribución de Calificaciones (1-5)")
    calificaciones = df_filtrado['calificacion_sugerencia_musica_1_a_5'].value_counts().sort_index()
    fig8 = px.bar(
        x=calificaciones.index,
        y=calificaciones.values,
        color=calificaciones.index,
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={'x': 'Calificación', 'y': 'Cantidad'}
    )
    fig8.update_layout(height=400, showlegend=False)
    st.plotly_chart(fig8)

# =======================
# ROW 5: CARACTERÍSTICAS Y SALTOS
# =======================
col1, col2 = st.columns(2)

# Gráfico 9: Características más Gustadas
with col1:
    st.subheader("Top 8 Características Preferidas")
    caracteristicas = df_filtrado['caracteristica_mas_gustada'].value_counts().head(8)
    fig9 = px.bar(
        x=caracteristicas.values,
        y=caracteristicas.index,
        orientation='h',
        color_discrete_sequence=['#1DB954']
    )
    fig9.update_layout(height=400, xaxis_title="Cantidad")
    st.plotly_chart(fig9)

# Gráfico 10: Scatter - Horas Escucha vs Saltos
with col2:
    st.subheader("Horas de Escucha vs Saltos por Día")
    fig10 = px.scatter(
        df_filtrado.sample(min(1000, len(df_filtrado))),
        x='horas_escucha_promedio_por_semana',
        y='saltos_promedio_por_dia',
        color='calificacion_sugerencia_musica_1_a_5',
        size='playlists_creadas',
        hover_data=['edad', 'tipo_suscripcion'],
        color_continuous_scale='Viridis'
    )
    fig10.update_layout(height=400)
    st.plotly_chart(fig10)

# =======================
# ROW 6: TOP PAÍSES Y ESTADO INACTIVOS
# =======================
col1, col2 = st.columns(2)

# Gráfico 11: Top Países
with col1:
    st.subheader("Top 12 Países con más Usuarios")
    paises_top = df_filtrado['pais'].value_counts().head(12)
    fig11 = px.bar(
        x=paises_top.values,
        y=paises_top.index,
        orientation='h',
        color_discrete_sequence=['#1DB954']
    )
    fig11.update_layout(height=400, xaxis_title="Cantidad", yaxis_title="País")
    st.plotly_chart(fig11)

# Gráfico 12: Actividad por Meses Inactivos
with col2:
    st.subheader("Usuarios por Meses Inactivos")
    inactivos = df_filtrado['meses_inactivo'].value_counts().sort_index()
    fig12 = px.bar(
        x=inactivos.index,
        y=inactivos.values,
        color_discrete_sequence=['#FF6B6B'],
        labels={'x': 'Meses Inactivo', 'y': 'Cantidad'}
    )
    fig12.update_layout(height=400)
    st.plotly_chart(fig12)

st.divider()

# =======================
# TABLA DE DATOS
# =======================
st.header("🗂️ Datos Detallados")

col1, col2, col3 = st.columns(3)
with col1:
    filtro_estado = st.selectbox("Filtrar por Estado", ['Todos', 'Active', 'Inactive'], key='estado_tabla')
with col2:
    mostrar_registros = st.slider("Registros a mostrar", 5, 100, 20)
with col3:
    st.empty()

if filtro_estado != 'Todos':
    df_tabla = df_filtrado[df_filtrado['estado_suscripcion'] == filtro_estado].head(mostrar_registros)
else:
    df_tabla = df_filtrado.head(mostrar_registros)

st.dataframe(
    df_tabla.select_dtypes(include=['object', 'int64', 'float64']),
    height=400
)
