# Import required libraries
import base64
import os
from urllib.parse import quote as urlquote
from flask import Flask, send_from_directory

import dash
import pathlib
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objs as go
import dash_table
from datetime import datetime as dt

import pandas as pd
import numpy as np
from datetime import datetime

# from flask_caching import Cache

UPLOAD_DIRECTORY = "dataframes"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Launch The Application
# Normally, Dash creates its own Flask server internally. By creating our own,
# we can create a route for downloading files directly:
server = Flask(__name__)
app = dash.Dash(
    server=server, meta_tags=[{"name": "viewport", "content": "width=device-width"}]
)

selected_dataframe = pd.DataFrame()
chart_types = [
    "area",
    "bar",
    "bar_polar",
    "box",
    "density_contour",
    "density_heatmap",
    "histogram",
    "line",
    "line_polar",
    "parallel_categories",
    "parallel_coordinates",
    "pie",
    "scatter",
    "scatter_matrix",
    "scatter_polar",
    "strip",
]

# cache = Cache(app.server, config={
#     'CACHE_TYPE': 'redis',
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# })

# Create App Layout
app.layout = html.Div(
    [
        dcc.Store(id="memory-dataframe", storage_type="session"),
        dcc.Tabs(
            id="tabs-example",
            children=[
                dcc.Tab(
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H2("Upload"),
                                        dcc.Upload(
                                            id="upload-data",
                                            children=html.Div(
                                                [
                                                    "Drag and drop or click to select a file to upload."
                                                ]
                                            ),
                                            style={
                                                "width": "100%",
                                                "height": "60px",
                                                "lineHeight": "60px",
                                                "borderWidth": "1px",
                                                "borderStyle": "dashed",
                                                "borderRadius": "5px",
                                                "textAlign": "center",
                                                "margin": "10px",
                                            },
                                            multiple=True,
                                        ),
                                    ],
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            children="Choose Dataframe:",
                                            className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="file-list",
                                            placeholder="Select an Option",
                                            className="dcc_control",
                                        ),
                                    ],
                                )
                            ]
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H3(
                                            "DataFrame", style={"textAlign": "center"}
                                        ),
                                        dash_table.DataTable(
                                            id="table",
                                            columns=[
                                                {"name": i, "id": i}
                                                for i in selected_dataframe.columns
                                            ],
                                            data=selected_dataframe.to_dict("records"),
                                            style_cell={"textAlign": "center"},
                                            style_header={
                                                "backgroundColor": "#3D9970",
                                                "fontWeight": "bold",
                                                "textAlign": "center",
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "rgb(248, 248, 248)",
                                                },
                                            ],
                                            page_current=0,
                                            page_size=10,
                                            page_action="custom",
                                        ),
                                    ],
                                    style={"display": "none"},
                                    id="div-table",
                                ),
                            ]
                        ),
                    ],
                    label="Dataframe",
                ),
                dcc.Tab(
                    children=[
                        html.Div(id="customize_control"),
                        html.Div([html.Button("Submit", id="goto_main", n_clicks=0)]),
                    ],
                    label="Columns",
                ),
                dcc.Tab(
                    children=[
                        html.Div(
                            [
                                html.Div(
                                    className="pretty_container four columns",
                                    id="filter_box",
                                ),
                                html.Div(
                                    [
                                        dash_table.DataTable(
                                            id="table_test",
                                            style_cell={"textAlign": "center"},
                                            style_header={
                                                "backgroundColor": "#3D9970",
                                                "fontWeight": "bold",
                                                "textAlign": "center",
                                            },
                                            style_data_conditional=[
                                                {
                                                    "if": {"row_index": "odd"},
                                                    "backgroundColor": "rgb(248, 248, 248)",
                                                },
                                            ],
                                            page_current=0,
                                            page_size=10,
                                            page_action="custom",
                                        ),
                                    ],
                                    className="pretty_container eight columns",
                                ),
                            ],
                            className="row flex-display",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.P(
                                            "Select Chart Type",
                                            className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="select_chart_type",
                                            options=[
                                                {"label": v, "value": v}
                                                for v in chart_types
                                            ],
                                            className="dcc_control",
                                        ),
                                    ],
                                    className="pretty_container two columns",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Select X axis", className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="select_x_axis", className="dcc_control",
                                        ),
                                        html.P(
                                            "Select Y axis", className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="select_y_axis", className="dcc_control",
                                        ),
                                    ],
                                    className="pretty_container two columns",
                                ),
                                html.Div(
                                    [
                                        html.P("Facet_row", className="control_label",),
                                        dcc.Dropdown(
                                            id="facet_row", className="dcc_control",
                                        ),
                                        html.P("Facet col", className="control_label",),
                                        dcc.Dropdown(
                                            id="facet_col", className="dcc_control",
                                        ),
                                    ],
                                    className="pretty_container two columns",
                                ),
                                html.Div(
                                    [
                                        html.P("Color", className="control_label",),
                                        dcc.Dropdown(
                                            id="color_columns", className="dcc_control",
                                        ),
                                    ],
                                    className="pretty_container two columns",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Group by Columns",
                                            className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="group_by_columns",
                                            className="dcc_control",
                                            multi=True,
                                        ),
                                        html.P(
                                            "Group by Function",
                                            className="control_label",
                                        ),
                                        dcc.Dropdown(
                                            id="group_by_function",
                                            className="dcc_control",
                                            options=[
                                                {"label": "mean", "value": "mean"},
                                                {"label": "min", "value": "min"},
                                                {"label": "max", "value": "max"},
                                                {"label": "count", "value": "count"},
                                                {"label": "sum", "value": "sum"},
                                            ],
                                        ),
                                    ],
                                    className="pretty_container four columns",
                                ),
                            ],
                            className="row flex-display center",
                        ),
                        html.Div(
                            [html.Button("Show plot", id="show_figure", n_clicks=0)]
                        ),
                        html.Div(id="test_div", className="row flex-display center",),
                        html.Div(
                            [
                                html.Div(
                                    [dcc.Graph(id="main_graph", figure="",)],
                                    className="pretty_container twelve columns",
                                    style={"height": "700"},
                                ),
                            ],
                            className="row flex-display",
                        ),
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.Button(
                                            "Save plot", id="save_button", n_clicks=0
                                        )
                                    ],
                                    id="save_button_container",
                                    style={"display": "none"},
                                ),
                                html.P(
                                    id="alert_save_plot",
                                    style={"color": "green", "font-weight": "bold"},
                                ),
                                html.Div(id="n_clicks_save", style={"display": "none"}),
                            ],
                            className="row flex-display",
                        ),
                    ],
                    label="Main",
                ),
            ],
        ),
        html.Div(id="tabs-example-content"),
    ],
    className="row",
)


