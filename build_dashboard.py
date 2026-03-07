import pandas as pd
import json

def build():
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
    <title>Crypto Auto Trading Bot - Advanced Backtest Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #f8f9fa;
            --panel-bg: #ffffff;
            --text-color: #212529;
            --text-muted: #6c757d;
            --border-color: #dee2e6;
            --accent: #007bff;
            --success: #28a745;
            --danger: #dc3545;
            --header-bg: #e9ecef;
            --row-alt: #f1f3f5;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}
        h1, h2 {{ color: var(--accent); border-bottom: 2px solid var(--accent); padding-bottom: 10px; margin-top: 30px; }}
        
        .controls {{
            background: var(--panel-bg); padding: 20px; border-radius: 8px;
            border: 1px solid var(--border-color); display: flex; gap: 20px;
            align-items: center; justify-content: center; margin-bottom: 30px; flex-wrap: wrap;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .control-group {{ display: flex; flex-direction: column; gap: 5px; }}
        .control-group label {{ font-size: 0.85rem; color: var(--text-muted); font-weight: bold; }}
        input[type="date"] {{
            padding: 8px 12px; border-radius: 6px; border: 1px solid var(--border-color); font-size: 1rem;
        }}
        button {{
            background: var(--accent); color: white; border: none; padding: 10px 20px;
            border-radius: 6px; font-weight: bold; cursor: pointer; margin-top: auto;
        }}
        button:hover {{ opacity: 0.9; }}
        
        .summary {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
        .summary-card {{ 
            flex: 1 1 200px; background-color: var(--panel-bg); padding: 20px; 
            border-radius: 8px; text-align: center; border: 1px solid var(--border-color);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }}
        .summary-card h3 {{ margin-top: 0; color: #495057; font-size: 1.1rem; border: none; padding: 0; }}
        .stat-value {{ font-size: 24px; font-weight: bold; margin-top: 10px; }}
        .positive {{ color: var(--success); }}
        .negative {{ color: var(--danger); }}
        
        .charts {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 30px; }}
        .chart-box {{ 
            flex: 1 1 500px; background: var(--panel-bg); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            height: 350px;
        }}
        .chart-box-wide {{
            flex: 1 1 100%; background: var(--panel-bg); border: 1px solid var(--border-color);
            border-radius: 8px; padding: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.03);
            height: 400px;
        }}
        
        .data-section {{ display: flex; flex-wrap: wrap; gap: 20px; margin-bottom: 40px; }}
        .data-table-wrapper {{ flex: 1 1 500px; background: var(--panel-bg); padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); border: 1px solid var(--border-color); overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; margin-top: 15px; font-size: 0.9rem; }}
        th, td {{ border: 1px solid var(--border-color); padding: 10px 12px; text-align: right; }}
        th {{ background-color: var(--header-bg); text-align: center; font-weight: bold; }}
        td:first-child {{ text-align: left; font-weight: bold; }}
        tbody tr:nth-child(even) {{ background-color: var(--row-alt); }}
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align: center; border: none;">📈 성과 분석 리포트 (Interactive Dashboard)</h1>
        
        <div class="controls">
            <div class="control-group">
                <label>시작일 (Start Date)</label>
                <input type="date" id="startDate">
            </div>
            <div class="control-group">
                <label>종료일 (End Date)</label>
                <input type="date" id="endDate">
            </div>
            <button onclick="updateDashboard()">조회하기 (Apply)</button>
        </div>

        <h2>📊 전체 기간 요약</h2>
        <div class="summary">
            <div class="summary-card">
                <h3>총 손익 (Total PnL)</h3>
                <div class="stat-value" id="valNetProfit">$0</div>
            </div>
            <div class="summary-card" style="background-color: #f1f8ff; border-color: #cce5ff;">
                <h3>최종 자산 (Final Equity)</h3>
                <div class="stat-value" id="valFinalEquity" style="color: #004085;">$0</div>
            </div>
            <div class="summary-card">
                <h3>총 거래 (Total Trades)</h3>
                <div class="stat-value" id="valTrades" style="color: #212529;">0</div>
            </div>
            <div class="summary-card">
                <h3>승률 (Win Rate)</h3>
                <div class="stat-value" id="valWinRate" style="color: #212529;">0%</div>
            </div>
            <div class="summary-card">
                <h3>승/패 (W/L)</h3>
                <div class="stat-value" id="valWL" style="color: #212529;">0 / 0</div>
            </div>
            <div class="summary-card">
                <h3>최대 낙폭 (MDD)</h3>
                <div class="stat-value negative" id="valMDD">0%</div>
            </div>
        </div>

        <h2>🎨 시각화 차트</h2>
        <div class="charts">
            <div class="chart-box">
                <h3 style="text-align:center; margin-top:0;">월별 손익 (Monthly PnL)</h3>
                <canvas id="monthlyChart"></canvas>
            </div>
            <div class="chart-box">
                <h3 style="text-align:center; margin-top:0;">누적 손익 (Cumulative PnL)</h3>
                <canvas id="cumulativeChart"></canvas>
            </div>
        </div>
        <div class="charts">
            <div class="chart-box-wide">
                <h3 style="text-align:center; margin-top:0;">종목별 총 손익 (Total PnL by Symbol)</h3>
                <canvas id="symbolChart"></canvas>
            </div>
        </div>

        <div class="data-section">
            <div class="data-table-wrapper">
                <h2 style="margin-top:0;">📋 월별 상세 데이터</h2>
                <table id="monthlyTable">
                    <thead>
                        <tr>
                            <th>월 (Month)</th>
                            <th>총 손익 (Total PnL)</th>
                            <th>총 거래</th>
                            <th>승/패</th>
                            <th>승률 (%)</th>
                            <th>평균 수익</th>
                            <th>평균 손실</th>
                            <th>손익비 (Payoff)</th>
                            <th>누적 수익</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
            <div class="data-table-wrapper">
                <h2 style="margin-top:0;">📈 종목별 상세 데이터</h2>
                <table id="symbolTable">
                    <thead>
                        <tr>
                            <th>종목 (Symbol)</th>
                            <th>총 손익 (Total PnL)</th>
                            <th>총 거래</th>
                            <th>승/패</th>
                            <th>승률 (%)</th>
                            <th>평균 수익</th>
                            <th>평균 손실</th>
                            <th>손익비 (Payoff)</th>
                        </tr>
                    </thead>
                    <tbody></tbody>
                </table>
            </div>
        </div>
    </div>

    <script>
        const allTrades = {trades_json};
        
        // 🌟 Pre-calculate exact Account Equity for EVERY trade before filtering
        // 🌟 Pre-calculate exact Account Equity & Return % for EVERY trade
        let globalEquity = 1000;
        for (let t of allTrades) {{
            t.ret_pct = t.pnl / globalEquity;
            globalEquity += t.pnl;
            t.account_equity = globalEquity;
        }}
        
        let charts = {{}};

        function formatUSD(val) {{
            return (val >= 0 ? '$' : '-$') + Math.abs(val).toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
        }}
        function colorClass(val) {{
            return val >= 0 ? 'positive' : 'negative';
        }}

        function updateDashboard() {{
            const startStr = document.getElementById('startDate').value;
            const endStr = document.getElementById('endDate').value;
            if (!startStr || !endStr) return;

            const start = new Date(startStr); start.setHours(0,0,0,0);
            const end = new Date(endStr); end.setHours(23,59,59,999);

            const filtered = allTrades.filter(t => {{
                const d = new Date(t.entry_time);
                return d >= start && d <= end;
            }});

            // 1. Overall Stats
            let netProfit = 0, wins = 0, losses = 0;
            let peakObj = 1000, maxDrawdown = 0;
            let virtualEquity = 1000;
            
            // Map for Monthly / Symbol
            let monthlyData = {{}};
            let symbolData = {{}};

            for (let t of filtered) {{
                let v_pnl = virtualEquity * t.ret_pct;
                netProfit += v_pnl;
                virtualEquity += v_pnl;
                
                if (v_pnl > 0) wins++; else losses++;
                
                if (virtualEquity > peakObj) peakObj = virtualEquity;
                const drawdown = (peakObj - virtualEquity) / peakObj * 100;
                if (drawdown > maxDrawdown) maxDrawdown = drawdown;

                // Monthly grouping
                const dateObj = new Date(t.exit_time);
                const monthKey = dateObj.getFullYear() + '-' + String(dateObj.getMonth() + 1).padStart(2, '0');
                if(!monthlyData[monthKey]) monthlyData[monthKey] = {{pnl:0, trades:0, wins:0, loss:0, winPnl:0, lossPnl:0}};
                
                monthlyData[monthKey].pnl += v_pnl;
                monthlyData[monthKey].trades++;
                if(v_pnl > 0) {{ monthlyData[monthKey].wins++; monthlyData[monthKey].winPnl += v_pnl; }}
                else {{ monthlyData[monthKey].loss++; monthlyData[monthKey].lossPnl += v_pnl; }}

                // Symbol grouping
                const sym = t.symbol;
                if(!symbolData[sym]) symbolData[sym] = {{pnl:0, trades:0, wins:0, loss:0, winPnl:0, lossPnl:0}};
                
                symbolData[sym].pnl += v_pnl;
                symbolData[sym].trades++;
                if(v_pnl > 0) {{ symbolData[sym].wins++; symbolData[sym].winPnl += v_pnl; }}
                else {{ symbolData[sym].loss++; symbolData[sym].lossPnl += v_pnl; }}
            }}

            const winRate = filtered.length > 0 ? (wins / filtered.length) * 100 : 0;

            // DOM Updates Summary
            const profitEl = document.getElementById('valNetProfit');
            profitEl.textContent = formatUSD(netProfit);
            profitEl.className = 'stat-value ' + colorClass(netProfit);

            document.getElementById('valFinalEquity').textContent = formatUSD(virtualEquity);

            document.getElementById('valTrades').textContent = filtered.length;
            document.getElementById('valWinRate').textContent = winRate.toFixed(2) + '%';
            document.getElementById('valWL').textContent = wins + ' / ' + losses;
            document.getElementById('valMDD').textContent = maxDrawdown.toFixed(2) + '%';

            // 2. Prepare Monthly Table & Charts
            const sortedMonths = Object.keys(monthlyData).sort();
            const monthlyLabels = [];
            const monthlyPnlData = [];
            const monthlyColors = [];
            
            const cumulativeLabels = [];
            const cumulativeData = [];
            let rCumul = 1000;
            if(sortedMonths.length > 0) {{ cumulativeLabels.push('Start'); cumulativeData.push(1000); }}

            const mBody = document.querySelector('#monthlyTable tbody');
            mBody.innerHTML = '';
            
            for(let m of sortedMonths) {{
                const d = monthlyData[m];
                monthlyLabels.push(m);
                monthlyPnlData.push(d.pnl);
                monthlyColors.push(d.pnl >= 0 ? '#28a745' : '#dc3545');

                rCumul += d.pnl;
                cumulativeLabels.push(m);
                cumulativeData.push(rCumul);

                const wr = d.trades > 0 ? (d.wins / d.trades * 100).toFixed(2) : '0.00';
                const aw = d.wins > 0 ? (d.winPnl / d.wins) : 0;
                const al = d.loss > 0 ? (d.lossPnl / d.loss) : 0;
                const payoff = al !== 0 ? Math.abs(aw / al).toFixed(2) : '∞';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${{m}}</td>
                    <td class="${{colorClass(d.pnl)}}">${{formatUSD(d.pnl)}}</td>
                    <td>${{d.trades}}</td>
                    <td>${{d.wins}} / ${{d.loss}}</td>
                    <td>${{wr}}%</td>
                    <td>${{formatUSD(aw)}}</td>
                    <td>${{formatUSD(al)}}</td>
                    <td>${{payoff}}</td>
                    <td class="${{colorClass(rCumul-1000)}}">${{formatUSD(rCumul-1000)}}</td>
                `;
                mBody.appendChild(tr);
            }}

            // 3. Prepare Symbol Table & Charts
            const sortedSymbols = Object.keys(symbolData).sort((a,b) => symbolData[b].pnl - symbolData[a].pnl);
            const symbolLabels = [];
            const symbolPnlData = [];
            const symbolColors = [];

            const sBody = document.querySelector('#symbolTable tbody');
            sBody.innerHTML = '';

            for(let s of sortedSymbols) {{
                const d = symbolData[s];
                symbolLabels.push(s);
                symbolPnlData.push(d.pnl);
                symbolColors.push(d.pnl >= 0 ? '#28a745' : '#dc3545');

                const wr = d.trades > 0 ? (d.wins / d.trades * 100).toFixed(2) : '0.00';
                const aw = d.wins > 0 ? (d.winPnl / d.wins) : 0;
                const al = d.loss > 0 ? (d.lossPnl / d.loss) : 0;
                const payoff = al !== 0 ? Math.abs(aw / al).toFixed(2) : '∞';

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${{s}}</td>
                    <td class="${{colorClass(d.pnl)}}">${{formatUSD(d.pnl)}}</td>
                    <td>${{d.trades}}</td>
                    <td>${{d.wins}} / ${{d.loss}}</td>
                    <td>${{wr}}%</td>
                    <td>${{formatUSD(aw)}}</td>
                    <td>${{formatUSD(al)}}</td>
                    <td>${{payoff}}</td>
                `;
                sBody.appendChild(tr);
            }}

            // Render Charts
            renderChart('monthlyChart', 'bar', monthlyLabels, '월별 수익금 ($)', monthlyPnlData, monthlyColors);
            renderChart('cumulativeChart', 'line', cumulativeLabels, '누적 자산 ($)', cumulativeData, '#007bff');
            renderChart('symbolChart', 'bar', symbolLabels, '종목별 수익금 ($)', symbolPnlData, symbolColors);
        }}

        function renderChart(id, type, labels, label, data, colors) {{
            const ctx = document.getElementById(id).getContext('2d');
            if(charts[id]) charts[id].destroy();

            const config = {{
                type: type,
                data: {{
                    labels: labels,
                    datasets: [{{
                        label: label,
                        data: data,
                        backgroundColor: type === 'line' ? 'rgba(0,123,255,0.1)' : colors,
                        borderColor: type === 'line' ? colors : 'transparent',
                        borderWidth: type === 'line' ? 2 : 0,
                        fill: type === 'line',
                        tension: 0.1,
                        pointRadius: type === 'line' ? 0 : 3
                    }}]
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    interaction: {{ mode: 'index', intersect: false }},
                    plugins: {{ legend: {{ display: type === 'line' }} }}
                }}
            }};
            charts[id] = new Chart(ctx, config);
        }}

        window.onload = () => {{
            const endNode = document.getElementById('endDate');
            const startNode = document.getElementById('startDate');
            
            endNode.value = new Date().toISOString().split('T')[0];
            if (allTrades.length > 0) {{
                const d = new Date(allTrades[0].entry_time);
                startNode.value = d.toISOString().split('T')[0];
            }} else {{
                startNode.value = '2020-01-01';
            }}
            updateDashboard();
        }};
    </script>
</body>
</html>
"""

    with open('C:/Crypto_Auto_Trading-BOT/docs/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("✅ Rich HTML Dashboard updated!")

if __name__ == "__main__":
    build()
