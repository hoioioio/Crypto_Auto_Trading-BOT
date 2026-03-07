import random
from datetime import datetime
from dateutil.relativedelta import relativedelta
import subprocess
import pandas as pd
import sys

def run_tests():
    start_bound = datetime(2020, 1, 1)
    end_bound = datetime(2025, 6, 1) # Ensure end is within bounds
    
    # generate random start dates
    delta_days = (end_bound - start_bound).days
    
    results = []
    
    print("🎲 Starting 10 Random 6-Month Period Backtests (Starting balance: $1000)")
    print("="*60)
    
    for i in range(10):
        rand_days = random.randint(0, delta_days)
        start_date = start_bound + relativedelta(days=rand_days)
        end_date = start_date + relativedelta(months=6)
        
        start_str = start_date.strftime("%Y-%m-%d 00:00:00")
        end_str = end_date.strftime("%Y-%m-%d 23:59:59")
        
        print(f"[{i+1}/10] Extracting: {start_str[:10]} ~ {end_str[:10]} ...", end="", flush=True)
        
        cmd = f"python c:/run_full_backtest_rebuild.py --start \"{start_str}\" --end \"{end_str}\" --risk 1.25"
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        try:
            df = pd.read_csv('c:/backtest_trades_2020_now.csv')
            if len(df) == 0:
                results.append((start_str, end_str, 1000.0, 0.0, 0))
                print(" 0 Trades")
                continue
                
            equity = 1000.0
            peak = 1000.0
            mdd = 0.0
            for _, r in df.iterrows():
                equity += float(r['PnL'])
                if equity > peak: peak = equity
                dd = (peak - equity) / peak * 100
                if dd > mdd: mdd = dd
            
            results.append((start_str, end_str, equity, mdd, len(df)))
            print(f" ${equity:,.2f} | MDD: {mdd:.1f}%")
        except:
            results.append((start_str, end_str, -1, -1, 0))
            print(" Error")
            
    print("\n" + "="*60)
    print("🔥 10 RANDOM RANGE TEST RESULTS (Institutional 1.25%)")
    print("="*60)
    for idx, (s, e, eq, mdd, num) in enumerate(results):
        status = "✅ PASS" if mdd < 45 else "⚠️ WARN"
        if eq < 1000: status = "📉 LOSS"
        print(f"Test {idx+1:2}: {s[:10]} to {e[:10]} | Vol: {num:3} | Eq: ${eq:9,.2f} | MDD: {mdd:4.1f}% | {status}")
    print("="*60)

if __name__ == '__main__':
    run_tests()
