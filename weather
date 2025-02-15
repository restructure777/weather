import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import pandas as pd
import datetime
import requests
import time  # APIリクエストの間に待機するために使用

# ご自身のAPIキーに置き換えてください
API_KEY = "f065126ba4e9306d8cd1c0f8e78dd3d4"  
LAT = 35.1815    # 名古屋市の緯度
LON = 136.9066   # 名古屋市の経度
BASE_URL = "https://api.openweathermap.org/data/2.5/onecall/timemachine"

def fetch_weather_data():
    """
    OpenWeatherMapのtimemachineエンドポイントを利用して、
    過去5日間の各日の正午付近の天気データを取得し、
    その日の最低気温と最高気温を算出してDataFrameにまとめます。
    """
    today = datetime.date.today()
    data = []
    
    # 過去5日分のデータを取得（最新の日付がリストの最後になるよう逆順に格納）
    for i in range(5):
        day = today - datetime.timedelta(days=i)
        # 当日の正午（12:00）を基準にする（※タイムゾーンに注意）
        dt_obj = datetime.datetime.combine(day, datetime.time(12, 0))
        timestamp = int(dt_obj.timestamp())
        
        params = {
            "lat": LAT,
            "lon": LON,
            "dt": timestamp,
            "appid": API_KEY,
            "units": "metric"  # 摂氏表示
        }
        
        response = requests.get(BASE_URL, params=params)
        if response.status_code == 200:
            json_data = response.json()
            hourly = json_data.get("hourly", [])
            if hourly:
                # 1時間ごとの温度データからその日の最低・最高気温を算出
                temps = [hour.get("temp") for hour in hourly]
                min_temp = min(temps)
                max_temp = max(temps)
                data.append({"date": day, "min_temp": min_temp, "max_temp": max_temp})
            else:
                data.append({"date": day, "min_temp": None, "max_temp": None})
        else:
            print(f"Failed to get data for {day}. HTTP Status code: {response.status_code}")
            data.append({"date": day, "min_temp": None, "max_temp": None})
        
        # APIのレート制限対策として1秒待機（必要に応じて調整）
        time.sleep(1)
    
    # ループでは最新の日が先頭に入るため、古い順に並び替え
    data = data[::-1]
    df = pd.DataFrame(data)
    return df

# Dashアプリの初期化
app = dash.Dash(__name__)

# アプリのレイアウト定義
app.layout = html.Div([
    html.H1("名古屋市の過去5日間の気温（OpenWeatherMap API利用）"),
    dcc.Graph(id='temp-graph'),
    # dcc.Intervalで一定間隔（ここでは1時間ごと）にデータを更新
    dcc.Interval(
        id='interval-component',
        interval=60*60*1000,  # 1時間ごと（ミリ秒単位）
        n_intervals=0
    )
])

# コールバックでグラフを更新
@app.callback(
    Output('temp-graph', 'figure'),
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    df = fetch_weather_data()
    figure = {
        'data': [
            go.Scatter(
                x=df['date'],
                y=df['min_temp'],
                mode='lines+markers',
                name='最低気温'
            ),
            go.Scatter(
                x=df['date'],
                y=df['max_temp'],
                mode='lines+markers',
                name='最高気温'
            )
        ],
        'layout': go.Layout(
            title="名古屋市の過去5日間の気温",
            xaxis={'title': '日付'},
            yaxis={'title': '気温 (℃)'},
            hovermode='closest'
        )
    }
    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
