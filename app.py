import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import pandas as pd
import requests
import datetime

# OpenWeatherMap API設定
API_KEY = "0a837038a275c1387a26fc15b3a9a9ce"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Dashアプリの初期化
app = dash.Dash(__name__)

# アプリのレイアウト定義
app.layout = html.Div([
    html.H1("🌤 5日間の天気ダッシュボード"),
    
    # 都市名入力フィールド
    html.Label("都市名を入力してください（例: Tokyo, London, New York）"),
    dcc.Input(id="city-input", type="text", value="Tokyo", debounce=True),
    html.Button("検索", id="search-button", n_clicks=0),
    
    # 天気予報グラフ
    dcc.Graph(id="forecast-graph")
])

# コールバック関数
@app.callback(
    Output("forecast-graph", "figure"),
    [Input("search-button", "n_clicks")],
    [State("city-input", "value")]
)
def update_weather(n_clicks, city):
    if not city:
        return go.Figure()
    
    # 未来の天気予報を取得
    forecast_params = {"q": city, "appid": API_KEY, "units": "metric"}
    forecast_response = requests.get(FORECAST_URL, params=forecast_params)
    
    if forecast_response.status_code != 200:
        return go.Figure()
    
    forecast_data = forecast_response.json()
    
    # 未来5日間の3時間ごとのデータをDataFrameに変換
    forecast_list = forecast_data["list"]
    forecast_df = pd.DataFrame({
        "date": [datetime.datetime.fromtimestamp(item["dt"]).strftime("%m-%d %H:%M") for item in forecast_list],
        "temp": [item["main"]["temp"] for item in forecast_list]
    })
    
    # グラフ作成（3時間ごとの気温推移）
    figure = {
        "data": [
            go.Scatter(x=forecast_df["date"], y=forecast_df["temp"], mode="lines+markers", name="気温")
        ],
        "layout": go.Layout(
            title=f"{city} の5日間の気温推移",
            xaxis={"title": "日付", "tickangle": -45},
            yaxis={"title": "気温 (℃)"},
            hovermode="closest"
        )
    }
    
    return figure

# アプリを起動
if __name__ == '__main__':
    app.run_server(debug=True)
