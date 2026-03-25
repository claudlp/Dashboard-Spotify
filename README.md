# 🧹 Limpiador de Datos CSV

# Proyecto: Análisis de Comportamiento de Usuarios de Spotify

Este proyecto contiene un análisis exploratorio de datos (EDA) y un dashboard interactivo de Streamlit para visualizar el comportamiento de los usuarios de Spotify.

## 📋 Tabla de Contenidos

- [Descripción del Proyecto](#-descripción-del-proyecto)
- [Configuración del Entorno](#-configuración-del-entorno)
- [Datos](#-datos)
- [Ejecución del Dashboard](#-ejecución-del-dashboard)

## 📝 Descripción del Proyecto

El objetivo de este proyecto es analizar el comportamiento de los usuarios de Spotify utilizando un dataset simulado. Se realizan diversas visualizaciones para entender patrones como la popularidad de los tipos de suscripción, la relación entre horas de escucha y la inactividad de los usuarios, los meses en los que los usuarios tienden a cancelar, los géneros musicales favoritos y las características más apreciadas de la plataforma. Finalmente, se despliega un dashboard interactivo utilizando Streamlit para una exploración más dinámica de los datos.

## 🛠️ Configuración del Entorno

Para ejecutar este proyecto, necesitarás tener Python y las siguientes librerías instaladas. Se recomienda usar un entorno virtual.

1.  **Clona este repositorio (si aplica) o descarga los archivos del proyecto.**

2.  **Instala las dependencias de Python:**
    Se ha generado un archivo `requirements.txt` con todas las librerías necesarias. Ejecuta el siguiente comando en tu terminal:
    ```bash
    pip install -r requirements.txt
    ```
    Las librerías incluyen `pandas`, `matplotlib`, `seaborn`, `streamlit`, `plotly`.

3.  **Para la ejecución en Google Colab:**
    Asegúrate de que `npx` (parte de Node.js) esté disponible para `localtunnel`. Colab generalmente ya lo tiene, pero si no, es posible que necesites instalar Node.js/npm.

## 📊 Datos

El análisis se basa en el archivo `spotify_user_behavior.csv`. Este dataset contiene información simulada sobre el comportamiento de los usuarios de Spotify, incluyendo:

-   `user_id`: Identificador único del usuario.
-   `country`: País del usuario.
-   `age`: Edad del usuario.
-   `signup_date`: Fecha de registro.
-   `subscription_type`: Tipo de suscripción (e.g., Premium Individual, Free).
-   `subscription_status`: Estado de la suscripción.
-   `months_inactive`: Meses que el usuario ha estado inactivo.
-   `inactive_3_months_flag`: Bandera si el usuario ha estado inactivo por más de 3 meses.
-   `ad_interaction`: Interacción con anuncios.
-   `ad_conversion_to_subscription`: Conversión de anuncio a suscripción.
-   `music_suggestion_rating_1_to_5`: Calificación de sugerencias musicales.
-   `avg_listening_hours_per_week`: Horas de escucha promedio por semana.
-   `favorite_genre`: Género musical favorito.
-   `most_liked_feature`: Característica más gustada de la plataforma.
-   `desired_future_feature`: Característica futura deseada.
-   `primary_device`: Dispositivo principal.
-   `playlists_created`: Número de playlists creadas.
-   `avg_skips_per_day`: Saltos promedio por día.

Asegúrate de que este archivo CSV esté en la misma ruta que el notebook de Colab o el script de Python cuando ejecutes el análisis.

## 🚀 Ejecución del Dashboard

El dashboard interactivo ha sido creado con Streamlit. Puedes ejecutarlo de la siguiente manera:

1.  Asegúrate de haber ejecutado las celdas de carga y limpieza de datos en el notebook de Colab, ya que el dashboard espera que el DataFrame `df` esté pre-cargado y limpio.

2.  Ejecuta el script `dashboard_spotify.py` usando `streamlit` y `localtunnel` para acceder a él a través de una URL pública (especialmente útil en entornos como Google Colab):
    ```bash
    streamlit run dashboard_spotify.py & npx localtunnel --port 8501
    ```
    Esto iniciará el servidor de Streamlit en el puerto 8501 y `localtunnel` generará una URL pública que podrás usar para acceder al dashboard desde tu navegador.

3.  Una vez que veas el mensaje `your url is: [una URL]` en la salida, abre esa URL en tu navegador.

4.  Para detener el dashboard y `localtunnel` en Colab, puedes usar los siguientes comandos en una nueva celda de código:
    ```python
    !pgrep -f "streamlit run dashboard_spotify.py" | xargs kill -9
    !pgrep -f "npx localtunnel --port 8501" | xargs kill -9
    print("Streamlit y localtunnel detenidos.")
    ```
    O simplemente reiniciar el entorno de ejecución de Colab (Entorno de ejecución -> Reiniciar entorno de ejecución...).
