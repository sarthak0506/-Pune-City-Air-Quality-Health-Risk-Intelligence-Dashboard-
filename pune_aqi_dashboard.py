import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go

# ── Load & Prep Data ─────────────────────────────────────────────
df = pd.read_excel("Pune_AQI_Dataset.xlsx", sheet_name="Daily_AQI")
df["Date"] = pd.to_datetime(df["Date"])
df["Year"]  = df["Year"].astype(str)

monthly = df.groupby(["Year","Month","Month_Name","Season","Ward","Zone","Ward_Type"]).agg(
    Avg_AQI=("AQI","mean"),
    Avg_PM25=("PM25","mean"),
    Avg_NO2=("NO2","mean"),
    Avg_CO=("CO","mean"),
    Avg_HRS=("Health_Risk_Score","mean"),
    Total_Hosp=("Hosp_Admissions","sum"),
    Unhealthy_Days=("AQI_Category", lambda x: x.isin(["Poor","Very Poor","Severe"]).sum())
).reset_index().round(1)

monthly["YearMonth"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)

# ── Constants ────────────────────────────────────────────────────
AQI_COLORS = {
    "Good":         "#00B050",
    "Satisfactory": "#92D050",
    "Moderate":     "#FFC000",
    "Poor":         "#FF6600",
    "Very Poor":    "#FF0000",
    "Severe":       "#7030A0"
}

ZONES    = sorted(df["Zone"].unique())
YEARS    = sorted(df["Year"].unique())
SEASONS  = sorted(df["Season"].unique())
WARDS    = sorted(df["Ward"].unique())

CARD_STYLE = {
    "background": "#1E2130",
    "borderRadius": "12px",
    "padding": "18px 20px",
    "textAlign": "center",
    "border": "1px solid #2D3250"
}

SIDEBAR_STYLE = {
    "background": "#161927",
    "borderRadius": "14px",
    "padding": "20px",
    "border": "1px solid #2D3250"
}

PLOT_THEME = dict(
    paper_bgcolor="#1E2130",
    plot_bgcolor="#1E2130",
    font=dict(color="#C8CDD8", family="Inter, sans-serif", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    colorway=["#4E8EF7","#F7B731","#FC5C65","#26de81","#fd9644","#a55eea"]
)

# ── App ──────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.CYBORG,
        "https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
    ],
    title="Pune AQI Dashboard"
)

def kpi_card(title, id_val, unit="", color="#4E8EF7"):
    return html.Div([
        html.P(title, style={"color":"#8899AA","fontSize":"11px","marginBottom":"4px","textTransform":"uppercase","letterSpacing":"1px"}),
        html.H3(id=id_val, style={"color": color,"fontSize":"28px","fontWeight":"700","margin":"0"}),
        html.Span(unit, style={"color":"#8899AA","fontSize":"11px"})
    ], style=CARD_STYLE)

