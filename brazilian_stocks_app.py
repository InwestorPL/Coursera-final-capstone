"""
Cotações B3 - Dashboard de Ações Brasileiras
--------------------------------------------
Demo com dados simulados baseados em preços reais de referência.
Em produção, substitua `fetch_quote()` e `fetch_history()` pela
chamada à API de sua preferência (brapi.dev, Yahoo Finance, etc.).
"""

import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# ---------------------------------------------------------------------------
# Configuração das ações
# ---------------------------------------------------------------------------
STOCKS = {
    "PETR4": {"name": "Petrobras PN", "sector": "Energia",           "base_price": 38.50},
    "VALE3": {"name": "Vale",          "sector": "Mineração",         "base_price": 62.30},
    "ITUB4": {"name": "Itaú Unibanco", "sector": "Financeiro",        "base_price": 34.80},
    "BBDC4": {"name": "Bradesco PN",   "sector": "Financeiro",        "base_price": 14.20},
    "BBAS3": {"name": "Banco do Brasil","sector": "Financeiro",       "base_price": 27.10},
    "B3SA3": {"name": "B3",            "sector": "Financeiro",        "base_price": 11.80},
    "ABEV3": {"name": "Ambev",         "sector": "Consumo",           "base_price": 11.50},
    "WEGE3": {"name": "WEG",           "sector": "Indústria",         "base_price": 52.40},
    "MGLU3": {"name": "Magazine Luiza","sector": "Varejo",            "base_price":  7.30},
    "RENT3": {"name": "Localiza",      "sector": "Mobilidade",        "base_price": 43.60},
    "ELET3": {"name": "Eletrobras ON", "sector": "Energia",           "base_price": 41.20},
    "SUZB3": {"name": "Suzano",        "sector": "Papel e Celulose",  "base_price": 54.90},
    "GGBR4": {"name": "Gerdau PN",     "sector": "Siderurgia",        "base_price": 19.40},
    "RDOR3": {"name": "Rede D'Or",     "sector": "Saúde",             "base_price": 32.80},
    "VBBR3": {"name": "Vibra Energia", "sector": "Energia",           "base_price": 22.10},
}

PERIODS = {
    "1 Semana":  7,
    "1 Mês":    30,
    "3 Meses":  90,
    "6 Meses": 180,
    "1 Ano":   365,
    "2 Anos":  730,
}

DEFAULT_STOCKS = ["PETR4", "VALE3", "ITUB4", "BBDC4", "ABEV3"]

SECTOR_COLORS = {
    "Energia":         "#f4a261",
    "Mineração":       "#e76f51",
    "Financeiro":      "#457b9d",
    "Consumo":         "#2a9d8f",
    "Indústria":       "#264653",
    "Varejo":          "#e9c46a",
    "Mobilidade":      "#6d6875",
    "Papel e Celulose":"#81b29a",
    "Siderurgia":      "#7e6551",
    "Saúde":           "#e07a5f",
}


# ---------------------------------------------------------------------------
# Simulação de dados (substitua por chamadas reais de API em produção)
# ---------------------------------------------------------------------------

def _rng_for(code):
    """Semente determinística por código para reprodutibilidade dentro da sessão."""
    return np.random.default_rng(hash(code + datetime.now().strftime("%Y%m%d%H")) % (2**32))


def fetch_quote(code):
    """Retorna cotação simulada para o código de ação fornecido."""
    rng = _rng_for(code)
    base = STOCKS[code]["base_price"]
    # Variação diária aleatória: ±3 %
    pct = rng.uniform(-3.0, 3.0)
    price = round(base * (1 + pct / 100), 2)
    prev = round(base, 2)
    change = round(price - prev, 2)
    volume = int(rng.integers(1_000_000, 50_000_000))
    high = round(price * rng.uniform(1.001, 1.02), 2)
    low = round(price * rng.uniform(0.98, 0.999), 2)
    return {
        "price": price,
        "change": change,
        "pct_change": pct,
        "volume": volume,
        "high": high,
        "low": low,
    }


def fetch_history(code, days):
    """Gera histórico de preços simulado via random walk."""
    rng = _rng_for(code + "hist")
    base = STOCKS[code]["base_price"]
    end = datetime.today()
    dates = pd.date_range(end=end, periods=days, freq="B")  # dias úteis
    # Random walk com drift levemente positivo
    returns = rng.normal(loc=0.0002, scale=0.015, size=len(dates))
    prices = base * np.cumprod(1 + returns)
    prices[-1] = round(fetch_quote(code)["price"], 2)

    df = pd.DataFrame({
        "Close": prices,
        "Open":  prices * rng.uniform(0.99, 1.01, size=len(dates)),
        "High":  prices * rng.uniform(1.00, 1.02, size=len(dates)),
        "Low":   prices * rng.uniform(0.98, 1.00, size=len(dates)),
        "Volume": rng.integers(1_000_000, 50_000_000, size=len(dates)),
    }, index=dates)
    return df


