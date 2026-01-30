# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown',
                                    options=([{'label': 'All Sites', 'value': 'ALL'}] +
                                            [{'label': site, 'value': site}
                                            for site in sorted(spacex_df['Launch Site'].unique())]),
                                    value='ALL',  # valor inicial: todos os sites
                                    placeholder='Select a Launch Site here',
                                    searchable=True,            # permite digitar para pesquisar
                                    clearable=False,            # evita o estado "vazio" (opcional, mas útil)
                                    style={'width': '60%', 'margin': '0 auto'}  # apenas estética
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                
                                dcc.RangeSlider(
                                    id='payload-slider',              # id do componente (usaremos no callback do scatter)
                                    min=0,                            # início do slider (kg)
                                    max=10000,                        # fim do slider (kg)
                                    step=1000,                        # passo de 1000 kg
                                    value=[int(min_payload), int(max_payload)],  # intervalo selecionado inicialmente
                                    marks={
                                        0: '0',
                                        2500: '2500',
                                        5000: '5000',
                                        7500: '7500',
                                        10000: '10000'
                                    },
                                    tooltip={'placement': 'bottom', 'always_visible': False}
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    """
    Atualiza o gráfico de pizza de acordo com o site selecionado no dropdown.

    - Se 'ALL': Mostra o total de lançamentos bem-sucedidos por site (soma da coluna 'class').
    - Se site específico: Mostra a proporção de Sucesso (class=1) vs Falha (class=0) naquele site.
    """
    # Caso 1: Todos os sites selecionados
    if entered_site == 'ALL':
        # Agrupa por site e soma a coluna 'class' (1=sucesso, 0=falha) → total de sucessos por site
        success_by_site = (
            spacex_df.groupby('Launch Site', as_index=False)['class']
            .sum()
            .rename(columns={'class': 'Successful Launches'})
        )

        # Cria o gráfico de pizza com nomes = sites e valores = sucessos
        fig = px.pie(
            success_by_site,
            names='Launch Site',
            values='Successful Launches',
            title='Total Successful Launches by Site'
        )
        return fig

    # Caso 2: Site específico selecionado
    else:
        # Filtra o dataframe apenas para o site escolhido
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]

        # Conta quantos sucessos (1) e falhas (0) há para o site
        counts = filtered_df['class'].value_counts().reset_index()
        counts.columns = ['class', 'count']

        # Mapeia 1→Success e 0→Failure para o rótulo da pizza ficar legível
        counts['class'] = counts['class'].map({1: 'Success', 0: 'Failure'})

        # Cria o gráfico de pizza com as contagens do site específico
        fig = px.pie(
            counts,
            names='class',
            values='count',
            title=f'Success vs Failure for site {entered_site}'
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
from dash.dependencies import Input, Output  # (já importado no topo, mantido aqui por clareza)

@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown', component_property='value'),
        Input(component_id='payload-slider', component_property='value')
    ]
)
def update_scatter_chart(selected_site, payload_range):
    """
    Atualiza o gráfico de dispersão (success-payload-scatter-chart) com base em:
    - Site selecionado no dropdown (selected_site)
    - Intervalo de payload selecionado no slider (payload_range = [low, high])

    Lógica:
    - Sempre filtra pelo intervalo de payload (entre low e high).
    - Se selected_site == 'ALL': usa todos os sites.
    - Caso contrário: filtra também pelo site específico.
    - O gráfico colore os pontos por 'Booster Version Category'.
    """
    # payload_range vem como uma lista [min, max] do RangeSlider
    low, high = payload_range

    # 1) Filtramos pelas linhas cujo Payload Mass (kg) está dentro do intervalo [low, high]
    mask_payload = (
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    )
    filtered_df = spacex_df[mask_payload].copy()

    # 2) Se o dropdown NÃO for "ALL", também filtramos pelo site escolhido
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]

    # 3) Construímos o título do gráfico conforme o contexto
    title = (
        'Payload vs. Outcome (All Sites)'
        if selected_site == 'ALL'
        else f'Payload vs. Outcome ({selected_site})'
    )

    # 4) Criamos o scatter plot:
    #    - x: payload
    #    - y: class (0/1)
    #    - color: versão do booster
    #    - hover_data: mostramos também o site no tooltip
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=title,
        labels={
            'Payload Mass (kg)': 'Payload (kg)',
            'class': 'Outcome (0=Failure, 1=Success)',
            'Booster Version Category': 'Booster'
        },
        hover_data=['Launch Site']
    )

    # 5) Ajuste visual opcional: tamanho e transparência dos marcadores
    fig.update_traces(marker=dict(size=10, opacity=0.75))

    # 6) Retornamos a figura para o Dash renderizar no componente Graph
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)