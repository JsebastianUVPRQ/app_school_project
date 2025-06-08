import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from PIL import Image
import io

# Cargar datos
player_data = pd.read_csv('player_stats.csv')
team_salary = pd.read_csv('team_salary.csv')

# Preprocesamiento de datos
player_data['age'] = player_data['age'].astype(int)
player_data['minutes_per_game'] = player_data['minutes'] / player_data['played']
player_data['goals_per_90'] = player_data['goals'] / (player_data['minutes'] / 90)
player_data['assists_per_90'] = player_data['assists'] / (player_data['minutes'] / 90)
player_data['goal_contributions'] = player_data['goals'] + player_data['assists']
player_data['goal_contributions_per_90'] = player_data['goal_contributions'] / (player_data['minutes'] / 90)

# Calcular estadísticas de equipo
team_stats = player_data.groupby('team').agg(
    total_goals=('goals', 'sum'),
    total_assists=('assists', 'sum'),
    total_minutes=('minutes', 'sum'),
    avg_age=('age', 'mean'),
    player_count=('name', 'count')
).reset_index()

# Combinar con datos de salario
team_data = pd.merge(team_stats, team_salary, on='team')
team_data['avg_weekly_salary'] = team_data['weekly'] / team_data['player_count']
team_data['efficiency'] = team_data['total_goals'] / (team_data['annual'] / 1000000)  # goles por millón de dólares

