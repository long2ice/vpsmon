import abc


class Payment(abc.ABC):
    icon: str
    name: str

    @classmethod
    def dict(cls):
        return {
            "icon": cls.icon,
            "name": cls.name,
        }


class PayPal(Payment):
    icon = "/payment/paypal.svg"
    name = "PayPal"


class CreditCard(Payment):
    icon = "/payment/credit-card.svg"
    name = "Credit Card"


class DebitCard(Payment):
    icon = "/payment/debit-card.svg"
    name = "Debit Card"


class AliPay(Payment):
    icon = "/payment/alipay.svg"
    name = "AliPay"


class WeChatPay(Payment):
    icon = "/payment/wechatpay.svg"
    name = "WeChatPay"


class UnionPay(Payment):
    icon = "/payment/unionpay.svg"
    name = "UnionPay"


class WebMoneyZ(Payment):
    icon = "/payment/webmoney.svg"
    name = "WebMoney"


class PerfectMoney(Payment):
    icon = "/payment/perfect-money.svg"
    name = "PerfectMoney"


class BTC(Payment):
    icon = "/payment/btc.svg"
    name = "BTC"


class ETH(Payment):
    icon = "/payment/eth.svg"
    name = "ETH"


class USDT(Payment):
    icon = "/payment/usdt.svg"
    name = "USDT"


class BankTransfer(Payment):
    icon = "/payment/bank-transfer.svg"
    name = "Bank Transfer"


class Stripe(Payment):
    icon = "/payment/stripe.svg"
    name = "Stripe"


class WireTransfer(Payment):
    icon = "/payment/wire-transfer.svg"
    name = "WireTransfer"


class GiftCard(Payment):
    icon = "/payment/gift-card.svg"
    name = "GiftCard"


class GooglePay(Payment):
    icon = "/payment/google-pay.svg"
    name = "GooglePay"


class ApplePay(Payment):
    icon = "/payment/apple-pay.svg"
    name = "ApplePay"
