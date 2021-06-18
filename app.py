import json
import sqlite3

import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from sklearn.cluster import KMeans

SQL_CONN = sqlite3.connect("UrbanData-test.db")
SQL_QUERY = "SELECT * FROM Kerncijfers_wijken_en_buurten_2016_pp WHERE Wijk_Buurt\ufeff NOT LIKE \"Wijk%\""

color_filters = ["GMS"]
with open("analyses.json") as json_file:
    pre_coded_analyses = json.load(json_file)

df = pd.read_sql_query(SQL_QUERY, con=SQL_CONN)
df = df.drop(df.index[[0]])
df = df.dropna(subset=[
    "Bevolking_Leeftijdsgroepen_15_tot_25_jaar",
    "Wonen_Woningen_naar_bouwjaar_Bouwjaar_voor_2000",
    "Inkomen_Inkomen_van_huishoudens_Huishoudens_met_een_laag_inkomen",
    "Inkomen_Inkomen_van_huishoudens_Huish_onder_of_rond_sociaal_minimum",
    "Wonen_Woningen_naar_eigendom_Huurwoningen_In_bezit_woningcorporatie",
    # "Criminaliteit_Totaal_diefstal_uit_woning_schuur_ed",
    # "Criminaliteit_Vernieling_misdrijf_tegen_openbare_orde",
    # "Criminaliteit_Gewelds__en_seksuele_misdrijven",
])

app = dash.Dash(__name__)

for key in pre_coded_analyses:
    model = KMeans(3, random_state=42)
    model.fit(df[pre_coded_analyses[key][0]])
    color_filters.append(key)
    if len(pre_coded_analyses[key][1]) == 3:
        df[key] = [pre_coded_analyses[key][1][x] for x in model.labels_]
    else:
        df[key] = [str(x) for x in model.labels_]


GMS_WIJKEN = ["Grasbroek", "Musschemig", "Schandelen", "Vrieheide"]
df["GMS"] = ["In GMS" if x in GMS_WIJKEN else "Niet in GMS" for x in df["Wijk_Buurt\ufeff"]]

color_filter_options = [{"label": x, "value": x} for x in color_filters]


app.title = "Groep 1: Demo Dashboard"
app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.P(children="📈BD04: DataScience📉",
                       className="header-emoji"),
                html.H1(children="Urban-Data Dashboard",
                        className="header-title"),
                html.P(children="Een demo dashboard voor data visualisaties",
                       className="header-description"),

            ], className="header"
        ),
        html.Div([
            html.Div(
                [
                    dcc.Dropdown(
                        id='xaxis-column',
                        options=[{'label': i, 'value': i}
                                 for i in df.columns],
                        value='Inkomen_Inkomen_van_huishoudens_Huishoudens_met_een_laag_inkomen',
                        style={'width': '48%', 'display': 'inline-block'}
                    ), dcc.Dropdown(
                        id='yaxis-column',
                        options=[{'label': i, 'value': i}
                                 for i in df.columns],
                        value='Bevolking_Geboorte_en_sterfte_Sterfte_totaal',
                        style={'width': '48%', 'display': 'inline-block'}
                    ),
                ]
            ),
            html.Div(children=[
                dcc.RadioItems(id="color-filter",
                               options=color_filter_options, value="GMS"),
                dcc.Graph(id="indicator-graphic")
            ], className="card"
            )
        ], className="wrapper"
        ),
        html.H1(children="Toelichting Analyses",
                style={"text-align": "center"}),
        html.Div(children=[
            html.Div([
                html.H2(children=key,),
                html.P(children=pre_coded_analyses[key][2],),
            ], className="card-text")
            for key in pre_coded_analyses if len(pre_coded_analyses[key]) == 3
        ],
            style={
                "display": "flex",
            "text-align": "center",
            "padding": "0 0 10% 0",
            "flex-wrap": "wrap"
        })
    ])


@app.callback(
    Output('indicator-graphic', 'figure'),
    Input('color-filter', 'value'),
    Input('xaxis-column', 'value'),
    Input('yaxis-column', 'value')
)
def update_graph(color_filter, x_label, y_label):

    fig = px.scatter(df,
                     x=x_label,
                     y=y_label,
                     color=color_filter,
                     size="Bevolking_Aantal_inwoners",
                     hover_name="Wijk_Buurt\ufeff",
                     color_continuous_scale="Viridis",
                     )
    fig.update_layout(legend={
        "yanchor": "top",
        "y": 0.99,
        "xanchor": "right",
    })
    return fig

# TODO: eindgebruiker analyse laten maken/ uitvoeren


if __name__ == "__main__":
    app.run_server(debug=False,
                   port=80,
                   host="peaceful-wave-95791.herokuapp.com")