# Functions
@server.route("/download/<path:path>")
def download(path):
    """Serve a file from the upload directory."""
    return send_from_directory(UPLOAD_DIRECTORY, path, as_attachment=True)


def save_file(name, content):
    """Decode and store a file uploaded with Plotly Dash."""
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def file_download_link(filename):
    """Create a Plotly Dash 'A' element that downloads a file from the app."""
    location = "/download/{}".format(urlquote(filename))
    return html.A(filename, href=location)


def uploaded_files():
    """List the files in the upload directory."""
    files = []
    for filename in os.listdir(UPLOAD_DIRECTORY):
        path = os.path.join(UPLOAD_DIRECTORY, filename)
        if os.path.isfile(path):
            files.append(filename)
    return files


# Callbacks
@app.callback(
    Output("file-list", "options"),
    [Input("upload-data", "filename"), Input("upload-data", "contents")],
)
def update_output(uploaded_filenames, uploaded_file_contents):
    """Save uploaded files and regenerate the file list."""

    if uploaded_filenames is not None and uploaded_file_contents is not None:
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            save_file(name, data)

    files = uploaded_files()
    if len(files) == 0:
        return [html.Li("No files yet!")]
    else:
        return [{"label": filename, "value": filename} for filename in files]


@app.callback(
    Output("memory-dataframe", "data"), [Input("file-list", "value")],
)
def return_selected_file(value):
    return value


@app.callback(
    [Output("table", "columns"), Output("table", "data"), Output("div-table", "style")],
    [
        Input("memory-dataframe", "data"),
        Input("table", "page_current"),
        Input("table", "page_size"),
    ],
)
def Create_Dataframe(value, page_current, page_size):
    """Crate a Pandas Dataframe from chosen File."""
    if value is None:
        selected_dataframe = pd.DataFrame()
        data = selected_dataframe.to_dict("records")
        columns = [{"name": i, "id": i} for i in selected_dataframe.columns]
        style = {"display": "none"}
        return columns, data, style

    path = os.path.join(UPLOAD_DIRECTORY, value)
    extension = os.path.splitext(path)[1]
    if extension == ".csv":
        selected_dataframe = pd.read_csv(path)
        data = selected_dataframe.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")
        columns = [{"name": i, "id": i} for i in selected_dataframe.columns]
        style = {"display": "block"}
    elif extension == ".feather":
        selected_dataframe = pd.read_feather(path)
        data = selected_dataframe.iloc[
            page_current * page_size : (page_current + 1) * page_size
        ].to_dict("records")
        columns = [{"name": i, "id": i} for i in selected_dataframe.columns]
        style = {"display": "block"}
    else:
        selected_dataframe = pd.DataFrame()
        data = selected_dataframe.to_dict("records")
        columns = [{"name": i, "id": i} for i in selected_dataframe.columns]
        style = {"display": "none"}

    return columns, data, style


