from datetime import datetime as dt, timedelta
import typing
from base64 import b64encode

import aiohttp


class UpgradeChatUser(object):
    """
    A user object from the UpgradeChat API.
    """

    def __init__(self, discord_id:str, username:str):
        self.discord_id: int = int(discord_id)
        self.username: str = username

    def __repr__(self):
        return self.username


class UpgradeChatOrderItem(object):
    """
    An order item from the UpgradeChat API.
    """

    def __init__(
            self, price:float, quantity:int, interval:str, interval_count:int, free_trial_length:int, is_time_limited:bool, product:dict,
            discord_roles:typing.List[dict], product_types:typing.List[str], payment_processor_record_id:str=None, payment_processor:str=None):
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

        self.product_name = product['name']
        self.product_uuid = product['uuid']

    def __repr__(self):
        return f"<{self.__class__.__name__} ${self.price:.2f} purchase>"


class UpgradeChatOrder(object):
    """
    An order object from the UpgradeChat API.
    """

    def __init__(
            self, uuid:str, id:str, purchased_at:dt, user:UpgradeChatUser, subtotal:float, discount:float, total:float, type:str,
            is_subscription:bool, cancelled_at:dt, order_items:typing.List[UpgradeChatOrderItem], created:dt=None,
            updated:dt=None, deleted:dt=None, payment_processor:str=None, payment_processor_record_id:str=None):
        self.uuid = uuid
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
        extras["order_items"] = [UpgradeChatOrderItem(**i) for i in data.pop("order_items", list())]
        extras["purchased_at"] = dt.strptime(data.pop("purchased_at"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("cancelled_at"):
            extras["cancelled_at"] = dt.strptime(data.pop("cancelled_at"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("created"):
            extras["created"] = dt.strptime(data.pop("created"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("updated"):
            extras["updated"] = dt.strptime(data.pop("updated"), "%Y-%m-%dT%H:%M:%S.%fZ")
        if data.get("deleted"):
            extras["deleted"] = dt.strptime(data.pop("deleted"), "%Y-%m-%dT%H:%M:%S.%fZ")
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
