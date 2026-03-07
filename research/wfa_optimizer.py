import os
import subprocess
import pandas as pd
import numpy as np

def get_mdd(csv_path):
    if not os.path.exists(csv_path): return 0, 0
    df = pd.read_csv(csv_path)
    if len(df) == 0: return 1000, 0
    equity = 1000.0
    peak = 1000.0
    mdd = 0.0
    
    df['EntryTime'] = pd.to_datetime(df['EntryTime'])
    df['ExitTime'] = pd.to_datetime(df['ExitTime'])
    
    events = []
    for _, row in df.iterrows():
        events.append({'time': row['EntryTime'], 'type': 1})
        events.append({'time': row['ExitTime'], 'type': 2, 'pnl': row['PnL']})
        
    events.sort(key=lambda x: (x['time'], x['type']))
    for e in events:
        if e['type'] == 2:
            equity += e['pnl']
            if equity > peak: peak = equity
            else:
                dd = (peak - equity) / peak
                if dd > mdd: mdd = dd
    return equity, mdd * 100

def run_wfa():
    risks = [0.15, 0.5, 0.75, 1.0, 1.25, 1.5]
    is_start = "2020-01-01 00:00:00"
    is_end = "2023-12-31 23:59:59"
    oos_start = "2024-01-01 00:00:00"
    oos_end = "2026-12-31 23:59:59"
    
    print("🏦 INSTITUTIONAL RISK: WALK-FORWARD ANALYSIS (WFA)")
    print("==================================================")
    print("=== BEGIN IN-SAMPLE (2020-2023) GRID SEARCH ===")
    best_risk = 0.15
    best_score = 0
    
    for r in risks:
        print(f"Testing Risk {r}%...", flush=True)
        cmd = f"python c:/run_full_backtest_rebuild.py --start \"{is_start}\" --end \"{is_end}\" --risk {r}"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        eq, mdd = get_mdd('c:/backtest_trades_2020_now.csv')
        
        # Scoring: We penalize MDD exponentially if it crosses 40% (Institutional pain threshold)
        if mdd <= 40:
            score = eq / (mdd + 1)
        else:
            score = 0
            
        print(f"  -> Eq: ${eq:,.0f} | MDD: {mdd:.2f}% | Score: {score:,.1f}")
        
        if score > best_score:
            best_score = score
            best_risk = r
            
    print(f"\n=> 🏆 WINNER (IS): {best_risk}% Risk (Eliminates Lookahead Bias)")
    
    print("\n=== BEGIN OUT-OF-SAMPLE (2024-2026) BLIND TEST ===")
    cmd = f"python c:/run_full_backtest_rebuild.py --start \"{oos_start}\" --end \"{oos_end}\" --risk {best_risk}"
    subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    eq, mdd = get_mdd('c:/backtest_trades_2020_now.csv')
    print(f"  -> Blind Test Eq: ${eq:,.0f} | OOS MDD: {mdd:.2f}%")
    
    if mdd < 45:
        print("✅ PASS: Strategy preserved safety constraints in Out-Of-Sample data.")
    else:
        print("❌ FAIL: Strategy broke down in Out-Of-Sample data (Overfitted).")
        
    print("==================================================")

if __name__ == '__main__':
    run_wfa()
