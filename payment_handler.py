"""
Payment Handler - M-Pesa, Binance, Card, Bank
"""
import requests
import base64
import json
from datetime import datetime
from config import (
    MPESA_CONSUMER_KEY, MPESA_CONSUMER_SECRET,
    MPESA_SHORTCODE, MPESA_PASSKEY, MPESA_CALLBACK_URL,
    BINANCE_API_KEY, BINANCE_SECRET_KEY
)


class PaymentHandler:
    
    # ─────────────────────────────────────────────
    # M-PESA (Safaricom Daraja API)
    # ─────────────────────────────────────────────
    
    def get_mpesa_token(self):
        """Get M-Pesa OAuth token"""
        try:
            credentials = base64.b64encode(
                f"{MPESA_CONSUMER_KEY}:{MPESA_CONSUMER_SECRET}".encode()
            ).decode()
            
            response = requests.get(
                "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
                headers={"Authorization": f"Basic {credentials}"},
                timeout=10
            )
            return response.json().get("access_token")
        except Exception as e:
            print(f"M-Pesa token error: {e}")
            return None
    
    def send_stk_push(self, phone: str, amount: int, account_ref: str) -> dict:
        """
        Send STK Push to user's phone
        phone: format 254XXXXXXXXX
        amount: KES amount
        """
        token = self.get_mpesa_token()
        if not token:
            return {"success": False, "error": "Token failed"}
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password = base64.b64encode(
            f"{MPESA_SHORTCODE}{MPESA_PASSKEY}{timestamp}".encode()
        ).decode()
        
        payload = {
            "BusinessShortCode": MPESA_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": MPESA_SHORTCODE,
            "PhoneNumber": phone,
            "CallBackURL": MPESA_CALLBACK_URL,
            "AccountReference": account_ref,
            "TransactionDesc": "FirmwareShop Credits"
        }
        
        try:
            response = requests.post(
                "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            result = response.json()
            
            if result.get("ResponseCode") == "0":
                return {
                    "success": True,
                    "checkout_request_id": result.get("CheckoutRequestID"),
                    "message": "STK Push sent to your phone"
                }
            else:
                return {"success": False, "error": result.get("ResponseDescription")}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_mpesa_code(self, transaction_code: str, expected_amount: float) -> bool:
        """
        Verify M-Pesa transaction via Daraja API
        In production: use transaction status query API
        For demo: basic validation
        """
        # Basic format validation (M-Pesa codes are 10 alphanumeric chars)
        if len(transaction_code) < 8 or len(transaction_code) > 12:
            return False
        
        if not transaction_code.isalnum():
            return False
        
        # In PRODUCTION: Query Safaricom transaction status
        # token = self.get_mpesa_token()
        # response = requests.post(
        #     "https://api.safaricom.co.ke/mpesa/transactionstatus/v1/query",
        #     headers={"Authorization": f"Bearer {token}"},
        #     json={"TransactionID": transaction_code, ...}
        # )
        # Use the response to verify amount matches
        
        # For now: Return False to queue for manual review
        # Change to True in testing environment
        return False  # Will go to pending queue
    
    # ─────────────────────────────────────────────
    # BINANCE PAY
    # ─────────────────────────────────────────────
    
    def create_binance_order(self, amount_usdt: float, order_id: str) -> dict:
        """Create a Binance Pay order"""
        try:
            import hmac
            import hashlib
            import time
            
            timestamp = int(time.time() * 1000)
            nonce = str(timestamp)
            
            payload = {
                "env": {"terminalType": "APP"},
                "merchantTradeNo": order_id,
                "orderAmount": str(amount_usdt),
                "currency": "USDT",
                "goods": {
                    "goodsType": "02",
                    "goodsCategory": "Z000",
                    "referenceGoodsId": order_id,
                    "goodsName": "FirmwareShop Credits",
                }
            }
            
            payload_str = json.dumps(payload)
            signature_payload = f"{timestamp}\n{nonce}\n{payload_str}\n"
            signature = hmac.new(
                BINANCE_SECRET_KEY.encode(),
                signature_payload.encode(),
                hashlib.sha512
            ).hexdigest().upper()
            
            response = requests.post(
                "https://bpay.binanceapi.com/binancepay/openapi/order",
                headers={
                    "BinancePay-Timestamp": str(timestamp),
                    "BinancePay-Nonce": nonce,
                    "BinancePay-Certificate-SN": BINANCE_API_KEY,
                    "BinancePay-Signature": signature,
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            
            result = response.json()
            if result.get("status") == "SUCCESS":
                return {
                    "success": True,
                    "checkout_url": result["data"]["checkoutUrl"],
                    "qr_code": result["data"].get("qrcodeLink", "")
                }
            return {"success": False, "error": result.get("errorMessage")}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def verify_crypto_txid(self, txid: str, amount: float, network: str = "TRC20") -> bool:
        """
        Verify crypto transaction on blockchain
        In production: use block explorer API
        """
        # For TRC20 (Tron): Use TronScan API
        # For BEP20 (BSC): Use BscScan API
        # For now: Queue for manual review
        return False
    
    # ─────────────────────────────────────────────
    # UTILITY
    # ─────────────────────────────────────────────
    
    def format_phone_ke(self, phone: str) -> str:
        """Format phone to 254XXXXXXXXX"""
        phone = phone.strip().replace(" ", "").replace("-", "")
        if phone.startswith("0"):
            phone = "254" + phone[1:]
        elif phone.startswith("+"):
            phone = phone[1:]
        return phone
    
    def usd_to_kes(self, usd: float) -> int:
        """Convert USD to KES (approximate)"""
        rate = 130  # Update periodically
        return int(usd * rate)
    
    def generate_order_id(self, user_id: int) -> str:
        """Generate unique order ID"""
        ts = int(datetime.now().timestamp())
        return f"FW{user_id}{ts}"[-20:]
