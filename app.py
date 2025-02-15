import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests
import datetime

app = dash.Dash(__name__)
server = app.server  # Herokuデプロイ用

CITY_COORDS = {
    "Tokyo": (35.682839, 139.759455),
    "Osaka": (34.6937, 135.5022),
    "Nagoya": (35.1815, 136.9066),
    "Fukuoka": (33.5904, 130.4017),
    "Sapporo": (43.0621, 141.3544)
}

app.layout = html.Div([
    html.H1("🌤 過去180日 & 未来5日の天気ダッシュボード"),
    dcc.Dropdown(
        id="city-dropdown",
        options=[{"label": city, "value": city} for city in CITY_COORDS.keys()],
        value="Tokyo"
    ),
    html.Button("データ取得", id="fetch-button", n_clicks=0),
    dcc.Graph(id="weather-graph"),
    html.Div(id="error-message", style={"color": "red", "font-size": "18px"})
])

@app.callback(
    [Output("weather-graph", "figure"), Output("error-message", "children")],
    [Input("fetch-button", "n_clicks")],
    [State("city-dropdown", "value")]
)
def update_weather(n_clicks, city):
    if not city:
        return go.Figure(), "都市を選択してください。"
    lat, lon = CITY_COORDS[city]
    today = datetime.date.today()
    past_start_date = (today - datetime.timedelta(days=180)).strftime("%Y-%m-%d")
    past_end_date = today.strftime("%Y-%m-%d")
    past_url = f"https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}&start_date={past_start_date}&end_date={past_end_date}&daily=temperature_2m_max,temperature_2m_min&timezone=Asia/Tokyo"
    past_response = requests.get(past_url)
    if past_response.status_code != 200:
        return go.Figure(), "過去のデータを取得できませんでした。"
    past_data = past_response.json()
    past_dates = past_data["daily"]["time"]
    past_temps_min = past_data["daily"]["temperature_2m_min"]
    past_temps_max = past_data["daily"]["temperature_2m_max"]
    future_start_date = today.strftime("%Y-%m-%d")
    future_end_date = (today + datetime.timedelta(days=5)).strftime("%Y-%m-%d")
    future_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&daily=temperature_2m_max,temperature_2m_min&timezone=Asia/Tokyo&start_date={future_start_date}&end_date={future_end_date}"
    future_response = requests.get(future_url)
    if future_response.status_code != 200:
        return go.Figure(), "未来のデータを取得できませんでした。"
    future_data = future_response.json()
    future_dates = future_data["daily"]["time"]
    future_temps_min = future_data["daily"]["temperature_2m_min"]
    future_temps_max = future_data["daily"]["temperature_2m_max"]
    all_dates = past_dates + future_dates
    all_temps_min = past_temps_min + future_temps_min
    all_temps_max = past_temps_max + future_temps_max
    figure = {
        "data": [
            go.Scatter(x=all_dates, y=all_temps_min, mode="lines+markers", name="最低気温"),
            go.Scatter(x=all_dates, y=all_temps_max, mode="lines+markers", name="最高気温")
        ],
        "layout": go.Layout(title=f"{city} の過去180日間と未来5日間の気温推移", xaxis={"title": "日付", "tickangle": -45}, yaxis={"title": "気温 (℃)"}, hovermode="closest")
    }
    return figure, ""

if __name__ == "__main__":
    app.run_server(debug=True)

