import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import requests
import os

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
    html.H1("🌤 OpenWeather 5日予報ダッシュボード"),
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

    api_key = os.getenv("WEATHER_API_KEY")
    if not api_key:
        return go.Figure(), "環境変数 WEATHER_API_KEY が未設定です。Renderに設定してください。"

    lat, lon = CITY_COORDS[city]
    forecast_url = (
        f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}"
        f"&appid={api_key}&units=metric&lang=ja"
    )

    try:
        forecast_response = requests.get(forecast_url, timeout=15)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
    except requests.RequestException:
        return go.Figure(), "OpenWeatherから予報データを取得できませんでした。"

    entries = forecast_data.get("list", [])
    if not entries:
        return go.Figure(), "予報データが空です。APIキーやプラン設定を確認してください。"

    daily_temps = {}
    for entry in entries:
        date_str = entry.get("dt_txt", "").split(" ")[0]
        main_data = entry.get("main", {})
        temp_min = main_data.get("temp_min")
        temp_max = main_data.get("temp_max")
        if not date_str or temp_min is None or temp_max is None:
            continue

        if date_str not in daily_temps:
            daily_temps[date_str] = {"min": temp_min, "max": temp_max}
        else:
            daily_temps[date_str]["min"] = min(daily_temps[date_str]["min"], temp_min)
            daily_temps[date_str]["max"] = max(daily_temps[date_str]["max"], temp_max)

    if not daily_temps:
        return go.Figure(), "予報データの解析に失敗しました。"

    all_dates = sorted(daily_temps.keys())
    all_temps_min = [daily_temps[d]["min"] for d in all_dates]
    all_temps_max = [daily_temps[d]["max"] for d in all_dates]
    figure = {
        "data": [
            go.Scatter(x=all_dates, y=all_temps_min, mode="lines+markers", name="最低気温"),
            go.Scatter(x=all_dates, y=all_temps_max, mode="lines+markers", name="最高気温")
        ],
        "layout": go.Layout(title=f"{city} の今後5日間の気温予報（OpenWeather）", xaxis={"title": "日付", "tickangle": -45}, yaxis={"title": "気温 (℃)"}, hovermode="closest")
    }
    return figure, ""

if __name__ == "__main__":
    app.run_server(debug=True)
