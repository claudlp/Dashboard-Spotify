import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)
plt.rcParams['font.size'] = 12
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

st.set_page_config(page_title='Spotify User Behavior Dashboard', layout='wide')

st.title('Spotify User Behavior Dashboard')
st.markdown('Visualiza y explora métricas de comportamiento de usuarios de Spotify. Usa los filtros en la barra lateral para análisis interactivo.')

DATA_FILE = 'spotify_user_behavior.csv'

COLUMN_MAPPING = {
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

@st.cache_data
def load_and_clean_data(filepath: str) -> pd.DataFrame:
    path = Path(filepath)
    if not path.exists():
        return pd.DataFrame()

    df = pd.read_csv(path)
    df.rename(columns=COLUMN_MAPPING, inplace=True)

    # Fecha
    if 'fecha_registro' in df.columns:
        df['fecha_registro'] = pd.to_datetime(df['fecha_registro'], errors='coerce')

    # Rellenar nulos en horas de escucha
    if 'horas_escucha_promedio_por_semana' in df.columns:
        df['horas_escucha_promedio_por_semana'] = pd.to_numeric(df['horas_escucha_promedio_por_semana'], errors='coerce')
        if df['horas_escucha_promedio_por_semana'].isnull().any():
            df['horas_escucha_promedio_por_semana'].fillna(df['horas_escucha_promedio_por_semana'].mean(), inplace=True)

    # Eliminar duplicados de usuarios
    if 'id_usuario' in df.columns:
        df.drop_duplicates(subset=['id_usuario'], inplace=True)

    # Forzar tipos
    if 'meses_inactivo' in df.columns:
        df['meses_inactivo'] = pd.to_numeric(df['meses_inactivo'], errors='coerce').fillna(0).astype(int)

    if 'bandera_inactivo_3_meses' in df.columns:
        df['bandera_inactivo_3_meses'] = pd.to_numeric(df['bandera_inactivo_3_meses'], errors='coerce').fillna(0).astype(int)

    return df


def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    sidebar = st.sidebar
    sidebar.header('Filtros')

    if 'pais' in df.columns:
        paises = sorted(df['pais'].dropna().unique().tolist())
        pais_selected = sidebar.multiselect('País', ['Todos'] + paises, default=['Todos'])
        if 'Todos' not in pais_selected and pais_selected:
            df = df[df['pais'].isin(pais_selected)]

    if 'tipo_suscripcion' in df.columns:
        tipos = sorted(df['tipo_suscripcion'].dropna().unique().tolist())
        suscripciones = sidebar.multiselect('Tipo de suscripción', ['Todos'] + tipos, default=['Todos'])
        if 'Todos' not in suscripciones and suscripciones:
            df = df[df['tipo_suscripcion'].isin(suscripciones)]

    if 'edad' in df.columns:
        edadmin = int(df['edad'].min()) if not df['edad'].dropna().empty else 0
        edadmax = int(df['edad'].max()) if not df['edad'].dropna().empty else 100
        edad_rango = sidebar.slider('Rango de edad', edadmin, edadmax, (edadmin, edadmax))
        df = df[df['edad'].between(edad_rango[0], edad_rango[1], inclusive='both')]

    if 'bandera_inactivo_3_meses' in df.columns:
        churn_filter = sidebar.selectbox('Estado churn', ['Todos', 'Activo (<3m inactivo)', 'Inactivo (≥3m inactivo)'])
        if churn_filter == 'Activo (<3m inactivo)':
            df = df[df['bandera_inactivo_3_meses'] == 0]
        elif churn_filter == 'Inactivo (≥3m inactivo)':
            df = df[df['bandera_inactivo_3_meses'] == 1]

    return df


def plot_pie_subscription(df: pd.DataFrame):
    if 'tipo_suscripcion' not in df.columns or df['tipo_suscripcion'].dropna().empty:
        st.warning('No hay datos de tipo de suscripción para graficar.')
        return

    counts = df['tipo_suscripcion'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=90, colors=sns.color_palette('viridis', len(counts)))
    ax.axis('equal')
    ax.set_title('Distribución de Tipos de Suscripción')
    st.pyplot(fig)


def plot_scatter_listening_vs_inactive(df: pd.DataFrame):
    if not all(col in df.columns for col in ['horas_escucha_promedio_por_semana', 'meses_inactivo', 'bandera_inactivo_3_meses']):
        st.warning('Faltan columnas para el gráfico de dispersión.')
        return

    df = df.copy()
    df['estado_churn'] = df['bandera_inactivo_3_meses'].apply(lambda x: 'Inactivo (+3 meses)' if x == 1 else 'Activo / Inactivo (<3 meses)')

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot(
        data=df,
        x='horas_escucha_promedio_por_semana',
        y='meses_inactivo',
        hue='estado_churn',
        palette={'Activo / Inactivo (<3 meses)': 'green', 'Inactivo (+3 meses)': 'red'},
        alpha=0.6,
        s=50,
        ax=ax
    )
    ax.set_title('Horas de Escucha vs Meses de Inactividad por Estado de Churn')
    ax.set_xlabel('Horas de Escucha Promedio por Semana')
    ax.set_ylabel('Meses Inactivo')
    ax.grid(True, linestyle='--', alpha=0.7)
    st.pyplot(fig)


def plot_hist_inactive_months(df: pd.DataFrame):
    if 'meses_inactivo' not in df.columns:
        st.warning('No hay datos de meses inactivo para el histograma.')
        return

    churned = df[df['meses_inactivo'] > 0]
    if churned.empty:
        st.warning('No hay usuarios inactivos (meses_inactivo > 0) para analizar.')
        return

    max_month = int(churned['meses_inactivo'].max())
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(churned['meses_inactivo'], bins=range(1, max_month + 2), kde=False, color='darkorange', ax=ax)
    ax.set_title('Distribución de Meses Inactivo (para Usuarios Inactivos)')
    ax.set_xlabel('Meses Inactivo')
    ax.set_ylabel('Número de Usuarios')
    ax.set_xticks(range(1, max_month + 1))
    st.pyplot(fig)


def plot_top_bars(df: pd.DataFrame, column: str, title: str):
    if column not in df.columns or df[column].dropna().empty:
        st.warning(f'No hay datos en {column} para graficar.')
        return

    top_values = df[column].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=top_values.values, y=top_values.index, palette='magma', ax=ax)
    ax.set_title(title)
    ax.set_xlabel('Número de Usuarios')
    ax.set_ylabel('')
    st.pyplot(fig)


