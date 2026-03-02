from config import settings

def check_pyramiding_triggers(symbol, pos_data, ticker_data):
    """
    3-Stage Pyramiding Logic (Conditional Scaling-in)
    """
    current_stage = pos_data.get('stage', 1)
    entry_price = float(pos_data['entry_price'])
    current_price = float(ticker_data['last'])
    is_long = pos_data['side'] in ['buy', 'long']
    
    # Calculate Unrealized PnL %
    if is_long:
        pnl_pct = (current_price - entry_price) / entry_price * 100 * float(pos_data['leverage'])
    else:
        pnl_pct = (entry_price - current_price) / entry_price * 100 * float(pos_data['leverage'])
        
    # Stage 1 -> Stage 2 Trigger 
    if current_stage == 1 and pnl_pct >= settings.PYRAMID_TRIGGER_1: 
        add_qty = pos_data['total_target_qty'] * 0.3 # 30% 추가 진입
        # execute_market_order(symbol, pos_data['side'], add_qty, reason="Pyramid_Stage_2")
        pos_data['stage'] = 2
        
    # Stage 2 -> Stage 3 Trigger 
    elif current_stage == 2 and pnl_pct >= settings.PYRAMID_TRIGGER_2: 
        add_qty = pos_data['total_target_qty'] * 0.4 # 나머지 40% 풀매수
        # execute_market_order(symbol, pos_data['side'], add_qty, reason="Pyramid_Stage_3")
        pos_data['stage'] = 3
        
    return pos_data

def check_dynamic_early_exit(row, position):
    """
    Reversal Hunter: 변곡점 징조 감지 로직
    """
    current_mfi = row['mfi']
    rev_ma_val = row['rev_ma'] 
    close_price = row['close']
    
    exit_reason = None
    
    # [Long Position] 과매수 상태에서 가격이 단기 이평선 하방 이탈 시 즉시 청산
    if position['side'] == 'buy':
        if current_mfi > settings.EARLY_EXIT_MFI_OVERBOUGHT and close_price < rev_ma_val:
            exit_reason = 'Reversal_Overbought_Drop'
            
    # [Short Position] 과매도 상태에서 가격이 단기 이평선 상방 돌파 시 즉시 청산
    elif position['side'] == 'sell':
        if current_mfi < settings.EARLY_EXIT_MFI_OVERSOLD and close_price > rev_ma_val:
            exit_reason = 'Reversal_Oversold_Spike'
            
    return exit_reason
