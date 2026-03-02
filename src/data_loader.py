import pandas as pd
from config import settings
from utils.logger import send_telegram_message

def fetch_ohlcv_live(symbol, timeframe, exchange, limit=1500):
    """
    Data Pipeline: Deep Warm-up (History Cache + Live API Supply)
    - 백테스트와 실거래 간의 지표 브리징(Bridging)을 위해 과거 데이터(Pickle)와 실시간 API 데이터를 병합
    """
    try:
        # 1. 로컬 캐시에서 과거 데이터(History Base) 고속 로딩
        hist_df = preload_history(symbol, timeframe) # Pseudo Function
        
        # 2. 거래소 API에서 최신(Fresh) 캔들 데이터 Fetch
        data = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        if not data: 
            return hist_df if not hist_df.empty else pd.DataFrame() 

        fresh_df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        fresh_df['datetime'] = pd.to_datetime(fresh_df['timestamp'], unit='ms', utc=True)
        fresh_df.set_index('datetime', inplace=True)
        fresh_df = fresh_df[['open', 'high', 'low', 'close', 'volume']]
        
        # 3. 과거 데이터와 실시간 데이터의 무결성 병합 (Merge & Deduplicate)
        if not hist_df.empty:
            combined_df = pd.concat([hist_df, fresh_df])
            combined_df = combined_df[~combined_df.index.duplicated(keep='last')]
            combined_df.sort_index(inplace=True)
            return combined_df
        else:
            return fresh_df

    except Exception as e:
        send_telegram_message(f"⚠️ {symbol} Live API Fetch Failed, using Cache fallback: {e}")
        return _HISTORY_CACHE.get((symbol, timeframe), pd.DataFrame())
