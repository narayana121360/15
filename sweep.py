"""
Efficiency and output vs flue gas inlet temperature, for the end of each
cycle tab in app.py.

The curves are the pre-computed temperature sweeps from
Optimization_Final.ipynb (each point is a full cycle solve, too slow to
redo in the app), stored in sweep_data.json:
    t_flue_in_c : flue gas inlet temperature (°C) -- the notebook dict keys
    output_kw   : tuple element [0], net power (kW) or cooling (kW) for LiBr
    energy      : tuple element [3], energy efficiency (%) or COP for LiBr
    exergy_pct  : tuple element [4], exergy efficiency (%); the sCO2 values
                  are already multiplied by 100
Start temperatures: sCO2 230 °C, transcritical CO2 130 °C, steam 190 °C,
ORC and LiBr the full sweep.
"""
import json
import os

KW_PER_TON = 3.517   # 1 ton of refrigeration = 3.517 kW of cooling

RED, BLUE, GREEN = "#d62728", "#1f77b4", "#2ca02c"
TITLES = {"super": "Supercritical CO₂ Brayton Cycle", "trans": "Transcritical CO₂ Rankine Cycle",
          "steam": "Steam Rankine Cycle", "orc": "Organic Rankine Cycle (ORC)",
          "libr": "LiBr Vapour Absorption Cycle"}

_DATA = None


def data(key):
    global _DATA
    if _DATA is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sweep_data.json")
        with open(path) as fh:
            _DATA = json.load(fh)["cycles"]
    return _DATA[key]


def _layout(fig, title):
    fig.update_layout(title_text=title, height=500, hovermode="x unified",
                      margin=dict(l=10, r=10, t=50, b=10),
                      legend=dict(orientation="h", yanchor="top", y=-0.15, x=0.5, xanchor="center"))
    fig.update_xaxes(title_text="Flue gas inlet temperature (°C)")


def power_cycle_figure(key):
    """Energy and exergy efficiency (left axis, %) and net power (right axis, kW)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    d = data(key)
    t = d["t_flue_in_c"]
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=t, y=d["energy"], name="Energy efficiency", line=dict(color=RED, width=2.5),
                             hovertemplate="%{y:.2f} %"), secondary_y=False)
    fig.add_trace(go.Scatter(x=t, y=d["exergy_pct"], name="Exergy efficiency", line=dict(color=BLUE, width=2.5),
                             hovertemplate="%{y:.2f} %"), secondary_y=False)
    fig.add_trace(go.Scatter(x=t, y=d["output_kw"], name="Net power", line=dict(color=GREEN, width=2.5, dash="dash"),
                             hovertemplate="%{y:,.1f} kW"), secondary_y=True)
    _layout(fig, TITLES[key])
    fig.update_yaxes(title_text="Efficiency (%)", secondary_y=False)
    fig.update_yaxes(title_text="Net power (kW)", secondary_y=True, showgrid=False, tickmode="auto",
                     title_font_color=GREEN, tickfont_color=GREEN)
    return fig


def libr_figure():
    """COP (left axis), exergy efficiency (right axis, %) and cooling (second right axis, tons)."""
    import plotly.graph_objects as go
    d = data("libr")
    t = d["t_flue_in_c"]
    tons = [kw / KW_PER_TON for kw in d["output_kw"]]
    cop_max = max(1.0, 1.2 * max(d["energy"]))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=t, y=d["energy"], name="COP", line=dict(color=RED, width=2.5),
                             hovertemplate="%{y:.3f}", yaxis="y"))
    fig.add_trace(go.Scatter(x=t, y=d["exergy_pct"], name="Exergy efficiency", line=dict(color=BLUE, width=2.5),
                             hovertemplate="%{y:.2f} %", yaxis="y2"))
    fig.add_trace(go.Scatter(x=t, y=tons, name="Cooling", line=dict(color=GREEN, width=2.5, dash="dash"),
                             hovertemplate="%{y:,.1f} tons", yaxis="y3"))
    _layout(fig, TITLES["libr"])
    fig.update_layout(
        xaxis=dict(domain=[0, 0.86]),
        # COP is essentially constant across the sweep, so start its axis at 0
        yaxis=dict(title=dict(text="COP", font=dict(color=RED)), tickfont=dict(color=RED), range=[0, cop_max]),
        yaxis2=dict(title=dict(text="Exergy efficiency (%)", font=dict(color=BLUE)), tickfont=dict(color=BLUE),
                    overlaying="y", side="right", anchor="x", showgrid=False, tickmode="auto"),
        yaxis3=dict(title=dict(text="Cooling (tons of refrigeration)", font=dict(color=GREEN)),
                    tickfont=dict(color=GREEN), overlaying="y", side="right", anchor="free",
                    position=0.97, showgrid=False, tickmode="auto"),
    )
    return fig


def figure(key):
    return libr_figure() if key == "libr" else power_cycle_figure(key)
