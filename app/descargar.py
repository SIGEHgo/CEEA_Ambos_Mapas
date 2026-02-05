import dash_ag_grid as dag
from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.SPACELAB])

df = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/ag-grid/olympic-winners.csv"
)

df = df.head(75)

columnDefs = [
    {"headerName": "ID", "valueGetter": {"function": "params.node.rowIndex + 1"}, "width": 70},
    {"field": "country"},
    {"field": "year"},
    {"field": "athlete"},
    {"field": "date"},
    {"field": "sport"},
    {"field": "total"},
]

defaultColDef = {"filter": True, "maxWidth": 150}

grid = dag.AgGrid(
    id="grid-regular-layout",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    defaultColDef=defaultColDef,
    dashGridOptions={"animateRows": False}
)

print_grid = dag.AgGrid(
    id="grid-modal-print",
    columnDefs=columnDefs,
    rowData=df.to_dict("records"),
    defaultColDef=defaultColDef,
    style={"height": "", "width": ""},
    dashGridOptions={"domLayout": "print"},
)

latin_text = dcc.Markdown("""
        ### Latin Text
        Lorem ipsum dolor sit amet, ne cum repudiare abhorreant. Atqui molestiae neglegentur ad nam, mei amet eros ea,
        populo deleniti scaevola et pri. Pro no ubique explicari, his reque nulla consequuntur in. His soleat doctus
        constituam te, sed at alterum repudiandae. Suas ludus electram te ius.
        """, style={"maxWidth": 800})

more_latin_text = dcc.Markdown("""
    ### More Latin Text
    Lorem ipsum dolor sit amet, ne cum repudiare abhorreant. Atqui molestiae neglegentur ad nam, mei amet eros ea,
    populo deleniti scaevola et pri. Pro no ubique explicari, his reque nulla consequuntur in. His soleat doctus
    constituam te, sed at alterum repudiandae. Suas ludus electram te ius.
    """, style={"maxWidth": 800})

print_layout = html.Div(
    [
        dbc.ModalHeader(dbc.Button("Print", id="grid-browser-print-btn")),
        dbc.ModalBody(
            # customize your printed report here
            [
                html.H1("Dash AG Grid Print Report Demo", className="py-4"),
                latin_text,
                print_grid,
                more_latin_text,
            ],
            id="grid-print-area",
        ),
        html.Div(id="dummy"),
    ]
)

app.layout = html.Div(
    [
        dbc.Button("Print Report", id="grid-modal-print-btn"),
        grid,
        latin_text,
        dbc.Modal(
            print_layout, id="modal-print-container", is_open=False, size='xl'
        ),
    ],  
    style={"margin": 20},
)


@callback(
    Output("grid-modal-print", "columnState"),
    Output("grid-modal-print", "filterModel"),
    Output("modal-print-container", "is_open"),
    Input("grid-modal-print-btn", "n_clicks"),
    State("grid-regular-layout", "columnState"),
    State("grid-regular-layout", "filterModel"),
    prevent_initial_call=True,
)
def open_print_modal(_, col_state, filter_model):
    return col_state, filter_model, True


app.clientside_callback(
    """
    function () {

         var printContents = document.getElementById('grid-print-area').innerHTML;
         var originalContents = document.body.innerHTML;

         document.body.innerHTML = printContents;

         window.print();

         document.body.innerHTML = originalContents;
         location.reload()

        return window.dash_clientside.no_update
    }
    """,
    Output("dummy", "children"),
    Input("grid-browser-print-btn", "n_clicks"),
    prevent_initial_call=True,
)

if __name__ == "__main__":
    app.run(debug=True)