# ---------------------------------------------------------------------------
# Componentes visuais
# ---------------------------------------------------------------------------

def price_card(code, data):
    info = STOCKS[code]
    if data is None:
        return dbc.Card(
            dbc.CardBody([
                html.H5(code, className="fw-bold"),
                html.P("Dados indisponíveis", className="text-danger"),
            ]),
            className="h-100 shadow-sm border-0",
        )

    up = data["change"] >= 0
    color = "success" if up else "danger"
    arrow = "▲" if up else "▼"
    sector_color = SECTOR_COLORS.get(info["sector"], "#888")

    return dbc.Card([
        html.Div(style={"height": "4px", "backgroundColor": sector_color,
                        "borderRadius": "4px 4px 0 0"}),
        dbc.CardBody([
            html.Div([
                html.Span(code, className="fw-bold fs-6 me-2"),
                dbc.Badge(info["sector"], className="small",
                          style={"backgroundColor": sector_color}),
            ], className="mb-1"),
            html.Small(info["name"], className="text-muted d-block mb-2"),
            html.H4(f"R$ {data['price']:.2f}", className="fw-bold mb-1"),
            html.Div([
                html.Span(f"{arrow} R$ {abs(data['change']):.2f}",
                          className=f"text-{color} fw-semibold"),
                html.Span(f" ({data['pct_change']:+.2f}%)",
                          className=f"text-{color}"),
            ]),
            html.Hr(className="my-2"),
            dbc.Row([
                dbc.Col(html.Small(
                    [html.Span("Max ", className="text-muted"), f"R$ {data['high']:.2f}"]
                )),
                dbc.Col(html.Small(
                    [html.Span("Min ", className="text-muted"), f"R$ {data['low']:.2f}"]
                )),
            ], className="gx-1"),
            html.Small(
                [html.Span("Vol ", className="text-muted"),
                 f"{data['volume'] / 1_000_000:.1f}M"],
                className="d-block mt-1",
            ),
        ]),
    ], className="h-100 shadow-sm border-0")


# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP],
    title="Cotações B3 – Ações Brasileiras",
)
server = app.server  # expõe o servidor Flask para deploy (gunicorn, etc.)

app.layout = dbc.Container([
    dcc.Interval(id="auto-refresh", interval=60_000, n_intervals=0),

    # ── Cabeçalho ─────────────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            html.H2([
                html.I(className="bi bi-graph-up-arrow text-success me-2"),
                "Cotações B3",
            ], className="fw-bold mb-0"),
            html.P("Principais ações da bolsa brasileira · Atualização a cada 60 s",
                   className="text-muted small mb-0"),
        ]),
        dbc.Col(
            html.Small(id="last-update", className="text-muted fst-italic"),
            className="d-flex align-items-center justify-content-end",
            width="auto",
        ),
    ], className="py-3 border-bottom mb-3 align-items-center"),

    # ── Aviso de dados simulados ───────────────────────────────────────────
    dbc.Alert([
        html.I(className="bi bi-info-circle me-2"),
        "Demonstração com ",
        html.Strong("dados simulados"),
        ". Em produção, conecte as funções ",
        html.Code("fetch_quote()"),
        " e ",
        html.Code("fetch_history()"),
        " à API de sua preferência (brapi.dev, Yahoo Finance, etc.).",
    ], color="info", className="small py-2 mb-3", dismissable=True),

    # ── Controles ─────────────────────────────────────────────────────────
    dbc.Card(dbc.CardBody(
        dbc.Row([
            dbc.Col([
                html.Label("Ações exibidas", className="fw-semibold small mb-1"),
                dcc.Dropdown(
                    id="stock-selector",
                    options=[
                        {"label": f"{c} – {v['name']}", "value": c}
                        for c, v in STOCKS.items()
                    ],
                    value=DEFAULT_STOCKS,
                    multi=True,
                    placeholder="Selecione as ações…",
                ),
            ], md=8),
            dbc.Col([
                html.Label("Período do gráfico", className="fw-semibold small mb-1"),
                dcc.Dropdown(
                    id="period-selector",
                    options=[{"label": k, "value": v} for k, v in PERIODS.items()],
                    value=30,
                    clearable=False,
                ),
            ], md=4),
        ])
    ), className="shadow-sm border-0 mb-3"),

    # ── Cards de preço ────────────────────────────────────────────────────
    html.Div(id="cards-container", className="mb-3"),

    # ── Gráfico + tabela ──────────────────────────────────────────────────
    dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    dbc.Row([
                        dbc.Col(html.Span("Histórico de Preços", className="fw-semibold")),
                        dbc.Col(
                            dcc.Dropdown(
                                id="chart-stock-selector",
                                options=[
                                    {"label": f"{c} – {v['name']}", "value": c}
                                    for c, v in STOCKS.items()
                                ],
                                value="PETR4",
                                clearable=False,
                            ),
                            width=5,
                        ),
                    ], align="center"),
                    className="bg-white border-bottom",
                ),
                dbc.CardBody(
                    dcc.Graph(id="price-chart",
                              config={"displayModeBar": False},
                              style={"height": "380px"}),
                    className="p-1",
                ),
            ], className="shadow-sm border-0"),
        ], md=8, className="mb-3"),

        dbc.Col([
            dbc.Card([
                dbc.CardHeader(
                    html.Span("Resumo", className="fw-semibold"),
                    className="bg-white border-bottom",
                ),
                dbc.CardBody(html.Div(id="summary-table"), className="p-0"),
            ], className="shadow-sm border-0"),
        ], md=4, className="mb-3"),
    ]),

    # ── Rodapé ────────────────────────────────────────────────────────────
    html.Footer(
        html.Small([
            html.I(className="bi bi-bar-chart-fill me-1"),
            "Dados simulados para fins de demonstração. "
            "Conecte à API real para cotações ao vivo.",
        ], className="text-muted"),
        className="text-center py-3 border-top",
    ),
], fluid=True, className="px-4 bg-light min-vh-100")


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@app.callback(
    Output("cards-container", "children"),
    Output("last-update", "children"),
    Input("stock-selector", "value"),
    Input("auto-refresh", "n_intervals"),
)
def update_cards(selected, _):
    if not selected:
        return html.P("Nenhuma ação selecionada.", className="text-muted"), ""

    cards = [
        dbc.Col(price_card(code, fetch_quote(code)), md=4, lg=3, xl=2, className="mb-3")
        for code in selected
    ]
    now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    return dbc.Row(cards, className="g-2"), f"Última atualização: {now}"


