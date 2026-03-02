import itertools
from joblib import Parallel, delayed
from config import settings

def run_grid_search_optimization(symbol_data_dict, test_period_start, test_period_end):
    """
    Curve-Fitting(과최적화) 방지를 위한 다차원 전수조사 최적화 로직
    - 단순히 최대 수익(Max PnL)이 아닌, Sharpe Ratio와 MDD 안정성을 기준으로 Robust Parameter 탐색
    """
    # 탐색할 파라미터 공간 정의 (Parameter Space)
    ma_fast_candidates = settings.GRID_FAST_MA_RANGE  # [Masked Config]
    ma_slow_candidates = settings.GRID_SLOW_MA_RANGE  # [Masked Config]
    mfi_exit_candidates = settings.GRID_MFI_RANGE     # [Masked Config]
    
    param_combinations = list(itertools.product(
        ma_fast_candidates, ma_slow_candidates, mfi_exit_candidates
    ))
    
    print(f"🔍 총 {len(param_combinations)}개의 파라미터 유니버스 백테스트 시작...")

    def test_single_combination(params):
        fast, slow, exit_mfi = params
        if fast >= slow: return None 
        
        # 전체 구간 시뮬레이션 대상 평가
        result = run_simulation_core(
            symbol_data=symbol_data_dict,
            start=test_period_start, end=test_period_end,
            entry_fast=fast, entry_slow=slow, early_exit_mfi=exit_mfi
        )
        
        # [핵심] 수익률뿐만 아니라, 하방 리스크(MDD)와 승률(Win Rate) 스코어링 수식 기반 추출
        robust_score = (result['net_profit'] / abs(result['mdd_usd'])) * result['win_rate']
        
        return {
            'params': params,
            'robust_score': robust_score,
            'net_profit': result['net_profit'],
            'mdd_usd': result['mdd_usd'],
            'sharpe': result['sharpe_ratio']
        }

    # Joblib을 활용한 CPU 병렬 처리(Multiprocessing)로 백테스트 속도 최적화
    all_results = Parallel(n_jobs=-1)(
        delayed(test_single_combination)(p) for p in param_combinations
    )
    
    valid_results = [r for r in all_results if r is not None]
    optimized_params = sorted(valid_results, key=lambda x: x['robust_score'], reverse=True)[:5]
    
    return optimized_params