# Configurar la app
st.set_page_config(
    page_title="Análisis de Fútbol Premier League",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Sidebar para filtros globales
st.sidebar.title("Filtros Globales")
min_age, max_age = st.sidebar.slider(
    "Rango de Edad:",
    min_value=16, max_value=40, value=(18, 35)
)
selected_positions = st.sidebar.multiselect(
    "Posiciones:",
    options=player_data['position'].unique(),
    default=['DF', 'MF', 'FW'])
selected_teams = st.sidebar.multiselect(
    "Equipos:",
    options=player_data['team'].unique(),
    default=player_data['team'].unique())
# Aplicar filtros
filtered_players = player_data[
    (player_data['age'] >= min_age) & 
    (player_data['age'] <= max_age) & 
    (player_data['position'].isin(selected_positions)) &
    (player_data['team'].isin(selected_teams))
]

filtered_teams = team_data[team_data['team'].isin(selected_teams)]

# Título principal
st.title("⚽ Análisis de Datos de Fútbol Premier League")
st.markdown("""
Explora estadísticas de jugadores, comparaciones de equipos y análisis de rendimiento basados en datos de la temporada.
""")

# Pestañas
tab1, tab2, tab3, tab4 = st.tabs([
    "🏠 Resumen General", 
    "👤 Jugadores", 
    "👥 Equipos", 
    "📊 Análisis Avanzado"
])

# Tab 1: Resumen General
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Distribución por Edad")
        fig_age = px.histogram(
            filtered_players, x='age', nbins=20, 
            color_discrete_sequence=['#1f77b4'])
        fig_age.update_layout(
            xaxis_title="Edad",
            yaxis_title="Número de Jugadores"
        )
        st.plotly_chart(fig_age, use_container_width=True)
        
    with col2:
        st.subheader("Distribución por Posición")
        pos_counts = filtered_players['position'].value_counts().reset_index()
        pos_counts.columns = ['position', 'count']
        fig_pos = px.pie(
            pos_counts, names='position', values='count',
            hole=0.3, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pos, use_container_width=True)
    
    st.subheader("Top 10 Jugadores por Valor Ofensivo")
    top_players = filtered_players.sort_values('goal_contributions_per_90', ascending=False).head(10)
    st.dataframe(top_players[['name', 'team', 'position', 'age', 'goals', 'assists', 'goal_contributions_per_90']],
                height=400)
    
    st.subheader("Relación Salario-Rendimiento de Equipos")
    fig_team = px.scatter(
        filtered_teams, x='annual', y='total_goals', 
        size='player_count', hover_name='team', 
        color='avg_age', trendline='ols',
        labels={'annual': 'Salario Anual ($)', 'total_goals': 'Goles Totales'},
        color_continuous_scale='Viridis'
    )
    fig_team.update_layout(
        xaxis_title="Salario Anual (Millones $)",
        yaxis_title="Goles Totales"
    )
    st.plotly_chart(fig_team, use_container_width=True)

# Tab 2: Jugadores
with tab2:
    st.subheader("Búsqueda de Jugadores")
    player_search = st.text_input("Buscar jugador por nombre:")
    
    if player_search:
        search_results = filtered_players[
            filtered_players['name'].str.contains(player_search, case=False)
        ]
        if not search_results.empty:
            selected_player = st.selectbox(
                "Selecciona un jugador:", 
                search_results['name']
            )
            player = filtered_players[filtered_players['name'] == selected_player].iloc[0]
            
            col1, col2 = st.columns([1, 3])
            with col1:
                st.subheader(f"**{player['name']}**")
                st.markdown(f"**Equipo:** {player['team']}")
                st.markdown(f"**Posición:** {player['position']}")
                st.markdown(f"**Edad:** {player['age']}")
                st.markdown(f"**Partidos:** {player['played']} ({player['starts']} como titular)")
                st.markdown(f"**Minutos:** {player['minutes']}")
                st.markdown(f"**Goles:** {player['goals']}")
                st.markdown(f"**Asistencias:** {player['assists']}")
                st.markdown(f"**Contribución gol/90:** {player['goal_contributions_per_90']:.2f}")
                
            with col2:
                # Gráfico de radar para estadísticas clave
                categories = ['Goles', 'Asistencias', 'Pases Progresivos', 'Regates Progresivos', 'Goles Esperados']
                values = [
                    player['goals'] / top_players['goals'].max() * 10,
                    player['assists'] / top_players['assists'].max() * 10,
                    player['progressive_passes'] / filtered_players['progressive_passes'].max() * 10,
                    player['progressive_carries'] / filtered_players['progressive_carries'].max() * 10,
                    player['expected_goals'] / filtered_players['expected_goals'].max() * 10
                ]
                
                fig_radar = go.Figure()
                fig_radar.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name=player['name']
                ))
                fig_radar.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
                    showlegend=False,
                    title="Perfil de Rendimiento"
                )
                st.plotly_chart(fig_radar, use_container_width=True)
        else:
            st.warning("No se encontraron jugadores con ese nombre.")
    else:
        st.info("Ingresa un nombre de jugador para buscar.")
    
    st.subheader("Comparador de Jugadores")
    player1 = st.selectbox("Jugador 1:", filtered_players['name'])
    player2 = st.selectbox("Jugador 2:", filtered_players['name'])
    
    if player1 and player2:
        p1 = filtered_players[filtered_players['name'] == player1].iloc[0]
        p2 = filtered_players[filtered_players['name'] == player2].iloc[0]
        
        metrics = ['goals', 'assists', 'minutes', 'progressive_passes', 
                   'progressive_carries', 'expected_goals', 'goal_contributions_per_90']
        labels = ['Goles', 'Asistencias', 'Minutos Jugados', 'Pases Progresivos', 
                  'Regates Progresivos', 'Goles Esperados (xG)', 'Contribución Gol/90']
        
        fig_comparison = go.Figure()
        
        fig_comparison.add_trace(go.Bar(
            x=labels,
            y=[p1[m] for m in metrics],
            name=player1,
            marker_color='#1f77b4'
        ))
        
        fig_comparison.add_trace(go.Bar(
            x=labels,
            y=[p2[m] for m in metrics],
            name=player2,
            marker_color='#ff7f0e'
        ))
        
        fig_comparison.update_layout(
            barmode='group',
            title="Comparación de Jugadores",
            xaxis_tickangle=-45
        )
        st.plotly_chart(fig_comparison, use_container_width=True)

