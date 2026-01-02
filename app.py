def create_gantt_chart_global(df_gantt, title="Gantt Chart"):
    """Crée un Gantt global avec toutes les tâches"""
    if df_gantt.empty:
        return None
    
    fig = px.timeline(
        df_gantt, 
        x_start="Start Date", 
        x_end="End Date", 
        y="Tâche_Projet",
        color="Équipe",
        color_discrete_map=TEAM_COLORS,
        hover_data=["Projet", "Équipe", "Charge", "Dépendance"],
        title=title,
        height=max(600, len(df_gantt) * 30)
    )
    
    # Ajouter les itérations
    colors_bg = ["rgba(230, 230, 230, 0.3)", "rgba(200, 230, 255, 0.3)", "rgba(220, 255, 220, 0.3)", "rgba(255, 220, 220, 0.3)", "rgba(220, 255, 255, 0.3)"]
    for i, it in enumerate(ITERATIONS):
        fig.add_vrect(
            x0=it["start"], x1=it["end"],
            fillcolor=colors_bg[i % len(colors_bg)], 
            layer="below", line_width=0,
            annotation_text=f"<b>{it['name']}</b>", 
            annotation_position="top left",
            annotation_font_size=13
        )
        fig.add_vline(x=it["end"], line_width=2, line_dash="dot", line_color="gray")
    
    # Ajouter les jours fériés
    for hol_date in HOLIDAYS_2026:
        start_hol = pd.to_datetime(hol_date)
        end_hol = start_hol + timedelta(days=1)
        fig.add_vrect(
            x0=start_hol, x1=end_hol,
            fillcolor="rgba(255, 0, 0, 0.2)",
            line_width=0,
            annotation_text="Férié",
            annotation_position="bottom right",
            annotation_font_color="red",
            annotation_font_size=10
        )
    
    # Indicateur date actuelle - CORRECTION
    today_dt = datetime.now()
    fig.add_vline(
        x=today_dt,
        line_width=3,
        line_dash="solid",
        line_color="rgb(255, 0, 0)",
        annotation_text="📍 AUJOURD'HUI",
        annotation_position="top",
        annotation_font_size=12,
        annotation_font_color="red"
    )

    first_iteration_start = ITERATIONS[0]["start"]
    last_iteration_end = ITERATIONS[-1]["end"]
    
    fig.update_xaxes(
        range=[first_iteration_start, last_iteration_end],
        tickformat="%a %d/%m",
        dtick=86400000.0,
        side="top",
        tickfont=dict(size=11),
        rangebreaks=[dict(bounds=["sat", "mon"])]
    )
    fig.update_yaxes(autorange="reversed")
    
    return fig
