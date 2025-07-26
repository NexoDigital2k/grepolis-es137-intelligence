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
    page_title="🏛️ GrepoIntel ES137 | R.D.M.P | Desarrollado por: Im a New Rookie",
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
    .target-highlight {
        background: linear-gradient(135deg, #FF6B6B, #FF8E53);
        padding: 1rem;
        border-radius: 12px;
        color: white;
        margin: 0.5rem 0;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
    }
    .success-box {
        background: linear-gradient(135deg, #56CCF2, #2F80ED);
        padding: 1.2rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(86, 204, 242, 0.3);
    }
    .warning-box {
        background: linear-gradient(135deg, #FFB347, #FF8C42);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #A8E6CF, #7FCDCD);
        padding: 1rem;
        border-radius: 10px;
        color: #2C3E50;
        margin: 0.5rem 0;
        border-left: 5px solid #27AE60;
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
    .alliance-card {
        background: linear-gradient(135deg, #8B5CF6, #A855F7);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 0.5rem 0;
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
                # Procesar datos
                players_data = pd.read_csv(
                    io.StringIO(response.text),
                    sep=',',
                    names=['ID', 'Nombre', 'ID_Alianza', 'Puntos', 'Ranking', 'Ciudades'],
                    na_values=['']
                )
                
                # Limpiar y ordenar datos
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
    """Carga datos de alianzas con diagnóstico mejorado"""
    try:
        url = "https://es137.grepolis.com/data/alliance.txt"
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Verificar si el archivo tiene contenido
            if len(response.text.strip()) == 0:
                return None  # Archivo vacío
            
            alliance_data = pd.read_csv(
                io.StringIO(response.text),
                sep=',',
                names=['ID_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Ranking_Alianza', 'Miembros']
            )
            
            # Verificar si los datos son válidos
            if len(alliance_data) == 0:
                return None
                
            return alliance_data
        else:
            return None  # Error HTTP
    except Exception as e:
        return None  # Error de conexión o parsing

@st.cache_data(ttl=900)
def load_towns_data():
    """Carga datos de ciudades para análisis territorial"""
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

# HEADER PRINCIPAL CORREGIDO
st.markdown('<h1 class="main-header">🏛️ GrepoIntel ES137 | R.D.M.P | Desarrollado por: Im a New Rookie</h1>', unsafe_allow_html=True)
st.markdown('<div class="success-box"><center>🚀 <b>Dashboard de Inteligencia Avanzada para R.D.M.P</b> 🚀</center></div>', unsafe_allow_html=True)

# SIDEBAR MEJORADO
st.sidebar.title("⚙️ Centro de Comando")
st.sidebar.markdown("---")

# Configuración personal
st.sidebar.subheader("👤 Configuración Personal")
mi_jugador = st.sidebar.text_input(
    "🎮 Tu nombre de jugador", 
    value="Im+a+New+Rookie", 
    help="Escribe tu nombre exacto como aparece en el juego"
)

# Selector de alianza mejorado con detección inteligente
alliance_data_sidebar = load_alliance_data()
selected_alliance_name = "R.D.M.P"  # Tu alianza por defecto
mi_alianza_id = 182  # Tu ID por defecto

if alliance_data_sidebar is not None:
    st.sidebar.success("✅ Datos de alianzas cargados correctamente")
    
    # Ordenar alianzas por ranking (mejores primero)
    alliance_options = alliance_data_sidebar.sort_values('Ranking_Alianza')
    
    # Crear lista de nombres de alianzas
    alliance_names = ["Sin alianza"] + alliance_options['Nombre_Alianza'].tolist()
    
    # Buscar el índice de R.D.M.P (tu alianza)
    try:
        rdmp_index = alliance_names.index("R.D.M.P") if "R.D.M.P" in alliance_names else 0
    except:
        rdmp_index = 0
    
    # Selector de alianza
    selected_alliance_name = st.sidebar.selectbox(
        "🛡️ Tu Alianza", 
        alliance_names, 
        index=rdmp_index,
        help="Selecciona tu alianza de la lista ordenada por ranking"
    )
    
    # Obtener ID de la alianza seleccionada
    if selected_alliance_name == "Sin alianza":
        mi_alianza_id = 0
    else:
        mi_alianza_id = int(alliance_options[alliance_options['Nombre_Alianza'] == selected_alliance_name]['ID_Alianza'].iloc[0])
        
    # Mostrar información adicional de la alianza seleccionada
    if selected_alliance_name != "Sin alianza":
        alianza_info = alliance_options[alliance_options['Nombre_Alianza'] == selected_alliance_name].iloc[0]
        st.sidebar.info(f"""
        **🏛️ {selected_alliance_name}**
        🏆 Ranking: #{int(alianza_info['Ranking_Alianza'])}
        👥 Miembros: {int(alianza_info['Miembros'])}
        💰 Puntos: {int(alianza_info['Puntos_Alianza']):,}
        📈 Promedio: {int(alianza_info['Puntos_Alianza']/alianza_info['Miembros']):,} pts/miembro
        """)
else:
    # Modo manual cuando no hay datos de alianzas
    st.sidebar.info("ℹ️ Datos de alianzas no disponibles - Modo manual activado")
    
    # Input manual para alianza
    mi_alianza_id = st.sidebar.number_input("🛡️ ID de tu Alianza", min_value=0, value=182, step=1)
    
    # Crear alianzas "virtuales" basadas en los datos de jugadores
    if players_data is not None:
        alianzas_detectadas = players_data[players_data['ID_Alianza'] != 0]['ID_Alianza'].value_counts().head(10)
        
        if len(alianzas_detectadas) > 0:
            st.sidebar.write("**🔍 Alianzas detectadas en datos de jugadores:**")
            for alianza_id, miembros in alianzas_detectadas.items():
                if alianza_id == mi_alianza_id:
                    st.sidebar.write(f"🎯 **ID {alianza_id}:** {miembros} miembros ← Tu alianza")
                else:
                    st.sidebar.write(f"• ID {alianza_id}: {miembros} miembros")
            
            selected_alliance_name = f"Alianza ID: {mi_alianza_id}"

st.sidebar.markdown("---")

# Configuración de análisis
st.sidebar.subheader("🎯 Configuración de Intelligence")
max_puntos_target = st.sidebar.slider("📊 Puntos máximos del target", 0, 5000, 3000, step=100)
max_ciudades_target = st.sidebar.selectbox("🏘️ Ciudades máximas", [1, 2, 3, 4], index=1)
incluir_alianzas_debiles = st.sidebar.checkbox("🎯 Incluir alianzas débiles", value=False, help="Incluye jugadores de alianzas con <1000 pts promedio")

st.sidebar.markdown("---")

# Opciones de visualización
st.sidebar.subheader("📊 Opciones de Display")
mostrar_graficos_avanzados = st.sidebar.checkbox("📈 Gráficos avanzados", value=True)
mostrar_analisis_territorial = st.sidebar.checkbox("🗺️ Análisis territorial", value=True)
mostrar_predicciones = st.sidebar.checkbox("🔮 Predicciones", value=True)
modo_compacto = st.sidebar.checkbox("📱 Modo compacto", value=False)

st.sidebar.markdown("---")

# Botones de acción
if st.sidebar.button("🔄 ACTUALIZAR DATOS", type="primary", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("📊 ANÁLISIS COMPLETO", type="secondary", use_container_width=True):
    st.session_state.show_full_analysis = True

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

# MÉTRICAS PRINCIPALES MEJORADAS
st.subheader("📊 Estado General de ES137")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="👥 Jugadores",
        value=f"{len(players_data):,}",
        help="Total de jugadores activos en ES137"
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
        label="👑 Líder",
        value=lider['Nombre'][:12] + "..." if len(lider['Nombre']) > 12 else lider['Nombre'],
        delta=f"{lider['Puntos']:,} pts"
    )

with col4:
    veteranos = len(players_data[players_data['Puntos'] >= 10000])
    st.metric(
        label="🏛️ Veteranos",
        value=f"{veteranos}",
        delta="≥10K pts"
    )

with col5:
    promedio_pts = players_data['Puntos'].mean()
    st.metric(
        label="📈 Promedio",
        value=f"{promedio_pts:,.0f}",
        delta="pts/jugador"
    )

# ANÁLISIS PERSONAL MEJORADO
st.markdown("---")
st.subheader(f"🎮 Análisis Personal: {mi_jugador}")

mi_data = players_data[players_data['Nombre'] == mi_jugador]

if not mi_data.empty:
    yo = mi_data.iloc[0]
    
    # Métricas personales en layout mejorado
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("🏆 Puntos", f"{yo['Puntos']:,}")
    
    with col2:
        st.metric("📊 Ranking", f"#{yo['Ranking']:.0f}")
    
    with col3:
        percentil = (1 - (yo['Ranking'] / len(players_data))) * 100
        st.metric("📈 Percentil", f"Top {percentil:.1f}%")
    
    with col4:
        st.metric("🏘️ Ciudades", f"{yo['Ciudades']:.0f}")
    
    with col5:
        # Manejo seguro de información de alianza
        if yo['ID_Alianza'] == 0:
            alianza_display = "Sin alianza"
        else:
            # Intentar obtener nombre real de la alianza
            if alliance_data is not None:
                alianza_match = alliance_data[alliance_data['ID_Alianza'] == yo['ID_Alianza']]
                if not alianza_match.empty:
                    alianza_display = alianza_match.iloc[0]['Nombre_Alianza']
                else:
                    alianza_display = f"ID: {yo['ID_Alianza']:.0f}"
            else:
                # Si no hay datos de alianzas, usar nombre configurado o ID
                if yo['ID_Alianza'] == mi_alianza_id:
                    alianza_display = "R.D.M.P"  # Tu alianza conocida
                else:
                    alianza_display = f"ID: {yo['ID_Alianza']:.0f}"
        
        st.metric("🛡️ Alianza", alianza_display)
    
    # Análisis de crecimiento personal
    if not modo_compacto:
        st.subheader("🚀 Análisis de Crecimiento Personal")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**🎯 Objetivos de Crecimiento:**")
            
            # Calcular objetivos realistas
            objetivos = []
            for salto in [10, 25, 50, 100]:
                if yo['Ranking'] - salto > 0:
                    objetivo_player = players_data.iloc[int(yo['Ranking']) - salto - 1]
                    puntos_necesarios = objetivo_player['Puntos'] - yo['Puntos']
                    if puntos_necesarios > 0:
                        objetivos.append({
                            'Objetivo': f"Subir {salto} posiciones",
                            'Ranking Meta': f"#{int(yo['Ranking']) - salto}",
                            'Puntos Necesarios': f"+{puntos_necesarios:,}",
                            'Dificultad': "🟢 Fácil" if puntos_necesarios < 500 else "🟡 Medio" if puntos_necesarios < 1500 else "🔴 Difícil"
                        })
            
            if objetivos:
                df_objetivos = pd.DataFrame(objetivos)
                st.dataframe(df_objetivos, hide_index=True, use_container_width=True)
        
        with col2:
            # Análisis de competencia cercana
            st.write("**⚔️ Competencia Cercana:**")
            
            # Jugadores cerca de tu ranking
            rango_competencia = players_data[
                (players_data['Ranking'] >= yo['Ranking'] - 15) &
                (players_data['Ranking'] <= yo['Ranking'] + 15) &
                (players_data['Nombre'] != yo['Nombre'])
            ].head(10)
            
            for _, competidor in rango_competencia.iterrows():
                diferencia = competidor['Puntos'] - yo['Puntos']
                if diferencia > 0:
                    st.write(f"⬆️ #{competidor['Ranking']:.0f} {competidor['Nombre']} (+{diferencia:.0f} pts)")
                else:
                    st.write(f"⬇️ #{competidor['Ranking']:.0f} {competidor['Nombre']} ({diferencia:.0f} pts)")
        
        # Gráfico de posición mejorado
        if mostrar_graficos_avanzados:
            st.write("**📊 Tu Posición vs Distribución del Servidor:**")
            
            fig = go.Figure()
            
            # Histograma de distribución
            fig.add_trace(go.Histogram(
                x=players_data['Puntos'],
                nbinsx=40,
                name="Distribución General",
                opacity=0.7,
                marker_color='lightblue'
            ))
            
            # Marcar tu posición
            fig.add_vline(
                x=yo['Puntos'],
                line_dash="dash",
                line_color="red",
                line_width=3,
                annotation_text=f"TÚ: {yo['Puntos']:,} pts"
            )
            
            # Marcar objetivos
            if objetivos:
                objetivo_cercano = players_data.iloc[int(yo['Ranking']) - 11]['Puntos']
                fig.add_vline(
                    x=objetivo_cercano,
                    line_dash="dot",
                    line_color="green",
                    annotation_text=f"Objetivo: {objetivo_cercano:,} pts"
                )
            
            fig.update_layout(
                title="Distribución de Puntos en ES137",
                xaxis_title="Puntos",
                yaxis_title="Número de Jugadores",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)

else:
    st.warning(f"❌ No se encontró el jugador '{mi_jugador}'. Verifica el nombre en la configuración del sidebar.")
    
    # Sugerencias de nombres similares
    similares = players_data[players_data['Nombre'].str.contains(mi_jugador.replace('+', '|').replace(' ', '|'), case=False, na=False)]
    if not similares.empty:
        st.write("🔍 **Nombres similares encontrados:**")
        for _, player in similares.head(5).iterrows():
            st.write(f"• {player['Nombre']} (#{player['Ranking']:.0f})")

# ANÁLISIS DE TARGETS MEJORADO
st.markdown("---")
st.subheader("🎯 Intelligence - Base de Datos de Targets")

# Filtros avanzados para targets
if incluir_alianzas_debiles and alliance_data is not None:
    # Incluir alianzas débiles (menos de 1000 pts promedio por miembro)
    alianzas_debiles = alliance_data[
        (alliance_data['Puntos_Alianza'] / alliance_data['Miembros']) < 1000
    ]['ID_Alianza'].tolist()
    
    targets = players_data[
        (players_data['Puntos'] < max_puntos_target) &
        (
            (players_data['ID_Alianza'] == 0) | 
            (players_data['ID_Alianza'].isin(alianzas_debiles))
        ) &
        (players_data['Ciudades'] <= max_ciudades_target) &
        (players_data['Puntos'] > 100)
    ].sort_values('Puntos', ascending=False)
else:
    targets = players_data[
        (players_data['Puntos'] < max_puntos_target) &
        (players_data['ID_Alianza'] == 0) &
        (players_data['Ciudades'] <= max_ciudades_target) &
        (players_data['Puntos'] > 100)
    ].sort_values('Puntos', ascending=False)

# Métricas de targets
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🎯 Targets Totales", f"{len(targets):,}")

with col2:
    targets_valiosos = len(targets[targets['Puntos'] > 1000])
    st.metric("💎 Targets Valiosos", f"{targets_valiosos:,}", delta=">1000 pts")

with col3:
    targets_faciles = len(targets[targets['Puntos'] < 500])
    st.metric("🎯 Targets Fáciles", f"{targets_faciles:,}", delta="<500 pts")

with col4:
    if len(targets) > 0:
        target_promedio = targets['Puntos'].mean()
        st.metric("📊 Promedio Target", f"{target_promedio:,.0f}", delta="pts")

# Tabla de targets mejorada
if len(targets) > 0:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.write("**🏹 Base de Datos de Targets:**")
        
        # Preparar datos para mostrar con información de alianza
        targets_display = targets[['Ranking', 'Nombre', 'Puntos', 'Ciudades', 'ID_Alianza']].head(20).copy()
        
        # Agregar información de alianza
        if alliance_data is not None:
            targets_display = targets_display.merge(
                alliance_data[['ID_Alianza', 'Nombre_Alianza']], 
                on='ID_Alianza', 
                how='left'
            )
            targets_display['Alianza'] = targets_display['Nombre_Alianza'].fillna("Sin alianza")
            targets_display = targets_display.drop(['ID_Alianza', 'Nombre_Alianza'], axis=1)
        else:
            targets_display['Alianza'] = targets_display['ID_Alianza'].apply(
                lambda x: "Sin alianza" if x == 0 else f"ID: {x:.0f}"
            )
            targets_display = targets_display.drop('ID_Alianza', axis=1)
        
        # Agregar columna de valor estimado de conquista
        targets_display['Valor Estimado'] = (targets_display['Puntos'] * 0.7 + 200).astype(int)
        
        # Formatear números
        targets_display['Ranking'] = targets_display['Ranking'].astype(int)
        targets_display['Puntos'] = targets_display['Puntos'].astype(int)
        targets_display['Ciudades'] = targets_display['Ciudades'].astype(int)
        
        st.dataframe(
            targets_display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Ranking": st.column_config.NumberColumn("🏆 Ranking", format="#%d"),
                "Nombre": st.column_config.TextColumn("👤 Nombre", width="medium"),
                "Puntos": st.column_config.NumberColumn("💰 Puntos", format="%d"),
                "Ciudades": st.column_config.NumberColumn("🏘️ Ciudades", format="%d"),
                "Alianza": st.column_config.TextColumn("🛡️ Alianza", width="small"),
                "Valor Estimado": st.column_config.NumberColumn("💎 Valor", format="+%d pts", help="Puntos estimados que ganarías al conquistar")
            }
        )
    
    with col2:
        # Análisis de targets por categorías
        st.write("**📊 Análisis de Targets:**")
        
        # Categorizar targets
        targets['Categoria'] = pd.cut(
            targets['Puntos'],
            bins=[0, 500, 1000, 1500, 2000, 3000],
            labels=['Principiante', 'Básico', 'Intermedio', 'Avanzado', 'Veterano']
        )
        
        categoria_counts = targets['Categoria'].value_counts()
        
        # Gráfico de dona
        fig_targets = px.pie(
            values=categoria_counts.values,
            names=categoria_counts.index,
            title="Targets por Categoría",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        st.plotly_chart(fig_targets, use_container_width=True)
        
        # Top 3 targets recomendados
        st.write("**🎯 Top 3 Recomendados:**")
        top_3 = targets.head(3)
        for i, (_, target) in enumerate(top_3.iterrows(), 1):
            valor_estimado = int(target['Puntos'] * 0.7 + 200)
            st.write(f"**{i}. {target['Nombre']}**")
            st.write(f"📊 {target['Puntos']:,} pts → +{valor_estimado:,} pts")
            st.write("---")

# CALCULADORA DE CONQUISTAS
if not mi_data.empty:
    st.markdown("---")
    st.subheader("🎯 Calculadora de Conquistas")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**⚔️ Simulador de Conquista:**")
        target_simulado = st.selectbox(
            "Seleccionar target:",
            options=targets['Nombre'].head(10).tolist(),
            help="Simula la conquista de uno de los top targets"
        )
        
        if target_simulado:
            target_data = targets[targets['Nombre'] == target_simulado].iloc[0]
            ganancia_estimada = int(target_data['Puntos'] * 0.7) + 200
            nuevo_total = yo['Puntos'] + ganancia_estimada
            
            st.info(f"🏆 Puntos del target: {target_data['Puntos']:,}")
            st.success(f"💰 Ganancia estimada: +{ganancia_estimada:,} pts")
            st.success(f"📊 Tus nuevos puntos: {nuevo_total:,}")
            
            # Calcular nuevo ranking estimado
            mejores = len(players_data[players_data['Puntos'] > nuevo_total])
            nuevo_ranking = mejores + 1
            salto_ranking = yo['Ranking'] - nuevo_ranking
            
            if salto_ranking > 0:
                st.success(f"📈 Nuevo ranking: #{nuevo_ranking} (+{salto_ranking} posiciones)")
    
    with col2:
        st.write("**📈 Análisis de Impacto:**")
        if target_simulado:
            # Gráfico de progreso
            fig_progreso = go.Figure(go.Bar(
                x=['Actual', 'Después de Conquista'],
                y=[yo['Puntos'], nuevo_total],
                marker_color=['lightblue', 'green'],
                text=[f"{yo['Puntos']:,}", f"{nuevo_total:,}"],
                textposition='auto',
            ))
            
            fig_progreso.update_layout(
                title="Progreso Estimado",
                yaxis_title="Puntos",
                height=300
            )
            
            st.plotly_chart(fig_progreso, use_container_width=True)
    
    with col3:
        st.write("**🎯 Estrategia Recomendada:**")
        if target_simulado:
            target_puntos = target_data['Puntos']
            
            if target_puntos < 500:
                st.write("🟢 **Target Fácil**")
                st.write("• Conquista directa")
                st.write("• Riesgo mínimo")
                st.write("• ROI: Alto")
            elif target_puntos < 1000:
                st.write("🟡 **Target Medio**")
                st.write("• Reconnaissance recomendado")
                st.write("• Riesgo moderado") 
                st.write("• ROI: Bueno")
            else:
                st.write("🔴 **Target Avanzado**")
                st.write("• Coordinación necesaria")
                st.write("• Riesgo alto")
                st.write("• ROI: Excelente")

# ANÁLISIS DE ALIANZAS MEJORADO
if alliance_data is not None:
    st.markdown("---")
    st.subheader("🛡️ Análisis de Alianzas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Ranking de Alianzas:**")
        top_alliances = alliance_data.head(15)[['Ranking_Alianza', 'Nombre_Alianza', 'Puntos_Alianza', 'Miembros']].copy()
        top_alliances.columns = ['Ranking', 'Alianza', 'Puntos', 'Miembros']
        top_alliances['Promedio'] = (top_alliances['Puntos'] / top_alliances['Miembros']).astype(int)
        top_alliances['Ranking'] = top_alliances['Ranking'].astype(int)
        top_alliances['Puntos'] = top_alliances['Puntos'].astype(int)
        top_alliances['Miembros'] = top_alliances['Miembros'].astype(int)
        
        # Destacar tu alianza
        def highlight_alliance(row):
            if row['Alianza'] == selected_alliance_name:
                return ['background-color: #FFD700; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        styled_alliances = top_alliances.style.apply(highlight_alliance, axis=1)
        st.dataframe(styled_alliances, hide_index=True, use_container_width=True)
    
    with col2:
        # Análisis de tu alianza
        mi_alianza_data = alliance_data[alliance_data['ID_Alianza'] == mi_alianza_id]
        
        if not mi_alianza_data.empty:
            alianza = mi_alianza_data.iloc[0]
            st.write(f"**🏠 Análisis de {alianza['Nombre_Alianza']}:**")
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("🏆 Puntos", f"{alianza['Puntos_Alianza']:,.0f}")
                st.metric("📊 Ranking", f"#{alianza['Ranking_Alianza']:.0f}")
            
            with col_b:
                st.metric("👥 Miembros", f"{alianza['Miembros']:.0f}")
                promedio_alianza = alianza['Puntos_Alianza'] / alianza['Miembros']
                st.metric("📈 Promedio", f"{promedio_alianza:,.0f}")
            
            # Miembros de la alianza
            miembros = players_data[players_data['ID_Alianza'] == mi_alianza_id]
            if len(miembros) > 0:
                st.write(f"**👥 Miembros de {alianza['Nombre_Alianza']}:**")
                miembros_sorted = miembros.sort_values('Puntos', ascending=False)
                
                # Crear DataFrame mejorado
                miembros_display = miembros_sorted[['Ranking', 'Nombre', 'Puntos', 'Ciudades']].head(10)
                miembros_display['Ranking'] = miembros_display['Ranking'].astype(int)
                miembros_display['Puntos'] = miembros_display['Puntos'].astype(int)
                miembros_display['Ciudades'] = miembros_display['Ciudades'].astype(int)
                
                # Destacar tu posición
                def highlight_player(row):
                    if row['Nombre'] == mi_jugador:
                        return ['background-color: #90EE90; font-weight: bold'] * len(row)
                    return [''] * len(row)
                
                styled_miembros = miembros_display.style.apply(highlight_player, axis=1)
                st.dataframe(styled_miembros, hide_index=True, use_container_width=True)
        
        else:
            st.warning(f"❌ No se encontró información de la alianza")
    
    # Gráfico de comparación de alianzas
    if mostrar_graficos_avanzados:
        st.write("**📊 Comparación de Top Alianzas:**")
        
        top_15 = alliance_data.head(15)
        
        fig_alliance = px.scatter(
            top_15,
            x='Miembros',
            y='Puntos_Alianza',
            size='Puntos_Alianza',
            color='Ranking_Alianza',
            hover_name='Nombre_Alianza',
            title="Puntos vs Miembros (Top 15 Alianzas)",
            labels={'Miembros': 'Número de Miembros', 'Puntos_Alianza': 'Puntos Totales'},
            color_continuous_scale='viridis_r'
        )
        
        # Destacar tu alianza si está en el top 15
        if not mi_alianza_data.empty and alianza['Ranking_Alianza'] <= 15:
            fig_alliance.add_scatter(
                x=[alianza['Miembros']],
                y=[alianza['Puntos_Alianza']],
                mode='markers',
                marker=dict(size=25, color='red', symbol='star', line=dict(width=2, color='white')),
                name=f'Tu Alianza ({alianza["Nombre_Alianza"]})',
                text=[alianza['Nombre_Alianza']]
            )
        
        st.plotly_chart(fig_alliance, use_container_width=True)

# HERRAMIENTAS AVANZADAS
st.markdown("---")
st.subheader("🔧 Herramientas Avanzadas")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🔍 Búsqueda Avanzada", use_container_width=True):
        st.session_state.show_search = True

with col2:
    if st.button("📊 Análisis Territorial", use_container_width=True):
        st.session_state.show_territorial = True

with col3:
    if st.button("⬇️ Exportar Intelligence", use_container_width=True):
        # Crear reporte completo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        
        # Datos para exportar
        export_data = {
            'targets': targets,
            'mi_alianza': miembros if 'miembros' in locals() else pd.DataFrame(),
            'top_alianzas': alliance_data.head(20) if alliance_data is not None else pd.DataFrame()
        }
        
        # Crear CSV combinado
        with st.spinner("Generando reporte..."):
            csv_targets = targets.to_csv(index=False)
            
        st.download_button(
            label="📥 Descargar Targets CSV",
            data=csv_targets,
            file_name=f"grepolis_es137_intelligence_{timestamp}.csv",
            mime="text/csv",
            use_container_width=True
        )

with col4:
    if st.button("🚨 Monitor de Amenazas", use_container_width=True):
        st.session_state.show_threats = True

# BÚSQUEDA AVANZADA
if st.session_state.get('show_search', False):
    st.markdown("---")
    st.subheader("🔍 Búsqueda Avanzada de Jugadores")
    
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
            resultados = players_data[players_data['Nombre'].str.contains(search_term, case=False, na=False)]
        elif search_type == "Exacto":
            resultados = players_data[players_data['Nombre'] == search_term]
        else:  # Empieza con
            resultados = players_data[players_data['Nombre'].str.startswith(search_term, na=False)]
        
        # Aplicar filtros adicionales
        if search_filter == "Con alianza":
            resultados = resultados[resultados['ID_Alianza'] != 0]
        elif search_filter == "Sin alianza":
            resultados = resultados[resultados['ID_Alianza'] == 0]
        elif search_filter == "Top 100":
            resultados = resultados[resultados['Ranking'] <= 100]
        
        if not resultados.empty:
            st.success(f"✅ {len(resultados)} resultado(s) encontrado(s)")
            
            # Mostrar resultados mejorados
            resultados_display = resultados[['Ranking', 'Nombre', 'Puntos', 'Ciudades', 'ID_Alianza']].head(20)
            
            # Agregar información de alianza
            if alliance_data is not None:
                resultados_display = resultados_display.merge(
                    alliance_data[['ID_Alianza', 'Nombre_Alianza']], 
                    on='ID_Alianza', 
                    how='left'
                )
                resultados_display['Alianza'] = resultados_display['Nombre_Alianza'].fillna("Sin alianza")
                resultados_display = resultados_display.drop(['ID_Alianza', 'Nombre_Alianza'], axis=1)
            else:
                resultados_display['Alianza'] = resultados_display['ID_Alianza'].apply(
                    lambda x: "Sin alianza" if x == 0 else f"ID: {x:.0f}"
                )
                resultados_display = resultados_display.drop('ID_Alianza', axis=1)
            
            st.dataframe(resultados_display, hide_index=True, use_container_width=True)
        else:
            st.error("❌ No se encontraron resultados")
    
    if st.button("❌ Cerrar Búsqueda"):
        st.session_state.show_search = False
        st.rerun()

# ANÁLISIS TERRITORIAL
if st.session_state.get('show_territorial', False) and towns_data is not None:
    st.markdown("---")
    st.subheader("🗺️ Análisis Territorial")
    
    # Análisis de densidad territorial
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏘️ Densidad de Ciudades por Región:**")
        
        # Crear mapa de calor de coordenadas
        if len(towns_data) > 0:
            fig_mapa = px.density_heatmap(
                towns_data.sample(min(1000, len(towns_data))),  # Sample para performance
                x='Coord_X',
                y='Coord_Y',
                title="Mapa de Densidad de Ciudades",
                labels={'Coord_X': 'Coordenada X', 'Coord_Y': 'Coordenada Y'}
            )
            
            st.plotly_chart(fig_mapa, use_container_width=True)
    
    with col2:
        st.write("**📊 Análisis de Concentración:**")
        
        # Top regiones por densidad
        region_analysis = towns_data.groupby(['Coord_X', 'Coord_Y']).size().reset_index(name='Ciudades')
        region_analysis = region_analysis.sort_values('Ciudades', ascending=False).head(10)
        
        st.write("**🏆 Top 10 Regiones más Densas:**")
        for _, region in region_analysis.iterrows():
            st.write(f"📍 ({region['Coord_X']}, {region['Coord_Y']}) - {region['Ciudades']} ciudades")
    
    if st.button("❌ Cerrar Análisis Territorial"):
        st.session_state.show_territorial = False
        st.rerun()

# MONITOR DE AMENAZAS
if st.session_state.get('show_threats', False) and not mi_data.empty:
    st.markdown("---")
    st.subheader("🚨 Monitor de Amenazas")
    
    # Identificar amenazas potenciales
    amenazas = players_data[
        (players_data['Ranking'] > yo['Ranking'] - 50) &
        (players_data['Ranking'] < yo['Ranking'] + 20) &
        (players_data['Puntos'] > yo['Puntos'] - 500) &
        (players_data['ID_Alianza'] != 0) &  # Con alianza (más peligrosos)
        (players_data['Nombre'] != yo['Nombre'])
    ].sort_values('Puntos', ascending=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**⚠️ Jugadores que Podrían Superarte:**")
        
        for _, amenaza in amenazas.head(10).iterrows():
            diferencia = amenaza['Puntos'] - yo['Puntos']
            alianza_amenaza = "Sin alianza"
            
            if alliance_data is not None:
                alianza_info = alliance_data[alliance_data['ID_Alianza'] == amenaza['ID_Alianza']]
                if not alianza_info.empty:
                    alianza_amenaza = alianza_info.iloc[0]['Nombre_Alianza']
            
            if diferencia > 0:
                st.warning(f"🚨 #{amenaza['Ranking']:.0f} **{amenaza['Nombre']}** (+{diferencia:.0f} pts) - {alianza_amenaza}")
            else:
                st.info(f"⚠️ #{amenaza['Ranking']:.0f} **{amenaza['Nombre']}** ({diferencia:.0f} pts) - {alianza_amenaza}")
    
    with col2:
        st.write("**📊 Análisis de Riesgo:**")
        
        if len(amenazas) > 0:
            # Gráfico de amenazas
            fig_amenazas = px.bar(
                x=amenazas['Nombre'].head(5),
                y=amenazas['Puntos'].head(5),
                title="Top 5 Amenazas por Puntos",
                labels={'x': 'Jugador', 'y': 'Puntos'}
            )
            
            # Añadir línea de referencia (tus puntos)
            fig_amenazas.add_hline(
                y=yo['Puntos'],
                line_dash="dash",
                line_color="red",
                annotation_text=f"Tus puntos: {yo['Puntos']:,}"
            )
            
            st.plotly_chart(fig_amenazas, use_container_width=True)
        else:
            st.success("🟢 No se detectaron amenazas inmediatas")
    
    if st.button("❌ Cerrar Monitor"):
        st.session_state.show_threats = False
        st.rerun()

# FOOTER MEJORADO
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.9rem; padding: 2rem; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; margin-top: 2rem;'>
        🏛️ <b>GrepoIntel ES137 | R.D.M.P</b><br>
        <i>Desarrollado por: Im a New Rookie</i><br><br>
        📊 Actualización automática cada 15 minutos | 
        🚀 Powered by Streamlit | 
        🛡️ Dedicado a la dominación de ES137<br>
        <small>💡 Usa el sidebar para personalizar tu experiencia | 
        📱 Optimizado para dispositivos móviles</small>
    </div>
    """, 
    unsafe_allow_html=True
)