app.layout = html.Div([

    # ── Header ──
    html.Div([
        html.Div([
            html.H1("🌫️ Pune City Air Quality & Health Risk Dashboard",
                    style={"color":"#E8ECF4","fontSize":"22px","fontWeight":"700","margin":"0"}),
            html.P("Daily AQI tracking across 20 wards | 2022–2024 | Source: CPCB India",
                   style={"color":"#8899AA","fontSize":"12px","margin":"4px 0 0"})
        ]),
        html.Div(id="last-updated", style={"color":"#8899AA","fontSize":"12px","alignSelf":"center"})
    ], style={"display":"flex","justifyContent":"space-between","alignItems":"flex-start",
              "background":"#161927","padding":"20px 28px","borderBottom":"1px solid #2D3250",
              "marginBottom":"20px"}),

    # ── Body ──
    html.Div([

        # ── Sidebar ──
        html.Div([
            html.Div([
                html.Label("Year", style={"color":"#8899AA","fontSize":"11px","textTransform":"uppercase","letterSpacing":"1px"}),
                dcc.Checklist(
                    id="filter-year",
                    options=[{"label": f" {y}", "value": y} for y in YEARS],
                    value=YEARS,
                    style={"color":"#C8CDD8","fontSize":"13px"},
                    inputStyle={"marginRight":"6px","accentColor":"#4E8EF7"}
                )
            ], style={"marginBottom":"20px"}),

            html.Div([
                html.Label("Season", style={"color":"#8899AA","fontSize":"11px","textTransform":"uppercase","letterSpacing":"1px"}),
                dcc.Checklist(
                    id="filter-season",
                    options=[{"label": f" {s}", "value": s} for s in SEASONS],
                    value=SEASONS,
                    style={"color":"#C8CDD8","fontSize":"13px"},
                    inputStyle={"marginRight":"6px","accentColor":"#4E8EF7"}
                )
            ], style={"marginBottom":"20px"}),

            html.Div([
                html.Label("Zone", style={"color":"#8899AA","fontSize":"11px","textTransform":"uppercase","letterSpacing":"1px"}),
                dcc.Checklist(
                    id="filter-zone",
                    options=[{"label": f" {z}", "value": z} for z in ZONES],
                    value=ZONES,
                    style={"color":"#C8CDD8","fontSize":"13px"},
                    inputStyle={"marginRight":"6px","accentColor":"#4E8EF7"}
                )
            ], style={"marginBottom":"20px"}),

            html.Div([
                html.Label("Ward Type", style={"color":"#8899AA","fontSize":"11px","textTransform":"uppercase","letterSpacing":"1px"}),
                dcc.Checklist(
                    id="filter-wardtype",
                    options=[{"label": f" {w}", "value": w} for w in ["Industrial","Traffic","Residential"]],
                    value=["Industrial","Traffic","Residential"],
                    style={"color":"#C8CDD8","fontSize":"13px"},
                    inputStyle={"marginRight":"6px","accentColor":"#4E8EF7"}
                )
            ], style={"marginBottom":"20px"}),

            html.Hr(style={"borderColor":"#2D3250"}),

            html.Div([
                html.Label("AQI Threshold Line", style={"color":"#8899AA","fontSize":"11px","textTransform":"uppercase","letterSpacing":"1px"}),
                dcc.Slider(id="aqi-threshold", min=50, max=300, step=50, value=100,
                           marks={50:"50",100:"100",200:"200",300:"300"},
                           tooltip={"placement":"bottom"})
            ])

        ], style={**SIDEBAR_STYLE, "width":"200px","minWidth":"200px","height":"fit-content"}),

        # ── Main Content ──
        html.Div([

            # ── KPI Row ──
            html.Div([
                kpi_card("Avg AQI",            "kpi-aqi",    "",        "#F7B731"),
                kpi_card("Avg PM2.5",          "kpi-pm25",   "µg/m³",   "#FC5C65"),
                kpi_card("Health Risk Score",  "kpi-hrs",    "/100",    "#fd9644"),
                kpi_card("Unhealthy Days",     "kpi-bad",    "%",       "#a55eea"),
                kpi_card("Hosp Admissions",    "kpi-hosp",   "total",   "#26de81"),
            ], style={"display":"grid","gridTemplateColumns":"repeat(5,1fr)","gap":"12px","marginBottom":"16px"}),

            # ── Row 1: AQI trend + AQI category donut ──
            html.Div([
                html.Div([dcc.Graph(id="chart-trend", style={"height":"280px"})],
                         style={"flex":"2","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
                html.Div([dcc.Graph(id="chart-donut", style={"height":"280px"})],
                         style={"flex":"1","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
            ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

            # ── Row 2: Ward AQI bar + Pollutant comparison ──
            html.Div([
                html.Div([dcc.Graph(id="chart-ward-bar", style={"height":"300px"})],
                         style={"flex":"1","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
                html.Div([dcc.Graph(id="chart-pollutant", style={"height":"300px"})],
                         style={"flex":"1","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
            ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

            # ── Row 3: Seasonal heatmap + Scatter (PM2.5 vs Hosp) ──
            html.Div([
                html.Div([dcc.Graph(id="chart-seasonal", style={"height":"320px"})],
                         style={"flex":"1","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
                html.Div([dcc.Graph(id="chart-scatter", style={"height":"320px"})],
                         style={"flex":"1","background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),
            ], style={"display":"flex","gap":"14px","marginBottom":"14px"}),

            # ── Row 4: Health Risk leaderboard table ──
            html.Div([
                dcc.Graph(id="chart-heatmap", style={"height":"320px"})
            ], style={"background":"#1E2130","borderRadius":"12px","border":"1px solid #2D3250","overflow":"hidden"}),

        ], style={"flex":"1","minWidth":"0"})

    ], style={"display":"flex","gap":"16px","padding":"0 24px 24px"}),

], style={"background":"#0F1120","minHeight":"100vh","fontFamily":"Inter, sans-serif"})


# ── Helper: filter dataframe ─────────────────────────────────────
def filter_df(years, seasons, zones, ward_types):
    mask = (
        df["Year"].isin(years) &
        df["Season"].isin(seasons) &
        df["Zone"].isin(zones) &
        df["Ward_Type"].isin(ward_types)
    )
    return df[mask]

def filter_monthly(years, seasons, zones, ward_types):
    mask = (
        monthly["Year"].isin(years) &
        monthly["Season"].isin(seasons) &
        monthly["Zone"].isin(zones) &
        monthly["Ward_Type"].isin(ward_types)
    )
    return monthly[mask]


# ── Callbacks ────────────────────────────────────────────────────
@callback(
    Output("kpi-aqi",  "children"),
    Output("kpi-pm25", "children"),
    Output("kpi-hrs",  "children"),
    Output("kpi-bad",  "children"),
    Output("kpi-hosp", "children"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_kpis(years, seasons, zones, ward_types):
    d = filter_df(years, seasons, zones, ward_types)
    if d.empty:
        return ["—"]*5
    avg_aqi  = round(d["AQI"].mean(), 1)
    avg_pm25 = round(d["PM25"].mean(), 1)
    avg_hrs  = round(d["Health_Risk_Score"].mean(), 1)
    bad_pct  = round(d["AQI_Category"].isin(["Poor","Very Poor","Severe"]).mean() * 100, 1)
    hosp     = f"{d['Hosp_Admissions'].sum():,}"
    return avg_aqi, avg_pm25, avg_hrs, f"{bad_pct}%", hosp


@callback(
    Output("chart-trend", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
    Input("aqi-threshold",   "value"),
)
def update_trend(years, seasons, zones, ward_types, threshold):
    m = filter_monthly(years, seasons, zones, ward_types)
    if m.empty:
        return go.Figure()
    trend = m.groupby("YearMonth")["Avg_AQI"].mean().reset_index().sort_values("YearMonth")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=trend["YearMonth"], y=trend["Avg_AQI"],
        mode="lines", name="Avg AQI",
        line=dict(color="#4E8EF7", width=2),
        fill="tozeroy", fillcolor="rgba(78,142,247,0.08)"
    ))
    fig.add_hline(y=threshold, line_dash="dash", line_color="#F7B731",
                  annotation_text=f"Threshold: {threshold}", annotation_font_color="#F7B731")
    fig.update_layout(**PLOT_THEME, title="Monthly AQI Trend",
                      xaxis=dict(showgrid=False, tickangle=-45, tickfont_size=9),
                      yaxis=dict(showgrid=True, gridcolor="#2D3250"),
                      showlegend=False)
    return fig


@callback(
    Output("chart-donut", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_donut(years, seasons, zones, ward_types):
    d = filter_df(years, seasons, zones, ward_types)
    if d.empty:
        return go.Figure()
    counts = d["AQI_Category"].value_counts().reset_index()
    counts.columns = ["Category","Count"]
    order = ["Good","Satisfactory","Moderate","Poor","Very Poor","Severe"]
    counts["Category"] = pd.Categorical(counts["Category"], categories=order, ordered=True)
    counts = counts.sort_values("Category")
    fig = go.Figure(go.Pie(
        labels=counts["Category"], values=counts["Count"],
        hole=0.55,
        marker_colors=[AQI_COLORS.get(c,"#888") for c in counts["Category"]],
        textfont_size=11
    ))
    fig.update_layout(**PLOT_THEME, title="AQI Category Distribution",
                      legend=dict(font_size=10, bgcolor="rgba(0,0,0,0)"))
    return fig


@callback(
    Output("chart-ward-bar", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_ward_bar(years, seasons, zones, ward_types):
    m = filter_monthly(years, seasons, zones, ward_types)
    if m.empty:
        return go.Figure()
    ward_aqi = m.groupby(["Ward","Ward_Type"])["Avg_AQI"].mean().reset_index().sort_values("Avg_AQI", ascending=True)
    color_map = {"Industrial":"#FC5C65","Traffic":"#F7B731","Residential":"#26de81"}
    fig = go.Figure(go.Bar(
        x=ward_aqi["Avg_AQI"], y=ward_aqi["Ward"],
        orientation="h",
        marker_color=[color_map.get(t,"#4E8EF7") for t in ward_aqi["Ward_Type"]],
        text=ward_aqi["Avg_AQI"].round(0).astype(int),
        textposition="outside", textfont=dict(size=10, color="#C8CDD8")
    ))
    fig.update_layout(**PLOT_THEME, title="Avg AQI by Ward",
                      xaxis=dict(showgrid=True, gridcolor="#2D3250"),
                      yaxis=dict(showgrid=False, tickfont_size=10),
                      bargap=0.25)
    return fig


@callback(
    Output("chart-pollutant", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_pollutant(years, seasons, zones, ward_types):
    m = filter_monthly(years, seasons, zones, ward_types)
    if m.empty:
        return go.Figure()
    season_poll = m.groupby("Season")[["Avg_PM25","Avg_NO2","Avg_CO"]].mean().reset_index()
    season_order = ["Winter","Post-Monsoon","Summer","Monsoon"]
    season_poll["Season"] = pd.Categorical(season_poll["Season"], categories=season_order, ordered=True)
    season_poll = season_poll.sort_values("Season")
    fig = go.Figure()
    for col, color, name in [
        ("Avg_PM25","#FC5C65","PM2.5 (µg/m³)"),
        ("Avg_NO2", "#F7B731","NO2 (µg/m³)"),
        ("Avg_CO",  "#4E8EF7","CO (×10 mg/m³)")
    ]:
        vals = season_poll[col] * (10 if col == "Avg_CO" else 1)
        fig.add_trace(go.Bar(name=name, x=season_poll["Season"], y=vals.round(1),
                             marker_color=color))
    fig.update_layout(**PLOT_THEME, title="Pollutants by Season",
                      barmode="group",
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=True, gridcolor="#2D3250"),
                      legend=dict(font_size=10, bgcolor="rgba(0,0,0,0)"))
    return fig


@callback(
    Output("chart-seasonal", "figure"),
    Input("filter-year",     "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_seasonal(years, zones, ward_types):
    m = monthly[
        monthly["Year"].isin(years) &
        monthly["Zone"].isin(zones) &
        monthly["Ward_Type"].isin(ward_types)
    ]
    if m.empty:
        return go.Figure()
    hm = m.groupby(["Ward","Season"])["Avg_AQI"].mean().reset_index()
    hm_pivot = hm.pivot(index="Ward", columns="Season", values="Avg_AQI").fillna(0)
    season_order = [s for s in ["Winter","Post-Monsoon","Summer","Monsoon"] if s in hm_pivot.columns]
    hm_pivot = hm_pivot[season_order]
    fig = go.Figure(go.Heatmap(
        z=hm_pivot.values,
        x=hm_pivot.columns.tolist(),
        y=hm_pivot.index.tolist(),
        colorscale=[[0,"#00B050"],[0.33,"#FFC000"],[0.66,"#FF6600"],[1,"#C00000"]],
        text=hm_pivot.values.round(0),
        texttemplate="%{text}",
        textfont=dict(size=9),
        showscale=True
    ))
    fig.update_layout(**PLOT_THEME, title="Ward × Season AQI Heatmap",
                      xaxis=dict(showgrid=False),
                      yaxis=dict(showgrid=False, tickfont_size=9))
    return fig


@callback(
    Output("chart-scatter", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_scatter(years, seasons, zones, ward_types):
    m = filter_monthly(years, seasons, zones, ward_types)
    if m.empty:
        return go.Figure()
    ward_agg = m.groupby(["Ward","Ward_Type"]).agg(
        Avg_PM25=("Avg_PM25","mean"),
        Total_Hosp=("Total_Hosp","sum"),
        Avg_HRS=("Avg_HRS","mean")
    ).reset_index()
    color_map = {"Industrial":"#FC5C65","Traffic":"#F7B731","Residential":"#26de81"}
    fig = go.Figure()
    for wtype, grp in ward_agg.groupby("Ward_Type"):
        fig.add_trace(go.Scatter(
            x=grp["Avg_PM25"], y=grp["Total_Hosp"],
            mode="markers+text",
            name=wtype,
            text=grp["Ward"],
            textposition="top center",
            textfont=dict(size=8),
            marker=dict(size=grp["Avg_HRS"]/3, color=color_map.get(wtype,"#888"),
                        opacity=0.8, line=dict(width=0.5, color="#0F1120"))
        ))
    fig.update_layout(**PLOT_THEME, title="PM2.5 vs Hospital Admissions (size = Health Risk)",
                      xaxis=dict(title="Avg PM2.5 (µg/m³)", showgrid=True, gridcolor="#2D3250"),
                      yaxis=dict(title="Total Hosp Admissions", showgrid=True, gridcolor="#2D3250"),
                      legend=dict(font_size=10, bgcolor="rgba(0,0,0,0)"))
    return fig


@callback(
    Output("chart-heatmap", "figure"),
    Input("filter-year",     "value"),
    Input("filter-season",   "value"),
    Input("filter-zone",     "value"),
    Input("filter-wardtype", "value"),
)
def update_heatmap(years, seasons, zones, ward_types):
    m = filter_monthly(years, seasons, zones, ward_types)
    if m.empty:
        return go.Figure()
    tbl = m.groupby(["Ward","Zone","Ward_Type"]).agg(
        Avg_AQI=("Avg_AQI","mean"),
        Avg_PM25=("Avg_PM25","mean"),
        Avg_HRS=("Avg_HRS","mean"),
        Total_Hosp=("Total_Hosp","sum"),
        Unhealthy_Days=("Unhealthy_Days","sum")
    ).reset_index().sort_values("Avg_HRS", ascending=False).round(1)

    def color_aqi(val):
        if val <= 50:   return "#00B050"
        elif val <= 100: return "#92D050"
        elif val <= 200: return "#FFC000"
        elif val <= 300: return "#FF6600"
        else:            return "#C00000"

    fig = go.Figure(go.Table(
        header=dict(
            values=["<b>Ward</b>","<b>Zone</b>","<b>Type</b>","<b>Avg AQI</b>",
                    "<b>Avg PM2.5</b>","<b>Health Risk</b>","<b>Hosp Admissions</b>","<b>Unhealthy Days</b>"],
            fill_color="#2D3250", font=dict(color="#E8ECF4", size=11),
            align="left", height=32
        ),
        cells=dict(
            values=[tbl["Ward"].tolist(), tbl["Zone"].tolist(), tbl["Ward_Type"].tolist(),
                    tbl["Avg_AQI"].tolist(), tbl["Avg_PM25"].tolist(),
                    tbl["Avg_HRS"].tolist(), tbl["Total_Hosp"].tolist(), tbl["Unhealthy_Days"].tolist()],
            fill_color=[
                ["#1E2130"] * len(tbl),
                ["#1E2130"] * len(tbl),
                ["#1E2130"] * len(tbl),
                [color_aqi(v) for v in tbl["Avg_AQI"]],
                ["#1E2130"] * len(tbl),
                [f"rgba(253,150,68,{min(v/100,1):.2f})" for v in tbl["Avg_HRS"]],
                ["#1E2130"] * len(tbl),
                ["#1E2130"] * len(tbl),
            ],
            font=dict(color="#C8CDD8", size=11),
            align="left", height=28
        )
    ))
    fig.update_layout(**PLOT_THEME, title="Ward Health Risk Leaderboard",
                      margin=dict(l=10,r=10,t=40,b=10))
    return fig


if __name__ == "__main__":
    app.run(debug=True, port=8050)