@app.callback(
    [Output("customize_control", "children"), Output("filter_box", "children"),],
    [Input("memory-dataframe", "data")],
)
def Create_Dataframe(dataframe):
    options = [
        {"label": "Dropdown", "value": "Dropdown"},
        {"label": "RangeSlider", "value": "RangeSlider"},
        {"label": "DatePickerRange", "value": "DatePickerRange"},
    ]
    if dataframe is None:
        selected_dataframe = pd.DataFrame()
        dropdowns = [x for x in selected_dataframe.columns]
        filter_types = [x for x in selected_dataframe.columns]
        return dropdowns, filter_types
    path = os.path.join(UPLOAD_DIRECTORY, dataframe)
    extension = os.path.splitext(path)[1]
    if extension == ".csv":
        selected_dataframe = pd.read_csv(path)
    elif extension == ".feather":
        selected_dataframe = pd.read_feather(path)
    else:
        selected_dataframe = pd.DataFrame()

    dropdowns = [
        html.Div(
            [
                html.Div(
                    [
                        html.P(
                            id={"type": "dynamic-dropdown-name", "index": x},
                            children=x,
                            className="control_label six columns",
                        ),
                        dcc.Dropdown(
                            id={"type": "dynamic-dropdown", "index": x},
                            options=options,
                            className="dcc_control six columns",
                        ),
                    ],
                    className="pretty_container twelve columns",
                )
            ],
            className="row flex-display six columns center",
        )
        for x in selected_dataframe.columns
    ]
    filter_types = [
        html.Div(id={"type": "dynamic-filter", "index": x},)
        for x in selected_dataframe.columns
    ]
    return dropdowns, filter_types


@app.callback(
    Output({"type": "dynamic-filter", "index": MATCH}, "children"),
    [Input("memory-dataframe", "data"), Input("goto_main", "n_clicks")],
    [
        State({"type": "dynamic-dropdown", "index": MATCH}, "value"),
        State({"type": "dynamic-dropdown-name", "index": MATCH}, "children"),
    ],
)
def Create_Dataframe(dataframe, submit_coloumn, value, name):
    if dataframe is None:
        return ""
    path = os.path.join(UPLOAD_DIRECTORY, dataframe)
    extension = os.path.splitext(path)[1]
    if extension == ".csv":
        selected_dataframe = pd.read_csv(path)
    elif extension == ".feather":
        selected_dataframe = pd.read_feather(path)
    selected_column = selected_dataframe[name]

    if value == "Dropdown":
        column_vlaues = selected_column.unique()#.tolist()
        columns_values_dict = [{"label": v, "value": v} for v in column_vlaues]
        return [
            html.P(children=name, className="control_label",),
            dcc.Dropdown(
                id={"type": "selected-filter", "index": name},
                className="dcc_control",
                options=columns_values_dict,
                multi=True,
            ),
            html.P(id={"type": "range_slider", "index": name},),
        ]
    if value == "RangeSlider":
        selected_column_min = selected_column.min()
        selected_column_max = selected_column.max()

        return [
            html.P(children=name, className="control_label",),
            dcc.RangeSlider(
                id={"type": "selected-filter", "index": name},
                className="dcc_control",
                min=selected_column_min,
                max=selected_column_max,
            ),
            html.P(id={"type": "range_slider", "index": name},),
        ]
    if value == "DatePickerRange":
        try:
            selected_column_date = pd.to_datetime(
                selected_column, infer_datetime_format=True
            )
            year_min = min(selected_column_date).year
            month_min = min(selected_column_date).month
            day_min = min(selected_column_date).day
            year_max = max(selected_column_date).year
            month_max = max(selected_column_date).month
            day_max = max(selected_column_date).day
        except:
            pass
        return [
            html.P(children=name, className="control_label",),
            dcc.DatePickerRange(
                id={"type": "selected-filter", "index": name},
                min_date_allowed=dt(year_min, month_min, day_min),
                max_date_allowed=dt(year_max, month_max, day_max),
                className="dcc_control",
            ),
            html.P(id={"type": "range_slider", "index": name},),
        ]
    else:
        return value


