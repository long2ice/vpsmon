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
    icon = "https://www.paypalobjects.com/webstatic/icon/favicon.ico"
    name = "PayPal"


class CreditCard(Payment):
    icon = ""
    name = "Credit Card"


class DebitCard(Payment):
    icon = ""
    name = "Debit Card"


class AliPay(Payment):
    icon = ""
    name = "AliPay"


class UnionPay(Payment):
    icon = ""
    name = "UnionPay"


class WebMoneyZ(Payment):
    icon = ""
    name = "WebMoney"


class PerfectMoney(Payment):
    icon = ""
    name = "PerfectMoney"


class BTC(Payment):
    icon = ""
    name = "BTC"


class ETH(Payment):
    icon = ""
    name = "ETH"


class BankTransfer(Payment):
    icon = ""
    name = "Bank Transfer"
