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
    icon = "/paypal.svg"
    name = "PayPal"


class CreditCard(Payment):
    icon = "/credit-card.svg"
    name = "Credit Card"


class DebitCard(Payment):
    icon = "/debit-card.svg"
    name = "Debit Card"


class AliPay(Payment):
    icon = "/alipay.svg"
    name = "AliPay"


class WeChatPay(Payment):
    icon = "/wechatpay.svg"
    name = "WeChatPay"


class UnionPay(Payment):
    icon = "/unionpay.svg"
    name = "UnionPay"


class WebMoneyZ(Payment):
    icon = "/webmoney.svg"
    name = "WebMoney"


class PerfectMoney(Payment):
    icon = "/perfect-money.svg"
    name = "PerfectMoney"


class BTC(Payment):
    icon = "/btc.svg"
    name = "BTC"


class ETH(Payment):
    icon = "/eth.svg"
    name = "ETH"


class BankTransfer(Payment):
    icon = "/bank-transfer.svg"
    name = "Bank Transfer"