@app.callback(
    [
        Output("test_div", "children"),
        Output("table_test", "columns"),
        Output("table_test", "data"),
        Output("select_x_axis", "options"),
        Output("select_y_axis", "options"),
        Output("group_by_columns", "options"),
        Output("color_columns", "options"),
        Output("facet_row", "options"),
        Output("facet_col", "options"),
    ],
    [
        Input("memory-dataframe", "data"),
        Input("select_chart_type", "value"),
        Input("table_test", "page_current"),
        Input("table_test", "page_size"),
        Input({"type": "selected-filter", "index": ALL}, "id"),
        Input({"type": "selected-filter", "index": ALL}, "value"),
        Input({"type": "selected-filter", "index": ALL}, "start_date"),
        Input({"type": "selected-filter", "index": ALL}, "end_date"),
    ],
)
def update_figure(
    dataframe, chart_type, page_current, page_size, column, value, start_date, end_date
):
    # range_slider = []
    if dataframe is None:
        return "", "", "", "", "", "", "", "", ""
    path = os.path.join(UPLOAD_DIRECTORY, dataframe)
    extension = os.path.splitext(path)[1]
    if extension == ".csv":
        selected_dataframe = pd.read_csv(path)
    elif extension == ".feather":
        selected_dataframe = pd.read_feather(path)
    for x in range(len(column)):
        if (value[x] is None) and (start_date[x] is None or end_date[x] is None):
            continue
        if isinstance(value[x], list):
            if len(value[x]) > 0:
                if isinstance(value[x][0], int) and len(value[x]) == 2:
                    range_slider = value[x]
                    selected_dataframe = selected_dataframe[
                        (selected_dataframe[column[x]["index"]] >= value[x][0])
                        & (selected_dataframe[column[x]["index"]] <= value[x][1])
                    ]
                else:
                    selected_dataframe = selected_dataframe[
                        selected_dataframe[column[x]["index"]].isin(value[x])
                    ]
                continue
            else:
                continue
        if start_date[x] is not None or end_date[x] is not None:
            if start_date[x] is not None:
                selected_dataframe = selected_dataframe[
                    (selected_dataframe[column[x]["index"]] >= start_date[x])
                ]
            if end_date[x] is not None:
                selected_dataframe = selected_dataframe[
                    (selected_dataframe[column[x]["index"]] <= end_date[x])
                ]
            continue
        if not isinstance(value[x], list):
            if value[x] == "":
                continue
            selected_dataframe = selected_dataframe[
                selected_dataframe[column[x]["index"]] == value[x]
            ]
    data = selected_dataframe.iloc[
        page_current * page_size : (page_current + 1) * page_size
    ].to_dict("records")
    columns = [{"name": i, "id": i} for i in selected_dataframe.columns]
    axis_valus = [{"label": v, "value": v} for v in selected_dataframe.columns]
    group_by_values = []
    for v in selected_dataframe.columns:
        if len(selected_dataframe[v].unique()) < selected_dataframe.shape[0] / 2:
            group_by_values.append({"label": v, "value": v})

    return (
        str(column)
        + "__"
        + str(value)
        + str(selected_dataframe.shape[0])
        + str(start_date)
        + str(end_date),
        columns,
        data,
        axis_valus,
        axis_valus,
        group_by_values,
        group_by_values,
        group_by_values,
        group_by_values,
    )


