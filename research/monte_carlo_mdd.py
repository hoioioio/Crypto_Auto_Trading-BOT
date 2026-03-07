import pandas as pd
import numpy as np

def run_monte_carlo(csv_path='C:/backtest_trades_2020_now.csv', iterations=10000):
    print("🏦 Institutional Risk Team: Running Monte Carlo Sequence Analysis...")
    df = pd.read_csv(csv_path)
    
    # 1. Reconstruct the exact equity curve to find the % impact of each trade
    df['EntryTime'] = pd.to_datetime(df['EntryTime'])
    df['ExitTime'] = pd.to_datetime(df['ExitTime'])
    
    entries = df[['EntryTime', 'PnL']].copy()
    entries['type'] = 'entry'
    entries['time'] = entries['EntryTime']
    entries['id'] = entries.index
    
    exits = df[['ExitTime', 'PnL']].copy()
    exits['type'] = 'exit'
    exits['time'] = exits['ExitTime']
    exits['id'] = exits.index
    
    events = pd.concat([entries, exits]).sort_values(by=['time', 'type'])
    
    equity = 1000.0
    entry_equities = {}
    
    for _, e in events.iterrows():
        if e['type'] == 'entry':
            entry_equities[e['id']] = equity
        else:
            equity += e['PnL']
            
    # Calculate each trade's exact % return on the account balance at that time
    df['trade_ret_pct'] = df.apply(lambda row: row['PnL'] / entry_equities[row.name], axis=1)
    
    trade_returns = df['trade_ret_pct'].values
    
    print(f"✅ Extracted {len(trade_returns)} trade impacts. Baseline Final Equity: ${equity:,.0f}")
    print(f"🎲 Shuffling trade sequences {iterations} times...")
    
    mdds = []
    final_equities = []
    
    for i in range(iterations):
        # Scramble the chronological order of trades
        shuffled_returns = np.random.choice(trade_returns, size=len(trade_returns), replace=False)
        
        # Vectorized equity curve generation
        equity_curve = 1000.0 * np.cumprod(1 + shuffled_returns)
        
        # Calculate MDD of this specific timeline
        peak = np.maximum.accumulate(equity_curve)
        drawdown = (peak - equity_curve) / peak
        mdd = np.max(drawdown) * 100.0
        
        mdds.append(mdd)
        final_equities.append(equity_curve[-1])
        
        if i > 0 and i % 2500 == 0:
            print(f"   ... {i} simulations complete")
            
    mdds = np.array(mdds)
    
    print("\n" + "="*50)
    print("🚨 INSTITUTIONAL MONTE CARLO RESULTS (10,000 passes)")
    print("="*50)
    print(f"Median MDD         : {np.median(mdds):.2f}%")
    print(f"95% Confidence MDD : {np.percentile(mdds, 95):.2f}%")
    print(f"99% Confidence MDD : {np.percentile(mdds, 99):.2f}% (The True Worst Case)")
    print(f"Absolute Worst MDD : {np.max(mdds):.2f}%")
    print("="*50)
    
if __name__ == '__main__':
    run_monte_carlo()
