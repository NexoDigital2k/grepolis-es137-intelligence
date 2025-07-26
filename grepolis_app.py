import streamlit as st
import pandas as pd
import requests
import io
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuración de la página
st.set_page_config(
    page_title="Grepolis ES137 Intelligence",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f4e79;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .target-card {
        background: #ff6b6b;
        padding: 0.8rem;
        border-radius: 8px;
        color: white;
        margin: 0.3rem 0;
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
</style>
""", unsafe_allow_html=True)

# Función para cargar datos
@st.cache_data(ttl=900)  # Cache por 15 minutos
def load_grepolis_data():
    """Carga y procesa datos de Grepolis ES137"""
    try:
        url = "https://es137.grepolis.com/data/players.txt"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Procesar datos
            players_data = pd.read_csv(
                io.StringIO(response.text),
                sep=',',
                names=['ID', 'Nombre', 'ID_Alianza', 'Puntos', 'Ranking', 'Ciudades'],
                na_values=['']
            )
            
            # Limpiar datos
            players_data = players_data.dropna(subset=['Nombre'])
            players_data['ID_Alianza'] = players_data['ID_Alianza'].fillna(0)
            players_data = players_data.sort_values('Ranking')
            
            return players_data, True, f"Datos actualizados: {datetime.now().strftime('%H:%M:%S')}"
        else:
            return None, False, f"Error de conexión: {response.status_code}"
    
    except Exception as e:
        return None, False, f"Error: {str(e)}"

# Función para cargar alianzas
@st.cache_data(ttl=900)
def load_alliance_data():
    """Carga datos de alianzas"""
    try:
        url = "https://es137.grepolis.com/data/alliance.txt"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            alliance_data = pd.read_csv(
                io.StringIO(response.text),
                sep=',',
                names=['ID_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Ranking_Alianza', 'Miembros']
            )
            return alliance_data
        else:
            return None
    except:
        return None

# Header principal
st.markdown('<h1 class="main-header">🏛️ Grepolis ES137 Intelligence</h1>', unsafe_allow_html=True)

# Sidebar para configuración
st.sidebar.title("⚙️ Configuración")

# Configuración de alianza
st.sidebar.subheader("🛡️ Tu Alianza")
mi_alianza_id = st.sidebar.number_input("ID de tu Alianza", min_value=1, value=182, step=1)
mi_jugador = st.sidebar.text_input("Tu nombre de jugador", value="Im+a+New+Rookie")

# Opciones de análisis
st.sidebar.subheader("📊 Análisis")
mostrar_targets = st.sidebar.checkbox("Mostrar Targets", value=True)
mostrar_amenazas = st.sidebar.checkbox("Mostrar Amenazas", value=True)
mostrar_alianza = st.sidebar.checkbox("Análisis de Alianza", value=True)

# Configuración de targets
st.sidebar.subheader("🎯 Filtros de Targets")
max_puntos_target = st.sidebar.slider("Puntos máximos del target", 0, 5000, 3000)
max_ciudades_target = st.sidebar.selectbox("Ciudades máximas", [1, 2, 3, 4], index=1)

# Botón de actualización
if st.sidebar.button("🔄 Actualizar Datos", type="primary"):
    st.cache_data.clear()
    st.rerun()

# Cargar datos
with st.spinner("Cargando datos de Grepolis ES137..."):
    players_data, success, message = load_grepolis_data()
    alliance_data = load_alliance_data()

if not success:
    st.error(f"❌ {message}")
    st.stop()

st.success(f"✅ {message}")

# MÉTRICAS PRINCIPALES
st.subheader("📊 Métricas del Servidor")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="👥 Jugadores Totales",
        value=f"{len(players_data):,}",
        delta=None
    )

with col2:
    sin_alianza = len(players_data[players_data['ID_Alianza'] == 0])
    st.metric(
        label="🎯 Sin Alianza",
        value=f"{sin_alianza:,}",
        delta=f"{sin_alianza/len(players_data)*100:.1f}%"
    )

with col3:
    lider = players_data.iloc[0]
    st.metric(
        label="🏆 Líder",
        value=lider['Nombre'],
        delta=f"{lider['Puntos']:,} pts"
    )

with col4:
    veteranos = len(players_data[players_data['Puntos'] >= 10000])
    st.metric(
        label="👑 Veteranos",
        value=f"{veteranos:,}",
        delta="≥10K pts"
    )

# ANÁLISIS PERSONAL
st.subheader(f"🎮 Análisis de {mi_jugador}")

mi_data = players_data[players_data['Nombre'] == mi_jugador]

if not mi_data.empty:
    yo = mi_data.iloc[0]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏆 Puntos", f"{yo['Puntos']:,}")
    
    with col2:
        st.metric("📊 Ranking", f"#{yo['Ranking']:.0f}")
    
    with col3:
        percentil = (1 - (yo['Ranking'] / len(players_data))) * 100
        st.metric("📈 Percentil", f"Top {percentil:.1f}%")
    
    with col4:
        st.metric("🏘️ Ciudades", f"{yo['Ciudades']:.0f}")
    
    # Gráfico de posición
    st.subheader("📈 Tu Posición en el Servidor")
    
    # Crear gráfico de distribución
    fig = px.histogram(
        players_data, 
        x='Puntos', 
        nbins=50,
        title="Distribución de Puntos en ES137",
        labels={'x': 'Puntos', 'y': 'Número de Jugadores'}
    )
    
    # Marcar tu posición
    fig.add_vline(
        x=yo['Puntos'], 
        line_dash="dash", 
        line_color="red",
        annotation_text=f"Tu posición: {yo['Puntos']:,} pts"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning(f"❌ No se encontró el jugador '{mi_jugador}'. Verifica el nombre en la configuración.")

# TARGETS
if mostrar_targets:
    st.subheader("🎯 Targets Vulnerables")
    
    targets = players_data[
        (players_data['Puntos'] < max_puntos_target) &
        (players_data['ID_Alianza'] == 0) &
        (players_data['Ciudades'] <= max_ciudades_target) &
        (players_data['Puntos'] > 100)
    ].sort_values('Puntos', ascending=False)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"**{len(targets)} targets encontrados**")
        
        # Tabla de targets
        targets_display = targets[['Ranking', 'Nombre', 'Puntos', 'Ciudades']].head(15)
        targets_display['Ranking'] = targets_display['Ranking'].astype(int)
        targets_display['Puntos'] = targets_display['Puntos'].astype(int)
        targets_display['Ciudades'] = targets_display['Ciudades'].astype(int)
        
        st.dataframe(
            targets_display,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        # Gráfico de targets por rango
        targets['Rango_Puntos'] = pd.cut(
            targets['Puntos'], 
            bins=[0, 500, 1000, 1500, 2000, 3000],
            labels=['0-500', '500-1K', '1K-1.5K', '1.5K-2K', '2K-3K']
        )
        
        target_counts = targets['Rango_Puntos'].value_counts()
        
        fig_targets = px.pie(
            values=target_counts.values,
            names=target_counts.index,
            title="Targets por Rango de Puntos"
        )
        
        st.plotly_chart(fig_targets, use_container_width=True)

# ANÁLISIS DE ALIANZA
if mostrar_alianza and alliance_data is not None:
    st.subheader("🛡️ Análisis de Alianzas")
    
    # Top alianzas
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Top 10 Alianzas**")
        top_alliances = alliance_data.head(10)[['Ranking_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Miembros']]
        top_alliances.columns = ['Ranking', 'Alianza', 'Puntos', 'Miembros']
        st.dataframe(top_alliances, hide_index=True)
    
    with col2:
        # Gráfico de puntos vs miembros
        fig_alliance = px.scatter(
            alliance_data.head(20),
            x='Miembros',
            y='Puntos_Alianza',
            text='Nombre_Alianza',
            title="Puntos vs Miembros (Top 20)",
            labels={'Miembros': 'Número de Miembros', 'Puntos_Alianza': 'Puntos Totales'}
        )
        fig_alliance.update_traces(textposition="top center")
        st.plotly_chart(fig_alliance, use_container_width=True)
    
    # Análisis de mi alianza
    mi_alianza_data = alliance_data[alliance_data['ID_Alianza'] == mi_alianza_id]
    
    if not mi_alianza_data.empty:
        alianza = mi_alianza_data.iloc[0]
        st.write(f"**📊 Tu Alianza: {alianza['Nombre_Alianza']}**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🏆 Puntos", f"{alianza['Puntos_Alianza']:,.0f}")
        
        with col2:
            st.metric("📊 Ranking", f"#{alianza['Ranking_Alianza']:.0f}")
        
        with col3:
            st.metric("👥 Miembros", f"{alianza['Miembros']:.0f}")
        
        with col4:
            promedio = alianza['Puntos_Alianza'] / alianza['Miembros']
            st.metric("📈 Promedio/Miembro", f"{promedio:,.0f}")

# HERRAMIENTAS ADICIONALES
st.subheader("🔧 Herramientas")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("🔍 Buscar Jugador", type="secondary"):
        st.session_state.show_search = True

with col2:
    if st.button("📊 Análisis Detallado", type="secondary"):
        st.session_state.show_analysis = True

with col3:
    if st.button("⬇️ Exportar Datos", type="secondary"):
        csv = targets.to_csv(index=False)
        st.download_button(
            label="📥 Descargar Targets CSV",
            data=csv,
            file_name=f"targets_es137_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv"
        )

# Búsqueda de jugador
if st.session_state.get('show_search', False):
    st.subheader("🔍 Búsqueda de Jugador")
    
    search_term = st.text_input("Buscar jugador por nombre:")
    
    if search_term:
        resultados = players_data[
            players_data['Nombre'].str.contains(search_term, case=False, na=False)
        ]
        
        if not resultados.empty:
            st.write(f"**{len(resultados)} resultados encontrados:**")
            
            for _, jugador in resultados.head(10).iterrows():
                alianza_info = "Sin alianza" if jugador['ID_Alianza'] == 0 else f"Alianza ID: {jugador['ID_Alianza']:.0f}"
                st.write(f"• **{jugador['Nombre']}** - #{jugador['Ranking']:.0f} - {jugador['Puntos']:,.0f} pts - {alianza_info}")
        else:
            st.write("No se encontraron resultados.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        🏛️ Grepolis ES137 Intelligence App | Actualizado cada 15 minutos | 
        Desarrollado para tu alianza
    </div>
    """, 
    unsafe_allow_html=True
)