# Tab 3: Equipos
with tab3:
    st.subheader("Comparación de Equipos")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Top 5 Equipos por Salario Anual**")
        top_salary = filtered_teams.sort_values('annual', ascending=False).head(5)
        fig_salary = px.bar(
            top_salary, x='team', y='annual',
            labels={'annual': 'Salario Anual ($)', 'team': 'Equipo'},
            color='team',
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig_salary, use_container_width=True)
        
    with col2:
        st.markdown("**Top 5 Equipos por Eficiencia Ofensiva**")
        top_efficiency = filtered_teams.sort_values('efficiency', ascending=False).head(5)
        fig_efficiency = px.bar(
            top_efficiency, x='team', y='efficiency',
            labels={'efficiency': 'Goles por millón $', 'team': 'Equipo'},
            color='team',
            color_discrete_sequence=px.colors.sequential.Plasma
        )
        st.plotly_chart(fig_efficiency, use_container_width=True)
    
    st.subheader("Análisis Detallado por Equipo")
    selected_team = st.selectbox("Selecciona un equipo:", filtered_teams['team'])
    
    if selected_team:
        team_players = filtered_players[filtered_players['team'] == selected_team]
        team_info = filtered_teams[filtered_teams['team'] == selected_team].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Salario Anual", f"${team_info['annual']:,.0f}")
        col2.metric("Goles Totales", team_info['total_goals'])
        col3.metric("Eficiencia", f"{team_info['efficiency']:.2f} goles/millón $")
        
        st.subheader(f"Jugadores Destacados de {selected_team}")
        
        # Top 3 goleadores
        top_scorers = team_players.sort_values('goals', ascending=False).head(3)
        # Top 3 asistentes
        top_assisters = team_players.sort_values('assists', ascending=False).head(3)
        # Top 3 jóvenes promesas (menores de 21 con más minutos)
        young_promises = team_players[team_players['age'] <= 21].sort_values('minutes', ascending=False).head(3)
        
        tabs = st.tabs(["Goleadores", "Asistentes", "Jóvenes Promesas"])
        
        with tabs[0]:
            st.dataframe(top_scorers[['name', 'position', 'age', 'minutes', 'goals', 'assists']])
        with tabs[1]:
            st.dataframe(top_assisters[['name', 'position', 'age', 'minutes', 'goals', 'assists']])
        with tabs[2]:
            st.dataframe(young_promises[['name', 'position', 'age', 'minutes', 'goals', 'assists']])
        
        st.subheader("Distribución de Posiciones")
        fig_team_pos = px.pie(
            team_players, names='position', 
            color_discrete_sequence=px.colors.qualitative.Pastel,
            hole=0.4
        )
        st.plotly_chart(fig_team_pos, use_container_width=True)

# Tab 4: Análisis Avanzado
with tab4:
    st.subheader("Relación entre Edad y Rendimiento")
    
    col1, col2 = st.columns(2)
    with col1:
        metric = st.selectbox("Métrica de rendimiento:", 
                             ['goals_per_90', 'assists_per_90', 'goal_contributions_per_90'])
    with col2:
        position_filter = st.selectbox("Filtrar por posición:", 
                                      ['Todas'] + list(filtered_players['position'].unique()))
    
    if position_filter != 'Todas':
        plot_data = filtered_players[filtered_players['position'] == position_filter]
    else:
        plot_data = filtered_players
        
    fig_age_perf = px.scatter(
        plot_data, x='age', y=metric, 
        color='position', hover_name='name',
        trendline='lowess',
        labels={
            'goals_per_90': 'Goles por 90 min',
            'assists_per_90': 'Asistencias por 90 min',
            'goal_contributions_per_90': 'Contribución gol por 90 min'
        }
    )
    st.plotly_chart(fig_age_perf, use_container_width=True)
    
    st.subheader("Análisis de Porteros (GK)")
    gk_data = filtered_players[filtered_players['position'] == 'GK']
    if not gk_data.empty:
        fig_gk = px.scatter(
            gk_data, x='minutes', y='played',
            size='age', hover_name='name', color='team',
            labels={'minutes': 'Minutos Jugados', 'played': 'Partidos Jugados'}
        )
        st.plotly_chart(fig_gk, use_container_width=True)
    else:
        st.warning("No hay datos de porteros con los filtros actuales.")
    
    st.subheader("Correlaciones entre Métricas")
    corr_metrics = st.multiselect(
        "Selecciona métricas para matriz de correlación:",
        options=['goals', 'assists', 'minutes', 'age', 'progressive_passes', 
                'progressive_carries', 'expected_goals', 'yellow', 'red'],
        default=['goals', 'assists', 'minutes', 'expected_goals']
    )
    
    if len(corr_metrics) >= 2:
        corr_data = filtered_players[corr_metrics].corr()
        fig_corr = px.imshow(
            corr_data, 
            text_auto=True, 
            aspect="auto",
            color_continuous_scale='RdBu',
            zmin=-1, 
            zmax=1
        )
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Selecciona al menos 2 métricas para generar la matriz de correlación.")

# Footer
st.markdown("---")
st.caption("Datos de jugadores y equipos de la Premier League - Temporada 2023/2024")