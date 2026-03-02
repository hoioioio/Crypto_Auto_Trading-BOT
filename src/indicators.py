import numpy as np
import pandas as pd

def calculate_awma(series: pd.Series, length=10, fast_end=2, slow_end=30) -> pd.Series:
    """
    Adaptive Weighted Moving Average (KAMA formulation)
    """
    # 1. Efficiency Ratio (ER): 가격 변화량 / 전체 변동성
    change = series.diff(length).abs()
    volatility = series.diff().abs().rolling(window=length).sum()
    er = (change / volatility).fillna(0)
    
    # 2. Smoothing Constant (SC)
    fast_sc = 2 / (fast_end + 1)
    slow_sc = 2 / (slow_end + 1)
    sc = (er * (fast_sc - slow_sc) + slow_sc) ** 2
    
    # 3. AMA Calculation (Vectorized & Numba optimizable)
    values = series.values
    sc_values = sc.values
    n = len(values)
    ama = np.zeros(n)
    ama[:] = np.nan
    
    start_idx = length
    if start_idx < n:
        ama[start_idx-1] = np.mean(values[:length]) 
        prev_ama = ama[start_idx-1]
        
        for i in range(start_idx, n):
            c = sc_values[i]
            price = values[i]
            if np.isnan(c) or np.isnan(price): continue
                
            current_ama = prev_ama + c * (price - prev_ama)
            ama[i] = current_ama
            prev_ama = current_ama
            
    return pd.Series(ama, index=series.index)