# Carga de datos

with st.spinner('Cargando y limpiando datos...'):
    df = load_and_clean_data(DATA_FILE)

if df.empty:
    st.error(f'No se puede cargar el archivo {DATA_FILE}. Asegúrate de que exista y tenga datos correctos.')
    st.stop()

# Filtrado

df_filtrado = apply_filters(df)

# Visibilidad del dataset
st.subheader('Dataset filtrado')
st.dataframe(df_filtrado.reset_index(drop=True))

# KPI

col1, col2, col3, col4, col5 = st.columns(5)

n_usuarios = len(df_filtrado)
media_horas = (df_filtrado['horas_escucha_promedio_por_semana'].mean() if 'horas_escucha_promedio_por_semana' in df_filtrado.columns else 0)
usuarios_inactivos = df_filtrado['meses_inactivo'][df_filtrado['meses_inactivo'] > 0].count() if 'meses_inactivo' in df_filtrado.columns else 0
usuarios_activos = n_usuarios - usuarios_inactivos
porcentaje_churn = (usuarios_inactivos / n_usuarios * 100) if n_usuarios > 0 else 0

col1.metric('Total usuarios', f'{n_usuarios:,}')
col2.metric('Horas escucha promedio / sem', f'{media_horas:.2f}')
col3.metric('Usuarios activos', f'{usuarios_activos:,}')
col4.metric('Usuarios inactivos', f'{usuarios_inactivos:,}')
col5.metric('Tasa churn (%)', f'{porcentaje_churn:.1f}%')

st.markdown('---')

# Gráficos

st.subheader('Distribución de Suscripciones')
plot_pie_subscription(df_filtrado)

st.subheader('Horas de escucha vs Inactividad')
plot_scatter_listening_vs_inactive(df_filtrado)

st.subheader('Histograma de Meses Inactivo')
plot_hist_inactive_months(df_filtrado)

st.subheader('Top géneros favoritos')
plot_top_bars(df_filtrado, 'genero_favorito', 'Top 10 Géneros Musicales Favoritos')

st.subheader('Top características más gustadas')
plot_top_bars(df_filtrado, 'caracteristica_mas_gustada', 'Top 10 Características Más Gustadas')

st.sidebar.markdown('---')
st.sidebar.write('Dashboard creado para visualización interactiva con Streamlit.')
