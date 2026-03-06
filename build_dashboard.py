import pandas as pd
import json

# Read the latest CSV
csv_path = 'c:/backtest_trades_2020_now.csv'
df = pd.read_csv(csv_path)

# Prepare data for JS
trades = []
for _, row in df.iterrows():
    trades.append({
        'symbol': row['Symbol'],
        'side': row['Side'],
        'entry_time': row['EntryTime'],
        'exit_time': row['ExitTime'],
        'pnl': float(row['PnL']),
        'roi': float(str(row['PnL%']).replace('%', '')) if 'PnL%' in row and pd.notnull(row['PnL%']) else 0.0
    })

trades_json = json.dumps(trades)

html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Auto Trading Bot - Backtest Viewer</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0f172a;
            --panel-bg: #1e293b;
            --text-color: #f8fafc;
            --text-muted: #94a3b8;
            --border-color: #334155;
            --accent: #3b82f6;
            --success: #10b981;
            --danger: #ef4444;
        }}
        body {{
            font-family: 'Inter', -apple-system, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0 0 10px 0;
            background: linear-gradient(to right, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .controls {{
            background: var(--panel-bg);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            display: flex;
            gap: 20px;
            align-items: center;
            justify-content: center;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }}
        .control-group {{
            display: flex;
            flex-direction: column;
            gap: 5px;
        }}
        .control-group label {{
            font-size: 0.85rem;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        input[type="date"] {{
            background: var(--bg-color);
            color: var(--text-color);
            border: 1px solid var(--border-color);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 1rem;
            color-scheme: dark;
        }}
        button {{
            background: var(--accent);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: 600;
            cursor: pointer;
            transition: opacity 0.2s;
            margin-top: auto;
        }}
        button:hover {{ opacity: 0.9; }}
        
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: var(--panel-bg);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            text-align: center;
        }}
        .stat-value {{
            font-size: 2rem;
            font-weight: bold;
            margin: 10px 0 5px 0;
        }}
        .stat-label {{
            color: var(--text-muted);
            font-size: 0.9rem;
        }}
        .chart-container {{
            background: var(--panel-bg);
            padding: 20px;
            border-radius: 12px;
            border: 1px solid var(--border-color);
            height: 400px;
        }}
        .positive {{ color: var(--success); }}
        .negative {{ color: var(--danger); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Interactive Backtest Viewer</h1>
            <p style="color: var(--text-muted)">자유롭게 기간을 설정하여 백테스트 성과를 분석해보세요.</p>
        </div>

        <div class="controls">
            <div class="control-group">
                <label>시작일 (Start Date)</label>
                <input type="date" id="startDate" value="2020-01-01">
            </div>
            <div class="control-group">
                <label>종료일 (End Date)</label>
                <input type="date" id="endDate" value="2026-12-31">
            </div>
            <button onclick="updateDashboard()">조회하기 (Apply)</button>
        </div>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">총 수익금 (Net Profit)</div>
                <div class="stat-value" id="valNetProfit">$0</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">승률 (Win Rate)</div>
                <div class="stat-value" id="valWinRate">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">최대 낙폭 (MDD)</div>
                <div class="stat-value negative" id="valMDD">0%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">총 거래 횟수 (Total Trades)</div>
                <div class="stat-value" id="valTrades">0</div>
            </div>
        </div>

        <div class="chart-container">
            <canvas id="pnlChart"></canvas>
        </div>
    </div>

    <script>
        const allTrades = {trades_json};
        let pnlChart = null;

        function updateDashboard() {{
            const startStr = document.getElementById('startDate').value;
            const endStr = document.getElementById('endDate').value;
            
            if (!startStr || !endStr) return;

            const start = new Date(startStr);
            start.setHours(0,0,0,0);
            const end = new Date(endStr);
            end.setHours(23,59,59,999);

            // Filter trades
            const filtered = allTrades.filter(t => {{
                const d = new Date(t.entry_time);
                return d >= start && d <= end;
            }});

            // Calculate Stats
            let netProfit = 0;
            let wins = 0;
            let peak = 1000; // Base $1000
            let currentBalance = 1000;
            let maxDrawdown = 0;
            
            const chartLabels = [];
            const chartData = [];

            // Add initial point
            if(filtered.length > 0) {{
                 chartLabels.push(startStr);
                 chartData.push(1000);
            }}

            for (let t of filtered) {{
                netProfit += t.pnl;
                currentBalance += t.pnl;
                if (t.pnl > 0) wins++;
                
                if (currentBalance > peak) peak = currentBalance;
                
                const drawdown = (peak - currentBalance) / peak * 100;
                if (drawdown > maxDrawdown) maxDrawdown = drawdown;

                // Format date for chart
                const d = new Date(t.exit_time);
                chartLabels.push(d.toLocaleDateString('ko-KR'));
                chartData.push(currentBalance);
            }}

            const winRate = filtered.length > 0 ? (wins / filtered.length) * 100 : 0;

            // DOM Updates
            const profitEl = document.getElementById('valNetProfit');
            profitEl.textContent = (netProfit >= 0 ? '+$' : '-$') + Math.abs(netProfit).toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits:2}});
            profitEl.className = 'stat-value ' + (netProfit >= 0 ? 'positive' : 'negative');

            document.getElementById('valWinRate').textContent = winRate.toFixed(2) + '%';
            document.getElementById('valMDD').textContent = maxDrawdown.toFixed(2) + '%';
            document.getElementById('valTrades').textContent = filtered.length;

            // Update Chart
            updateChart(chartLabels, chartData);
        }}

        function updateChart(labels, data) {{
            const ctx = document.getElementById('pnlChart').getContext('2d');
            
            if (pnlChart) {{
                pnlChart.destroy();
            }}

            pnlChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: '포트폴리오 자산 변화 (Portfolio Balance)',
                        data: data,
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 0,
                        pointHitRadius: 10,
                        tension: 0.1
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{
                        intersect: false,
                        mode: 'index',
                    }},
                    scales: {{
                        y: {{
                            grid: {{ color: '#334155' }},
                            ticks: {{ color: '#94a3b8' }}
                        }},
                        x: {{
                            grid: {{ display: false }},
                            ticks: {{ 
                                color: '#94a3b8',
                                maxTicksLimit: 10
                            }}
                        }}
                    }},
                    plugins: {{
                        legend: {{
                            labels: {{ color: '#f8fafc' }}
                        }}
                    }}
                }}
            }});
        }}

        // Initial Load
        window.onload = () => {{
            // Set default end date to today
            document.getElementById('endDate').value = new Date().toISOString().split('T')[0];
            // Find earliest trade for start date
            if (allTrades.length > 0) {{
                 document.getElementById('startDate').value = allTrades[0].entry_time.split(' ')[0];
            }}
            updateDashboard();
        }};
    </script>
</body>
</html>
"""

with open('C:/Crypto_Auto_Trading-BOT/docs/index.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ Dashboard generated at C:/Crypto_Auto_Trading-BOT/docs/index.html")
