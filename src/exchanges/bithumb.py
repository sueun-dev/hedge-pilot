"""
Bithumb Native API 거래소 클래스
"""
import hashlib
import hmac
import base64
import time
import urllib.parse
import requests
import logging
from typing import Dict, Optional

class BithumbExchange:
    """Bithumb Native API 거래소 구현"""
    
    def __init__(self, api_key: str, api_secret: str):
        self.exchange_id = 'bithumb'
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Configure logging
        self.logger = logging.getLogger(f"{__name__}.{self.exchange_id}")
        
        # API endpoints
        self.public_api_url = "https://api.bithumb.com/public"
        self.private_api_url = "https://api.bithumb.com"
        
        # Session for HTTP requests
        self.session = requests.Session()
        self.session.headers.update({
            'Api-Key': self.api_key,
            'Api-Sign': '',
            'Api-Nonce': ''
        })
    
    def _create_signature(self, endpoint: str, params: Dict) -> Dict:
        """Create signature for private API calls"""
        nonce = str(int(time.time() * 1000))
        
        # Create the message to sign
        data = endpoint + chr(0) + urllib.parse.urlencode(params) + chr(0) + nonce
        
        # Create signature
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            data.encode('utf-8'),
            hashlib.sha512
        ).hexdigest()
        
        # Encode signature
        api_sign = base64.b64encode(signature.encode('utf-8')).decode('utf-8')
        
        return {
            'Api-Key': self.api_key,
            'Api-Sign': api_sign,
            'Api-Nonce': nonce,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    
    def _public_api_call(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make public API call"""
        try:
            url = f"{self.public_api_url}/{endpoint}"
            if params:
                url += f"/{params.get('order_currency', 'ALL')}_{params.get('payment_currency', 'KRW')}"
            
            response = self.session.get(url)
            data = response.json()
            
            if data.get('status') == '0000':
                return data.get('data')
            else:
                self.logger.error(f"API error: {data.get('message')}")
                return None
        except Exception as e:
            self.logger.error(f"Public API call failed: {e}")
            return None
    
    def _private_api_call(self, endpoint: str, params: Dict) -> Optional[Dict]:
        """Make private API call"""
        try:
            url = f"{self.private_api_url}{endpoint}"
            headers = self._create_signature(endpoint, params)
            
            response = self.session.post(url, headers=headers, data=params)
            data = response.json()
            
            if data.get('status') == '0000':
                return data.get('data')
            else:
                self.logger.error(f"API error: {data.get('message')}")
                return None
        except Exception as e:
            self.logger.error(f"Private API call failed: {e}")
            return None
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get ticker information"""
        try:
            # Convert symbol format: XRP/KRW -> XRP_KRW
            base, quote = symbol.split('/')
            
            data = self._public_api_call('ticker', {
                'order_currency': base,
                'payment_currency': quote
            })
            
            if data:
                return {
                    'symbol': symbol,
                    'last': float(data['closing_price']),
                    'bid': None,  # Bithumb doesn't provide bid/ask in ticker
                    'ask': None,
                    'high': float(data['max_price']),
                    'low': float(data['min_price']),
                    'volume': float(data['units_traded'])
                }
            return None
        except Exception as e:
            self.logger.error(f"Failed to get ticker for {symbol}: {e}")
            return None
    
    def get_balance(self, currency: str) -> Optional[Dict]:
        """Get balance for a specific currency"""
        try:
            params = {
                'currency': currency
            }
            
            data = self._private_api_call('/info/balance', params)
            
            if data:
                total = float(data.get(f'total_{currency.lower()}', 0))
                in_use = float(data.get(f'in_use_{currency.lower()}', 0))
                available = float(data.get(f'available_{currency.lower()}', 0))
                
                return {
                    'free': available,
                    'used': in_use,
                    'total': total
                }
            return {'free': 0, 'used': 0, 'total': 0}
        except Exception as e:
            self.logger.error(f"Failed to get balance for {currency}: {e}")
            return None
    
    def create_market_order(self, symbol: str, side: str, amount: float, params: Optional[Dict] = None) -> Optional[Dict]:
        """Create a market order"""
        try:
            # Convert symbol format: XRP/KRW -> XRP
            base, quote = symbol.split('/')
            
            if side == 'buy':
                # For buy orders, calculate the quantity based on KRW amount
                ticker = self.get_ticker(symbol)
                if not ticker:
                    return None
                
                # Calculate quantity from KRW amount
                quantity = amount / ticker['last']
                # Round to 8 decimal places
                quantity = round(quantity, 8)
                
                order_params = {
                    'order_currency': base,
                    'payment_currency': quote,
                    'units': str(quantity),
                    'type': 'bid'  # market buy
                }
            else:
                # For sell orders, amount is the quantity
                order_params = {
                    'order_currency': base,
                    'payment_currency': quote,
                    'units': str(amount),
                    'type': 'ask'  # market sell
                }
            
            data = self._private_api_call('/trade/market', order_params)
            
            if data:
                self.logger.info(f"Market order placed: {symbol} {side} {amount}")
                return {
                    'id': data.get('order_id'),
                    'symbol': symbol,
                    'side': side,
                    'amount': amount,
                    'status': 'closed',  # Market orders are immediately executed
                    'filled': amount
                }
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to create market order: {e}")
            return None
    
    def get_markets(self) -> Dict:
        """Get all markets"""
        # For simplicity, return empty dict as we focus on KRW markets
        return {}
    
    def get_usdt_krw_price(self) -> Optional[float]:
        """Get USDT/KRW price"""
        ticker = self.get_ticker('USDT/KRW')
        return ticker['last'] if ticker else None
    
    @property
    def exchange(self):
        """Compatibility property"""
        return self