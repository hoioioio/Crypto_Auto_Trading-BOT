from config import settings
from utils.logger import send_telegram_message

def update_hard_sl_exchange(symbol, side, sl_price, exchange):
    """
    Flash Crash Protection: 거래소 서버 직접 체결 스탑로스
    """
    try:
        # 1. Cancel Existing Stops to avoid ghost triggers
        open_orders = exchange.fetch_open_orders(symbol)
        for o in open_orders:
            if o['type'] == 'STOP_MARKET':
                exchange.cancel_order(o['id'], symbol)
                
        # 2. Place New Stop Order
        stop_side = 'sell' if side in ['buy', 'long'] else 'buy'
        sl_price_str = exchange.price_to_precision(symbol, sl_price)
        
        # 'closePosition=True'를 사용하여 수량 잔차(Precision) 에러 억제
        params = {
            'stopPrice': float(sl_price_str),
            'closePosition': True, 
            'workingType': 'MARK_PRICE' 
        }
        
        exchange.create_order(symbol, 'STOP_MARKET', stop_side, None, None, params)
        print(f"✅ {symbol} Hard SL Activated at: {sl_price_str}")
        
    except Exception as e:
        send_telegram_message(f"🚨 [Hard_SL_Update_Failed] {symbol} 비상 스탑로스 설정 실패: {e}")

def execute_market_order(symbol, side, amount, exchange, reason="Unknown"):
    """
    Paper Trading 호환 주문 체결 엔진
    - LIVE_MODE에 따라 실제 거래소 API를 타거나, 로컬 가상 원장(In-Memory DB)을 업데이트함.
    """
    try:
        if settings.LIVE_MODE:
            # 실제 거래소 API 호출
            order = exchange.create_market_order(symbol, side, amount)
            send_telegram_message(f"✅ [REAL] {symbol} {side.upper()} 체결 완료! ({reason})")
            return order
        else:
            # 가상 모의 투자 (Paper Trading) 로직 
            # 슬리피지(Slippage)와 수수료(Fee)를 실제와 똑같이 모사하여 가상 원장에 기록
            simulated_price = get_current_tick_price(symbol, exchange) # Pseudo-function mapping
            simulated_fee = amount * simulated_price * settings.TAKER_FEE_RATE
            
            # 로컬 가상 포지션 객체 라이프사이클 업데이트
            update_virtual_position(symbol, side, amount, simulated_price, simulated_fee) # Pseudo-function
            
            print(f"🔄 [MOCK] 가상 체결 완료: {side.upper()} {amount} at {simulated_price} ({reason})")
            return {"status": "mock_success", "price": simulated_price, "amount": amount}
            
    except Exception as e:
        send_telegram_message(f"🚨 주문 실행 중 오류 발생: {e}")
        return None
