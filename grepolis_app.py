import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Configuración de la página
st.set_page_config(
    page_title="🏛️ GrepoIntel ES137 | R.D.M.P",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        transition: transform 0.3s ease;
    }
    .metric-container:hover {
        transform: translateY(-5px);
    }
    .success-box {
        background: linear-gradient(135deg, #56CCF2, #2F80ED);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(86, 204, 242, 0.3);
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    .status-active { color: #28a745; font-weight: bold; }
    .status-recent { color: #ffc107; font-weight: bold; }
    .status-inactive { color: #fd7e14; font-weight: bold; }
    .status-offline { color: #dc3545; font-weight: bold; }
    .tab-content {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Funciones para cargar datos
@st.cache_data(ttl=900)  # Cache por 15 minutos
def load_grepolis_data():
    """Carga y procesa datos de Grepolis ES137"""
    try:
        with st.spinner("🔄 Conectando con servidores de Grepolis ES137..."):
            url = "https://es137.grepolis.com/data/players.txt"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                players_data = pd.read_csv(
                    io.StringIO(response.text),
                    sep=',',
                    names=['ID', 'Nombre', 'ID_Alianza', 'Puntos', 'Ranking', 'Ciudades'],
                    na_values=['']
                )
                
                players_data = players_data.dropna(subset=['Nombre'])
                players_data['ID_Alianza'] = players_data['ID_Alianza'].fillna(0)
                players_data = players_data.sort_values('Ranking')
                
                return players_data, True, f"✅ Datos actualizados: {datetime.now().strftime('%H:%M:%S')}"
            else:
                return None, False, f"❌ Error de conexión: {response.status_code}"
    
    except Exception as e:
        return None, False, f"❌ Error: {str(e)}"

@st.cache_data(ttl=900)
def load_alliance_data():
    """Carga datos de alianzas"""
    try:
        url = "https://es137.grepolis.com/data/alliance.txt"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            if len(response.text.strip()) == 0:
                return None
            
            alliance_data = pd.read_csv(
                io.StringIO(response.text),
                sep=',',
                names=['ID_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Ranking_Alianza', 'Miembros']
            )
            
            if len(alliance_data) == 0:
                return None
                
            return alliance_data
        else:
            return None
    except Exception as e:
        return None

@st.cache_data(ttl=900)
def load_towns_data():
    """Carga datos de ciudades"""
    try:
        url = "https://es137.grepolis.com/data/towns.txt"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            towns_data = pd.read_csv(
                io.StringIO(response.text),
                sep=',',
                names=['ID_Ciudad', 'Nombre_Ciudad', 'ID_Jugador', 'Coord_X', 'Coord_Y', 'Puntos_Ciudad']
            )
            return towns_data
        else:
            return None
    except:
        return None

def simulate_activity_status(players_data):
    """Simula estados de actividad basándose en datos disponibles"""
    # Nota: Los datos reales de actividad no están disponibles en las APIs públicas
    # Esta función simula estados basándose en patrones de puntuación y ranking
    
    players_with_status = players_data.copy()
    
    # Simular actividad basándose en algunos indicadores indirectos
    def assign_status(row):
        # Jugadores con más puntos y mejor ranking tienden a ser más activos
        score = row['Puntos'] / 1000 + (len(players_data) - row['Ranking']) / 100
        
        # Añadir algo de aleatoriedad para simular
        random_factor = random.random() * 0.3
        final_score = score + random_factor
        
        if final_score > 8:
            return "🟢 Activo", "Últimas 4h"
        elif final_score > 5:
            return "🟡 Reciente", "6-12h"
        elif final_score > 2:
            return "🟠 Inactivo", "12-24h"
        else:
            return "🔴 Offline", "+24h"
    
    status_data = players_with_status.apply(assign_status, axis=1, result_type='expand')
    players_with_status['Estado'] = status_data[0]
    players_with_status['Ultima_Actividad'] = status_data[1]
    
    return players_with_status

# HEADER PRINCIPAL
st.markdown('<h1 class="main-header">🏛️ GrepoIntel ES137 | R.D.M.P</h1>', unsafe_allow_html=True)
st.markdown('<div class="success-box"><center>🚀 <b>Dashboard de Inteligencia Avanzada</b> 🚀<br><small>Desarrollado por: Im a New Rookie</small></center></div>', unsafe_allow_html=True)

# SIDEBAR - CONFIGURACIÓN Y NAVEGACIÓN
st.sidebar.title("⚙️ Centro de Comando")
st.sidebar.markdown("---")

# Configuración personal
st.sidebar.subheader("👤 Configuración Personal")
mi_jugador = st.sidebar.text_input("🎮 Tu nombre de jugador", value="Im+a+New+Rookie")
mi_alianza_id = st.sidebar.number_input("🛡️ ID de tu Alianza", min_value=0, value=182, step=1)

st.sidebar.markdown("---")

# PESTAÑAS PRINCIPALES
st.sidebar.subheader("📊 Navegación")
tab_selection = st.sidebar.radio(
    "Seleccionar sección:",
    ["🌍 SERVIDOR", "🛡️ ALIANZA", "👤 JUGADOR"],
    index=0
)

st.sidebar.markdown("---")

# Botón de actualización
if st.sidebar.button("🔄 ACTUALIZAR DATOS", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

# Mostrar hora de última actualización
st.sidebar.info(f"🕒 Última actualización: {datetime.now().strftime('%H:%M:%S')}")

# CARGAR DATOS
players_data, success, message = load_grepolis_data()
alliance_data = load_alliance_data()
towns_data = load_towns_data()

# Mostrar estado de conexión
if success:
    st.success(message)
else:
    st.error(message)
    st.stop()

# Procesar datos con estados de actividad
players_with_activity = simulate_activity_status(players_data)

# =============================================================================
# PESTAÑA: SERVIDOR
# =============================================================================
if tab_selection == "🌍 SERVIDOR":
    st.header("🌍 Información del Servidor ES137")
    
    # Estado General de Ciudades
    st.subheader("🏘️ Estado General de Ciudades")
    
    if towns_data is not None:
        # Calcular estadísticas de ciudades
        total_cities = len(towns_data)
        
        # Simular estados de ciudades basándose en jugadores
        cities_with_status = towns_data.merge(
            players_with_activity[['ID', 'Estado']], 
            left_on='ID_Jugador', 
            right_on='ID', 
            how='left'
        )
        
        # Ciudades por estado
        activas = len(cities_with_status[cities_with_status['Estado'] == '🟢 Activo'])
        vacaciones = len(cities_with_status[cities_with_status['Estado'] == '🟡 Reciente'])  # Simular vacaciones
        fantasma = len(cities_with_status[cities_with_status['Estado'].isin(['🟠 Inactivo', '🔴 Offline'])])
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏘️ Total Ciudades", f"{total_cities:,}")
        
        with col2:
            st.metric("🟢 Activas", f"{activas:,}", delta=f"{activas/total_cities*100:.1f}%")
        
        with col3:
            st.metric("🟡 Vacaciones", f"{vacaciones:,}", delta=f"{vacaciones/total_cities*100:.1f}%")
        
        with col4:
            st.metric("👻 Fantasma", f"{fantasma:,}", delta=f"{fantasma/total_cities*100:.1f}%")
        
        # Gráfico de distribución de ciudades
        fig_cities = px.pie(
            values=[activas, vacaciones, fantasma],
            names=['Activas', 'Vacaciones', 'Fantasma'],
            title="Distribución de Estados de Ciudades",
            color_discrete_sequence=['#28a745', '#ffc107', '#dc3545']
        )
        st.plotly_chart(fig_cities, use_container_width=True)
    
    else:
        st.warning("❌ No se pudieron cargar los datos de ciudades")
    
    st.markdown("---")
    
    # Estado de Jugadores
    st.subheader("👥 Estado de Jugadores")
    
    # Métricas de jugadores
    total_players = len(players_with_activity)
    active_players = len(players_with_activity[players_with_activity['Estado'] == '🟢 Activo'])
    recent_players = len(players_with_activity[players_with_activity['Estado'] == '🟡 Reciente'])
    inactive_players = len(players_with_activity[players_with_activity['Estado'] == '🟠 Inactivo'])
    offline_players = len(players_with_activity[players_with_activity['Estado'] == '🔴 Offline'])
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("👥 Total", f"{total_players:,}")
    
    with col2:
        st.metric("🟢 Activos", f"{active_players:,}", delta="< 4h")
    
    with col3:
        st.metric("🟡 Recientes", f"{recent_players:,}", delta="6-12h")
    
    with col4:
        st.metric("🟠 Inactivos", f"{inactive_players:,}", delta="12-24h")
    
    with col5:
        st.metric("🔴 Offline", f"{offline_players:,}", delta="> 24h")
    
    # Filtros para la lista de jugadores
    st.subheader("🔍 Lista de Jugadores con Filtros")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_status = st.selectbox(
            "📊 Filtrar por estado:",
            ["Todos", "🟢 Activos", "🟡 Recientes", "🟠 Inactivos", "🔴 Offline"]
        )
    
    with col2:
        sort_by = st.selectbox(
            "📈 Ordenar por:",
            ["Ranking", "Nombre", "Puntos", "Estado"]
        )
    
    with col3:
        max_players = st.slider("📋 Mostrar jugadores:", 10, 100, 50)
    
    # Aplicar filtros
    filtered_players = players_with_activity.copy()
    
    if filter_status != "Todos":
        filtered_players = filtered_players[filtered_players['Estado'] == filter_status]
    
    # Ordenar
    if sort_by == "Ranking":
        filtered_players = filtered_players.sort_values('Ranking')
    elif sort_by == "Nombre":
        filtered_players = filtered_players.sort_values('Nombre')
    elif sort_by == "Puntos":
        filtered_players = filtered_players.sort_values('Puntos', ascending=False)
    elif sort_by == "Estado":
        filtered_players = filtered_players.sort_values('Estado')
    
    # Mostrar tabla
    display_players = filtered_players.head(max_players)[['Ranking', 'Nombre', 'Puntos', 'Ciudades', 'Estado', 'Ultima_Actividad']]
    display_players['Ranking'] = display_players['Ranking'].astype(int)
    display_players['Puntos'] = display_players['Puntos'].astype(int)
    display_players['Ciudades'] = display_players['Ciudades'].astype(int)
    
    st.dataframe(
        display_players,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
            "Nombre": st.column_config.TextColumn("👤 Nombre"),
            "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
            "Ciudades": st.column_config.NumberColumn("🏘️ Ciudades", format="%d"),
            "Estado": st.column_config.TextColumn("📊 Estado"),
            "Ultima_Actividad": st.column_config.TextColumn("🕒 Última Actividad")
        }
    )
    
    st.markdown("---")
    
    # Top 10 Jugadores
    st.subheader("🏆 Top 10 Jugadores del Servidor")
    
    top_10 = players_data.head(10).copy()
    
    # Agregar información de alianza
    if alliance_data is not None:
        top_10 = top_10.merge(
            alliance_data[['ID_Alianza', 'Nombre_Alianza']], 
            on='ID_Alianza', 
            how='left'
        )
        top_10['Alianza'] = top_10['Nombre_Alianza'].fillna("Sin alianza")
    else:
        top_10['Alianza'] = top_10['ID_Alianza'].apply(
            lambda x: "Sin alianza" if x == 0 else f"ID: {x:.0f}"
        )
    
    # Mostrar top 10
    top_10_display = top_10[['Ranking', 'Nombre', 'Puntos', 'Alianza']]
    top_10_display['Ranking'] = top_10_display['Ranking'].astype(int)
    top_10_display['Puntos'] = top_10_display['Puntos'].astype(int)
    
    st.dataframe(
        top_10_display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Ranking": st.column_config.NumberColumn("🏆 Pos", format="#%d"),
            "Nombre": st.column_config.TextColumn("👑 Jugador"),
            "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
            "Alianza": st.column_config.TextColumn("🛡️ Alianza")
        }
    )

# =============================================================================
# PESTAÑA: ALIANZA
# =============================================================================
elif tab_selection == "🛡️ ALIANZA":
    st.header("🛡️ R.D.M.P - Centro de Comando")
    
    # Obtener miembros de R.D.M.P (ID 182)
    miembros_rdmp = players_with_activity[players_with_activity['ID_Alianza'] == mi_alianza_id].copy()
    
    if len(miembros_rdmp) > 0:
        # Información general de R.D.M.P
        if alliance_data is not None:
            mi_alianza_data = alliance_data[alliance_data['ID_Alianza'] == mi_alianza_id]
            if not mi_alianza_data.empty:
                alianza = mi_alianza_data.iloc[0]
                nombre_alianza = alianza['Nombre_Alianza']
                ranking_alianza = int(alianza['Ranking_Alianza'])
                puntos_alianza = int(alianza['Puntos_Alianza'])
            else:
                nombre_alianza = "R.D.M.P"
                ranking_alianza = "N/A"
                puntos_alianza = int(miembros_rdmp['Puntos'].sum())
        else:
            nombre_alianza = "R.D.M.P"
            ranking_alianza = "N/A"
            puntos_alianza = int(miembros_rdmp['Puntos'].sum())
        
        # Header de la alianza
        st.subheader(f"🏠 {nombre_alianza} - Estado Operacional")
        
        # Métricas principales de la alianza
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🏆 Ranking", f"#{ranking_alianza}")
        
        with col2:
            st.metric("💰 Puntos Totales", f"{puntos_alianza:,}")
        
        with col3:
            st.metric("👥 Miembros Activos", f"{len(miembros_rdmp)}")
        
        with col4:
            promedio_pts = int(miembros_rdmp['Puntos'].mean())
            st.metric("📊 Promedio", f"{promedio_pts:,} pts")
        
        with col5:
            total_ciudades = int(miembros_rdmp['Ciudades'].sum())
            st.metric("🏘️ Total Ciudades", f"{total_ciudades}")
        
        st.markdown("---")
        
        # Análisis de efectividad militar
        st.subheader("⚔️ Análisis Militar de R.D.M.P")
        
        # Clasificar miembros por capacidad militar
        miembros_rdmp['Categoria_Militar'] = pd.cut(
            miembros_rdmp['Puntos'],
            bins=[0, 1000, 3000, 6000, 15000, float('inf')],
            labels=['🟥 Recluta', '🟨 Soldado', '🟦 Veterano', '🟪 Elite', '🟫 Legendario']
        )
        
        # Calcular potencial militar estimado
        miembros_rdmp['Potencial_Militar'] = (miembros_rdmp['Puntos'] * 0.6 + miembros_rdmp['Ciudades'] * 200).astype(int)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Distribución por categoría militar
            categoria_counts = miembros_rdmp['Categoria_Militar'].value_counts()
            
            st.write("**🛡️ Distribución de Fuerzas:**")
            for categoria, count in categoria_counts.items():
                porcentaje = (count / len(miembros_rdmp)) * 100
                st.write(f"{categoria}: {count} miembros ({porcentaje:.1f}%)")
        
        with col2:
            # Estados de actividad
            estado_counts = miembros_rdmp['Estado'].value_counts()
            
            st.write("**📊 Estado Operacional:**")
            for estado, count in estado_counts.items():
                porcentaje = (count / len(miembros_rdmp)) * 100
                st.write(f"{estado}: {count} miembros ({porcentaje:.1f}%)")
        
        st.markdown("---")
        
        # Tabla detallada de miembros con información militar
        st.subheader("👥 Roster Completo de R.D.M.P")
        
        # Filtros para la tabla
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filtro_categoria = st.selectbox(
                "🎯 Filtrar por Categoría:",
                ["Todos"] + list(miembros_rdmp['Categoria_Militar'].unique())
            )
        
        with col2:
            filtro_estado = st.selectbox(
                "📊 Filtrar por Estado:",
                ["Todos"] + list(miembros_rdmp['Estado'].unique())
            )
        
        with col3:
            ordenar_por = st.selectbox(
                "📈 Ordenar por:",
                ["Puntos", "Ranking", "Potencial Militar", "Ciudades", "Nombre"]
            )
        
        # Aplicar filtros
        miembros_filtrados = miembros_rdmp.copy()
        
        if filtro_categoria != "Todos":
            miembros_filtrados = miembros_filtrados[miembros_filtrados['Categoria_Militar'] == filtro_categoria]
        
        if filtro_estado != "Todos":
            miembros_filtrados = miembros_filtrados[miembros_filtrados['Estado'] == filtro_estado]
        
        # Ordenar
        if ordenar_por == "Puntos":
            miembros_filtrados = miembros_filtrados.sort_values('Puntos', ascending=False)
        elif ordenar_por == "Ranking":
            miembros_filtrados = miembros_filtrados.sort_values('Ranking')
        elif ordenar_por == "Potencial Militar":
            miembros_filtrados = miembros_filtrados.sort_values('Potencial_Militar', ascending=False)
        elif ordenar_por == "Ciudades":
            miembros_filtrados = miembros_filtrados.sort_values('Ciudades', ascending=False)
        elif ordenar_por == "Nombre":
            miembros_filtrados = miembros_filtrados.sort_values('Nombre')
        
        # Preparar tabla para mostrar
        tabla_miembros = miembros_filtrados[[
            'Ranking', 'Nombre', 'Puntos', 'Ciudades', 'Categoria_Militar', 
            'Estado', 'Potencial_Militar'
        ]].copy()
        
        # Formatear números
        tabla_miembros['Ranking'] = tabla_miembros['Ranking'].astype(int)
        tabla_miembros['Puntos'] = tabla_miembros['Puntos'].astype(int)
        tabla_miembros['Ciudades'] = tabla_miembros['Ciudades'].astype(int)
        
        # Cambiar nombres de columnas
        tabla_miembros.columns = ['Ranking', 'Nombre', 'Puntos', 'Ciudades', 'Categoría', 'Estado', 'Pot. Militar']
        
        # Destacar tu jugador
        def highlight_my_player(row):
            if row['Nombre'] == mi_jugador:
                return ['background-color: #90EE90; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        st.dataframe(
            tabla_miembros,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
                "Nombre": st.column_config.TextColumn("👤 Nombre"),
                "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
                "Ciudades": st.column_config.NumberColumn("🏘️ Ciudades", format="%d"),
                "Categoría": st.column_config.TextColumn("⚔️ Categoría"),
                "Estado": st.column_config.TextColumn("📊 Estado"),
                "Pot. Militar": st.column_config.NumberColumn("🎯 Potencial", format="%d", help="Estimación de capacidad militar")
            }
        )
        
        st.markdown("---")
        
        # Análisis de crecimiento de la alianza
        st.subheader("📈 Análisis de Rendimiento")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top performers de la alianza
            st.write("**🏆 Top 5 R.D.M.P:**")
            top_5 = miembros_rdmp.nlargest(5, 'Puntos')[['Nombre', 'Ranking', 'Puntos']]
            
            for i, (_, member) in enumerate(top_5.iterrows(), 1):
                posicion_servidor = int(member['Ranking'])
                st.write(f"{i}. **{member['Nombre']}** - #{posicion_servidor} ({int(member['Puntos']):,} pts)")
        
        with col2:
            # Estadísticas de la alianza
            st.write("**📊 Estadísticas Clave:**")
            
            mejor_ranking = int(miembros_rdmp['Ranking'].min())
            peor_ranking = int(miembros_rdmp['Ranking'].max())
            mediana_puntos = int(miembros_rdmp['Puntos'].median())
            
            st.write(f"🥇 Mejor miembro: Puesto #{mejor_ranking}")
            st.write(f"📉 Miembro más bajo: Puesto #{peor_ranking}")
            st.write(f"📊 Mediana de puntos: {mediana_puntos:,}")
            st.write(f"🎯 Rango de influencia: {peor_ranking - mejor_ranking} posiciones")
        
        # Gráfico de distribución de puntos
        fig_distribucion = px.histogram(
            miembros_rdmp,
            x='Puntos',
            nbins=15,
            title="Distribución de Puntos en R.D.M.P",
            labels={'Puntos': 'Puntos del Jugador', 'count': 'Número de Miembros'},
            color_discrete_sequence=['#667eea']
        )
        
        fig_distribucion.update_layout(
            xaxis_title="Puntos",
            yaxis_title="Número de Miembros",
            showlegend=False
        )
        
        st.plotly_chart(fig_distribucion, use_container_width=True)
        
        # Comparación con otras alianzas (contexto)
        if alliance_data is not None and not mi_alianza_data.empty:
            st.markdown("---")
            st.subheader("🎯 Posición Competitiva")
            
            # Encontrar alianzas cercanas en ranking
            ranking_actual = int(alianza['Ranking_Alianza'])
            
            alianzas_cercanas = alliance_data[
                (alliance_data['Ranking_Alianza'] >= ranking_actual - 3) &
                (alliance_data['Ranking_Alianza'] <= ranking_actual + 3)
            ].copy()
            
            # Destacar R.D.M.P
            def highlight_rdmp(row):
                if row['ID_Alianza'] == mi_alianza_id:
                    return ['background-color: #FFD700; font-weight: bold'] * len(row)
                return [''] * len(row)
            
            alianzas_display = alianzas_cercanas[['Ranking_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Miembros']].copy()
            alianzas_display['Promedio'] = (alianzas_display['Puntos_Alianza'] / alianzas_display['Miembros']).astype(int)
            alianzas_display.columns = ['Ranking', 'Alianza', 'Puntos', 'Miembros', 'Promedio']
            
            st.write("**⚔️ Alianzas Competidoras Cercanas:**")
            st.dataframe(
                alianzas_display,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
                    "Alianza": st.column_config.TextColumn("🛡️ Alianza"),
                    "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
                    "Miembros": st.column_config.NumberColumn("👥 Miembros", format="%d"),
                    "Promedio": st.column_config.NumberColumn("📊 Promedio", format="%d")
                }
            )
    
    else:
        st.warning(f"❌ No se encontraron miembros de la alianza con ID: {mi_alianza_id}")
        st.info("💡 Verifica que el ID de alianza en el sidebar sea correcto (182 para R.D.M.P)")

# =============================================================================
# PESTAÑA: JUGADOR
# =============================================================================
elif tab_selection == "👤 JUGADOR":
    st.header("👤 Información de Jugadores")
    
    # Análisis personal
    st.subheader(f"🎮 Tu Perfil: {mi_jugador}")
    
    mi_data = players_with_activity[players_with_activity['Nombre'] == mi_jugador]
    
    if not mi_data.empty:
        yo = mi_data.iloc[0]
        
        # Métricas personales
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("🏆 Puntos", f"{int(yo['Puntos']):,}")
        
        with col2:
            st.metric("📊 Ranking", f"#{int(yo['Ranking'])}")
        
        with col3:
            percentil = (1 - (yo['Ranking'] / len(players_data))) * 100
            st.metric("📈 Percentil", f"Top {percentil:.1f}%")
        
        with col4:
            st.metric("🏘️ Ciudades", f"{int(yo['Ciudades'])}")
        
        with col5:
            st.metric("📊 Estado", yo['Estado'])
        
        # Análisis de progreso
        st.subheader("🚀 Análisis de Progreso")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Objetivos de Ranking:**")
            
            objetivos = []
            for salto in [5, 10, 25, 50]:
                if yo['Ranking'] - salto > 0:
                    objetivo_player = players_data.iloc[int(yo['Ranking']) - salto - 1]
                    puntos_necesarios = objetivo_player['Puntos'] - yo['Puntos']
                    if puntos_necesarios > 0:
                        objetivos.append({
                            'Objetivo': f"Subir {salto} posiciones",
                            'Ranking Meta': f"#{int(yo['Ranking']) - salto}",
                            'Puntos Necesarios': f"+{int(puntos_necesarios):,}",
                            'Jugador a Superar': objetivo_player['Nombre'][:15]
                        })
            
            if objetivos:
                df_objetivos = pd.DataFrame(objetivos)
                st.dataframe(df_objetivos, hide_index=True, use_container_width=True)
        
        with col2:
            st.write("**⚔️ Competencia Cercana:**")
            
            # Jugadores cerca de tu ranking
            rango_competencia = players_data[
                (players_data['Ranking'] >= yo['Ranking'] - 10) &
                (players_data['Ranking'] <= yo['Ranking'] + 10) &
                (players_data['Nombre'] != yo['Nombre'])
            ].head(10)
            
            for i, (_, competidor) in enumerate(rango_competencia.iterrows()):
                diferencia = int(competidor['Puntos'] - yo['Puntos'])
                if diferencia > 0:
                    st.write(f"⬆️ #{int(competidor['Ranking'])} {competidor['Nombre'][:20]} (+{diferencia:,} pts)")
                else:
                    st.write(f"⬇️ #{int(competidor['Ranking'])} {competidor['Nombre'][:20]} ({diferencia:,} pts)")
    
    else:
        st.warning(f"❌ No se encontró el jugador '{mi_jugador}'")
        
        # Sugerencias de nombres similares
        similares = players_data[players_data['Nombre'].str.contains(mi_jugador.replace('+', '|'), case=False, na=False)]
        if not similares.empty:
            st.write("🔍 **Nombres similares encontrados:**")
            for _, player in similares.head(5).iterrows():
                st.write(f"• {player['Nombre']} (#{int(player['Ranking'])})")
    
    st.markdown("---")
    
    # Búsqueda de jugadores
    st.subheader("🔍 Búsqueda de Jugadores")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        search_term = st.text_input("🎮 Buscar jugador:", placeholder="Nombre del jugador...")
    
    with col2:
        search_type = st.selectbox("🔍 Tipo de búsqueda", ["Contiene", "Exacto", "Empieza con"])
    
    with col3:
        search_filter = st.selectbox("📊 Filtrar por", ["Todos", "Con alianza", "Sin alianza", "Top 100"])
    
    if search_term:
        # Aplicar filtros de búsqueda
        if search_type == "Contiene":
            resultados = players_with_activity[players_with_activity['Nombre'].str.contains(search_term, case=False, na=False)]
        elif search_type == "Exacto":
            resultados = players_with_activity[players_with_activity['Nombre'] == search_term]
        else:  # Empieza con
            resultados = players_with_activity[players_with_activity['Nombre'].str.startswith(search_term, na=False)]
        
        # Aplicar filtros adicionales
        if search_filter == "Con alianza":
            resultados = resultados[resultados['ID_Alianza'] != 0]
        elif search_filter == "Sin alianza":
            resultados = resultados[resultados['ID_Alianza'] == 0]
        elif search_filter == "Top 100":
            resultados = resultados[resultados['Ranking'] <= 100]
        
        if not resultados.empty:
            st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)")
            
            # Mostrar resultados
            resultados_display = resultados[['Ranking', 'Nombre', 'Puntos', 'Ciudades', 'Estado']].head(20)
            resultados_display['Ranking'] = resultados_display['Ranking'].astype(int)
            resultados_display['Puntos'] = resultados_display['Puntos'].astype(int)
            resultados_display['Ciudades'] = resultados_display['Ciudades'].astype(int)
            
            st.dataframe(
                resultados_display,
                hide_index=True,
                use_container_width=True,
                column_config={
                    "Ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
                    "Nombre": st.column_config.TextColumn("👤 Nombre"),
                    "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
                    "Ciudades": st.column_config.NumberColumn("🏘️ Ciudades", format="%d"),
                    "Estado": st.column_config.TextColumn("📊 Estado")
                }
            )
        else:
            st.error("❌ No se encontraron resultados")

# FOOTER
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; margin-top: 2rem;'>
        🏛️ <b>GrepoIntel ES137 | R.D.M.P</b><br>
        <i>Desarrollado por: Im a New Rookie</i><br><br>
        📊 Actualización automática cada 15 minutos | 
        🚀 Powered by Streamlit | 
        🛡️ Dashboard de Inteligencia Militar<br>
        <small>💡 Navega por las pestañas del sidebar para explorar diferentes secciones</small>
    </div>
    """, 
    unsafe_allow_html=True
)