@app.callback(
    [
        Output("main_graph", "figure"),
        Output("save_button_container", "style"),
        Output("alert_save_plot", "children"),
        Output("n_clicks_save", "children"),
    ],
    [
        Input("memory-dataframe", "data"),
        Input("save_button", "n_clicks"),
        Input("show_figure", "n_clicks"),
    ],
    [
        State("n_clicks_save", "children"),
        State({"type": "selected-filter", "index": ALL}, "id"),
        State({"type": "selected-filter", "index": ALL}, "value"),
        State({"type": "selected-filter", "index": ALL}, "start_date"),
        State({"type": "selected-filter", "index": ALL}, "end_date"),
        State("select_chart_type", "value"),
        State("select_x_axis", "value"),
        State("select_y_axis", "value"),
        State("group_by_columns", "value"),
        State("group_by_function", "value"),
        State("color_columns", "value"),
        State("facet_row", "value"),
        State("facet_col", "value"),
    ],
)
def update_figure(
    dataframe,
    n_clicks,
    show_figure,
    n_clicks_save,
    column,
    value,
    start_date,
    end_date,
    chart_type,
    x_axis,
    y_axis,
    group_by_columns,
    group_by_function,
    color_columns,
    facet_row,
    facet_col,
):

    style = {"display": "none"}
    if dataframe is None or x_axis is None or (y_axis is None) or chart_type is None:
        return go.Figure(), style, "", n_clicks
    path = os.path.join(UPLOAD_DIRECTORY, dataframe)
    extension = os.path.splitext(path)[1]
    if extension == ".csv":
        selected_dataframe = pd.read_csv(path)
    elif extension == ".feather":
        selected_dataframe = pd.read_feather(path)
    for x in range(len(column)):
        if (value[x] is None) and (start_date[x] is None or end_date[x] is None):
            continue
        if isinstance(value[x], list):
            if len(value[x]) > 0:
                if isinstance(value[x][0], int) and len(value[x]) == 2:
                    range_slider = value[x]
                    selected_dataframe = selected_dataframe[
                        (selected_dataframe[column[x]["index"]] >= value[x][0])
                        & (selected_dataframe[column[x]["index"]] <= value[x][1])
                    ]
                else:
                    selected_dataframe = selected_dataframe[
                        selected_dataframe[column[x]["index"]].isin(value[x])
                    ]
                continue
            else:
                continue
        if start_date[x] is not None or end_date[x] is not None:
            if start_date[x] is not None:
                selected_dataframe = selected_dataframe[
                    (selected_dataframe[column[x]["index"]] >= start_date[x])
                ]
            if end_date[x] is not None:
                selected_dataframe = selected_dataframe[
                    (selected_dataframe[column[x]["index"]] <= end_date[x])
                ]
            continue
        if not isinstance(value[x], list):
            if value[x] == "":
                continue
            selected_dataframe = selected_dataframe[
                selected_dataframe[column[x]["index"]] == value[x]
            ]
    if (
        group_by_columns != []
        and group_by_columns is not None
        and chart_type != "histogram"
    ):
        if x_axis not in group_by_columns:
            group_by_columns.append(x_axis)
    if (
        group_by_columns != []
        and group_by_columns is not None
        and group_by_function != []
        and group_by_function is not None
    ):
        selected_dataframe = (
            selected_dataframe.groupby(group_by_columns)
            .agg(group_by_function)
            .reset_index()
            .sort_values(by=y_axis)
        )

    if color_columns != [] and color_columns is not None:
        if group_by_columns is None or group_by_columns == []:
            fig = getattr(px, chart_type)(
                selected_dataframe,
                x=x_axis,
                y=y_axis,
                color=color_columns,
                facet_row=facet_row,
                facet_col=facet_col,
            )
        if (
            group_by_columns != []
            and group_by_columns is not None
            and group_by_function != []
            and group_by_function is not None
        ):
            if color_columns in group_by_columns:
                fig = getattr(px, chart_type)(
                    selected_dataframe,
                    x=x_axis,
                    y=y_axis,
                    color=color_columns,
                    facet_row=facet_row,
                    facet_col=facet_col,
                )
            else:
                group_by_columns.remove(x_axis)
                fig = getattr(px, chart_type)(
                    selected_dataframe,
                    x=x_axis,
                    y=y_axis,
                    color=group_by_columns[0],
                    facet_row=facet_row,
                    facet_col=facet_col,
                )
    else:
        if (
            group_by_columns != []
            and group_by_columns is not None
            and group_by_function != []
            and group_by_function is not None
            and len(group_by_columns) > 1
        ):
            group_by_columns.remove(x_axis)
            fig = getattr(px, chart_type)(
                selected_dataframe,
                x=x_axis,
                y=y_axis,
                color=group_by_columns[0],
                facet_row=facet_row,
                facet_col=facet_col,
            )
        else:
            fig = getattr(px, chart_type)(
                selected_dataframe,
                x=x_axis,
                y=y_axis,
                facet_row=facet_row,
                facet_col=facet_col,
            )
    height = 500
    if facet_row != None and facet_row != []:
        height = 800
    fig.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=height)
    style = {"display": "block"}
    alert = ""
    if n_clicks > n_clicks_save:
        now = datetime.now()

        current_time = (
            str(chart_type)
            + " -"
            + str(x_axis)
            + " by "
            + str(y_axis)
            + " grouped- "
            + str(group_by_columns)
            + " func- "
            + str(group_by_function)
        )
        fig.write_html("data/plots/" + str(current_time) + ".html")
        style = {"display": "none"}
        alert = "Plot is saved in data/plots/" + current_time + ".html seccessfully!"

    return fig, style, alert, n_clicks


if __name__ == "__main__":
    app.run_server()
pr