@app.callback(
    Output("price-chart", "figure"),
    Input("chart-stock-selector", "value"),
    Input("period-selector", "value"),
    Input("auto-refresh", "n_intervals"),
)
def update_chart(code, days, _):
    if not code:
        return go.Figure()

    hist = fetch_history(code, days)
    if hist.empty:
        return go.Figure()

    up = hist["Close"].iloc[-1] >= hist["Close"].iloc[0]
    line_color = "#28a745" if up else "#dc3545"
    fill_color = "rgba(40,167,69,0.07)" if up else "rgba(220,53,69,0.07)"

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["Close"].round(2),
        mode="lines",
        line=dict(color=line_color, width=2),
        fill="tozeroy", fillcolor=fill_color,
        name="Fechamento",
        hovertemplate="<b>%{x|%d/%m/%Y}</b><br>R$ %{y:.2f}<extra></extra>",
    ))

    fig.add_trace(go.Bar(
        x=hist.index, y=hist["Volume"],
        name="Volume",
        yaxis="y2",
        marker_color="rgba(120,120,200,0.25)",
        hovertemplate="Volume: %{y:,.0f}<extra></extra>",
    ))

    period_label = {v: k for k, v in PERIODS.items()}.get(days, f"{days} dias")
    name = STOCKS[code]["name"]

    fig.update_layout(
        title=dict(text=f"{code} – {name} | {period_label}", x=0.01,
                   font=dict(size=13, color="#333")),
        yaxis=dict(title="Preço (R$)", tickprefix="R$ ",
                   showgrid=True, gridcolor="#f0f0f0", zeroline=False),
        yaxis2=dict(title="Volume", overlaying="y", side="right",
                    showgrid=False, tickformat=","),
        xaxis=dict(showgrid=False, zeroline=False),
        plot_bgcolor="white", paper_bgcolor="white",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(l=10, r=10, t=50, b=10),
        hovermode="x unified",
    )
    return fig


@app.callback(
    Output("summary-table", "children"),
    Input("stock-selector", "value"),
    Input("auto-refresh", "n_intervals"),
)
def update_table(selected, _):
    if not selected:
        return html.P("Nenhuma ação.", className="text-muted p-3")

    rows = []
    for code in selected:
        data = fetch_quote(code)
        if data:
            up = data["change"] >= 0
            color = "text-success" if up else "text-danger"
            arrow = "▲" if up else "▼"
            rows.append(html.Tr([
                html.Td(html.Span(code, className="fw-semibold"), className="ps-3"),
                html.Td(f"R$ {data['price']:.2f}"),
                html.Td(html.Span(
                    f"{arrow} {data['pct_change']:+.2f}%", className=f"{color} fw-semibold"
                )),
            ]))
        else:
            rows.append(html.Tr([
                html.Td(code, className="ps-3"), html.Td("–"), html.Td("–"),
            ]))

    return dbc.Table(
        [
            html.Thead(html.Tr([
                html.Th("Ação", className="ps-3"), html.Th("Preço"), html.Th("Var. %"),
            ]), className="table-light"),
            html.Tbody(rows),
        ],
        bordered=False, hover=True, responsive=True, size="sm", className="mb-0",
    )


@app.callback(
    Output("chart-stock-selector", "value"),
    Input("stock-selector", "value"),
    Input("chart-stock-selector", "value"),
)
def sync_chart_stock(selected, current):
    if selected and current not in selected:
        return selected[0]
    return current or "PETR4"


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
