from datetime import datetime as dt, timedelta
import typing
from base64 import b64encode
import enum

import aiohttp


UpgradeChatInterval = enum.Enum("UpgradeChatInterval", "day week month year")
UpgradeChatItemType = enum.Enum("UpgradeChatItemType", "UPGRADE SHOP")
UpgradeChatProductType = enum.Enum("UpgradeChatProductType", "DISCORD_ROLE SHOP_PRODUCT")
UpgradeChatPaymentProcessor = enum.Enum("UpgradeChatPaymentProcessor", "PAYPAL STRIPE")


class UpgradeChatUser(object):
    """
    A user object from the UpgradeChat API.
    """

    def __init__(self, discord_id:str, username:str):
        self.discord_id: int = int(discord_id)
        self.username: str = username

    def __repr__(self):
        return self.username


class UpgradeChatProduct(object):
    """
    A product from the UpgradeChat API.

    You only get these objects from an endpoint that we're not using, so it's unlikely to be used in VBU,
    but is here for completeness sake.
    """

    def __init__(
            self, uuid:str, checkout_uri:str, name:str, account_id:int, price:float, interval:UpgradeChatInterval, interval_count:int,
            free_trial_length:int, description:str, image_link:str, variable_price:bool, is_time_limited:bool, limited_inventory:bool,
            available_stock:int, shippable:bool, paymentless_trial:bool, product_types:typing.List[UpgradeChatProductType],
            created:dt, updated:dt, deleted:dt=None):
        self.uuid = uuid
        self.checkout_uri = checkout_uri
        self.name = name
        self.account_id = account_id
        self.price = price
        self.interval = interval
        self.interval_count = interval_count
        self.free_trial_length = free_trial_length
        self.description = description
        self.image_link = image_link
        self.variable_price = variable_price
        self.is_time_limited = is_time_limited
        self.limited_inventory = limited_inventory
        self.available_stock = available_stock
        self.shippable = shippable
        self.paymentless_trial = paymentless_trial
        self.product_types = product_types
        self.created = created
        self.updated = updated
        self.deleted = deleted

    @classmethod
    def from_api(cls, data):
        """
        Makes an instance of the object using a response from the API.
        """

        extras = {}
        extras["interval"] = UpgradeChatInterval[data.pop("interval")]
        extras["product_types"] = [UpgradeChatInterval[i] for i in data.pop("product_types")]
        if data.get("created"):
            extras["created"] = dt.strptime(data.pop("created"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("updated"):
            extras["updated"] = dt.strptime(data.pop("updated"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("deleted"):
            extras["deleted"] = dt.strptime(data.pop("deleted"), "%Y-%m-%dT%H:%M:%S.%fZ")
        return cls(**extras, **data)


class UpgradeChatOrderItem(object):
    """
    An order item from the UpgradeChat API.
    """

    def __init__(
            self, price:float, quantity:int, interval:UpgradeChatInterval, interval_count:int, free_trial_length:int, is_time_limited:bool,
            product:dict, discord_roles:typing.List[dict], product_types:typing.List[UpgradeChatProductType],
            payment_processor:UpgradeChatPaymentProcessor, payment_processor_record_id:str):
        self.price = price
        self.quantity = quantity
        self.interval = interval
        self.interval_count = interval_count
        self.free_trial_length = free_trial_length
        self.is_time_limited = is_time_limited
        self.discord_roles = discord_roles
        self.product_types = product_types
        self.payment_processor_record_id = payment_processor_record_id
        self.payment_processor = payment_processor

        self.product = product
        self.product_name = product['name']
        self.product_uuid = product['uuid']

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self.product_name}' ${self.price:.2f}>"

    @classmethod
    def from_api(cls, data):
        """
        Makes an instance of the object using a response from the API.
        """

        extras = {}
        if data.get("interval"):
            extras["interval"] = UpgradeChatInterval[data.pop("interval")]
        extras["product_types"] = [UpgradeChatProductType[i] for i in data.pop("product_types")]
        extras["payment_processor"] = UpgradeChatPaymentProcessor[data.pop("payment_processor")]
        return cls(**data, **extras)


class UpgradeChatOrder(object):
    """
    An order object from the UpgradeChat API.
    """

    def __init__(
            self, uuid:str, id:str, purchased_at:dt, user:UpgradeChatUser, subtotal:float, discount:float, total:float, type:UpgradeChatItemType,
            is_subscription:bool, cancelled_at:dt, order_items:typing.List[UpgradeChatOrderItem], created:dt, updated:dt,
            deleted:dt=None, payment_processor:UpgradeChatPaymentProcessor=None, payment_processor_record_id:str=None):
        self.uuid = uuid
        self.id = id
        self.purchased_at = purchased_at
        self.payment_processor = payment_processor
        self.payment_processor_record_id = payment_processor_record_id
        self.user = user
        self.subtotal = subtotal
        self.discount = discount
        self.total = total
        self.type = type
        self.is_subscription = is_subscription
        self.cancelled_at = cancelled_at
        self.deleted = deleted
        self.created = created
        self.updated = updated

        self.order_items = order_items
        self.order_item_names = [i.product_name for i in self.order_items]
        self.order_item_uuids = [i.product_uuid for i in self.order_items]

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.uuid}>"

    @classmethod
    def from_api(cls, data):
        """
        Makes an instance of the object using a response from the API.
        """

        extras = {}
        extras["user"] = UpgradeChatUser(**data.pop("user"))
        extras["payment_processor"] = UpgradeChatPaymentProcessor[data.pop("payment_processor")]
        extras["type"] = UpgradeChatItemType[data.pop("type")]
        extras["order_items"] = [UpgradeChatOrderItem.from_api(i) for i in data.pop("order_items", list())]
        extras["purchased_at"] = dt.strptime(data.pop("purchased_at"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("cancelled_at"):
            extras["cancelled_at"] = dt.strptime(data.pop("cancelled_at"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("deleted"):
            extras["deleted"] = dt.strptime(data.pop("deleted"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("created"):
            extras["created"] = dt.strptime(data.pop("created"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("updated"):
            extras["updated"] = dt.strptime(data.pop("updated"), "%Y-%m-%dT%H:%M:%S.%fZ")
        return cls(**data, **extras)


class UpgradeChat(object):
    """
    A wrapper around the UpgradeChat API.
    """

    BASE = "https://api.upgrade.chat/v1/{endpoint}"

    def __init__(self, client_id:str, client_secret:str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._basic_auth_token = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        self._access_token = None

    async def get_access_token(self) -> str:
        """
        Get an access token from their Oauth endpoint.
        """

        # See if we need to bother with a new token
        refresh = None
        if self._access_token is not None:
            token, refresh, expiry = self._access_token
            if expiry > (dt.utcnow() - timedelta(seconds=30)):
                pass
            else:
                return token

        # Set up params
        data = {
            "grant_type": "client_credentials",
        }

        # Set up headers
        headers = {
            "Authorization": f"Basic {self._basic_auth_token}",
            "Accept": "application/json",
        }

        # Get the token data
        async with aiohttp.ClientSession() as session:
            async with session.post("https://api.upgrade.chat/oauth/token", data=data, headers=headers) as r:
                data = await r.json()

        # Parse and store
        self._access_token = (data['access_token'], data['refresh_token'], dt.fromtimestamp(int(data['access_token_expires_in']) / 1_000))
        return self._access_token[0]

    async def get_orders(self, limit:int=100, offset:int=0, discord_id:int=None) -> typing.List[UpgradeChatOrder]:
        """
        Get a list of order objects that adhere to the request parameters given.

        Args:
            limit (int, optional): The number of responses to get.
            offset (int, optional): The offset that you want to get.
            discord_id (int, optional): The ID of the Discord user that you want to look up

        Returns:
            typing.List[UpgradeChatOrder]: A list of purchases that the user has made.
        """

        # Sort out our params
        params = {
            "limit": limit,
            "offset": offset,
        }
        if discord_id:
            params.update({"userDiscordId": discord_id})

        # And our headers
        access_token = await self.get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        # Send the web request
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE.format(endpoint="orders"), params=params, headers=headers) as r:
                data = await r.json()

        # Deal with our response
        if data.get("data"):
            return [UpgradeChatOrder.from_api(i) for i in data.get("data")]
        return []
