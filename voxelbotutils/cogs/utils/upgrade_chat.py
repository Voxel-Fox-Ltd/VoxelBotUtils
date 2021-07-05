from datetime import datetime as dt, timedelta
import typing
from base64 import b64encode
import enum
import collections
import json

import aiohttp


class UpgradeChatInterval(enum.Enum):
    """
    A subscription interval enum for Upgrade.Chat role subscriptions.

    Attributes:
        day
        week
        month
        year
    """

    day = enum.auto()
    week = enum.auto()
    month = enum.auto()
    year = enum.auto()


class UpgradeChatItemType(enum.Enum):
    """
    An item type enum to allow you to query the Upgrade.Chat API.

    Attributes:
        UPGRADE
        SHOP
    """

    UPGRADE = enum.auto()
    SHOP = enum.auto()


class UpgradeChatProductType(enum.Enum):
    """
    A product type enum for internal responses from the Upgrade.Chat API - this is not for querying with.

    Attributes:
        DISCORD_ROLE
        SHOP_PRODUCT
    """

    DISCORD_ROLE = enum.auto()
    SHOP_PRODUCT = enum.auto()


class UpgradeChatPaymentProcessor(enum.Enum):
    """
    A payment processor enum for Upgrade.Chat purchases.

    Attributes:
        PAYPAL
        STRIPE
    """

    PAYPAL = enum.auto()
    STRIPE = enum.auto()


class UpgradeChatUser(object):
    """
    A user object from the UpgradeChat API.

    Attributes:
        discord_id (int): The ID of the user.
        username (str): The uername of the user.
    """

    def __init__(self, discord_id: str, username: str):
        self.discord_id: int = int(discord_id)
        self.username: str = username

    def __repr__(self):
        return self.username


class UpgradeChatProduct(object):
    """
    A product from the UpgradeChat API.

    Attributes:
        uuid (str): The UUID of the product.
        checkout_uri (str): The checkout link.
        name (str): The name of the product.
        account_id (int): The ID of the account that the product is attached to.
        price (float): The price of the product.
        interval (UpgradeChatInterval): How often the product is billed at.
        interval_count (int): How many times the product will be billed for.
        free_trial_length (int): The number of days that the product is free.
        description (str): The description for the product.
        image_link (str): The URL of the image that the product uses.
        variable_price (bool): Whether or not the price is variable.
        is_time_limited (bool): Whether or not the product is only available for a given amount of
            time.
        limited_inventory (bool): Whether or not the product has a limited inventory.
        available_stock (int): How many of the product is still available.
        shippable (bool): Whether or not the product is shippable.
        paymentless_trial (bool): Whether or not the trial period for this product is paymentless.
        product_types (typing.List[UpgradeChatProductType]): The types attached to this product.
        created (datetime.datetime): When this product was created.
        updated (datetime.datetime): When this product was updated.
        deleted (datetime.datetime, optional): When this product was deleted.
    """

    def __init__(
            self, uuid: str, checkout_uri: str, name: str, account_id: int,
            price: float, interval: UpgradeChatInterval, interval_count: int,
            free_trial_length: int, description: str, image_link: str, variable_price: bool,
            is_time_limited: bool, limited_inventory: bool,
            available_stock: int, shippable: bool, paymentless_trial: bool,
            product_types: typing.List[UpgradeChatProductType],
            created: dt, updated: dt, deleted: dt = None):
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

    Attributes:
        price (float): The price of the item.
        quantity (int): The amount of the item that was purchased.
        interval (UpgradeChatInterval): The interval that the item is billed at.
        interval_count (int): The number of times that the user will be billed.
        free_trial_length (int): The length of the free trial available with the item.
        is_time_limited (bool): Whether or not the item is time-limited.
        product (dict): The product payload.
        discord_roles (typing.List[dict]): A list of Discord roles that are attached to this order item.
        product_types (typing.List[UpgradeChatProductType]): A list of product types that this order item is.
        payment_processor (UpgradeChatPaymentProcessor): The payment processor used to purchase this item.
        payment_processor_record_id (str): The record ID that the payment processor used for this purchase.
    """

    def __init__(
            self, price: float, quantity: int, interval: UpgradeChatInterval,
            interval_count: int, free_trial_length: int, is_time_limited: bool,
            product: dict, discord_roles: typing.List[dict],
            product_types: typing.List[UpgradeChatProductType],
            payment_processor: UpgradeChatPaymentProcessor, payment_processor_record_id: str):
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

    Attributes:
        uuid (str): The UUID of the order
        id (str): The ID of the order.
        purchased_at (datetime.datetime): A timestamp of when the order was placed.
        user (UpgradeChatUser): The user who placed the order.
        subtotal (float): A subtotal of the items at checkout.
        discount (float): The discount applied to the items.
        total (float): The total that the user paid.
        type (UpgradeChatItemType): The type of item that was ordered.
        is_subscription (bool): Whether or not the order was a subscription.
        cancelled_at (datetime.datetime): The time when the order was cancelled
        order_items (typing.List[UpgradeChatOrderItem]): A list of items that were included in the order.
        created (datetime.datetime): When the order was created.
        updated (datetime.datetime): When the order was last updated.
        deleted (datetime.datetime, optional): When the order was deleted.
        payment_processor (UpgradeChatPaymentProcessor, optional): The payment processor for the order.
        payment_processor_record_id (str, optional): The record ID that the payment processor used.
        order_item_names (typing.List[str]): A list of item names that were ordered.
        order_item_uuids (typing.List[str]): A list of item UUIDs that were ordered.
    """

    def __init__(
            self, uuid: str, id: str, purchased_at: dt, user: UpgradeChatUser,
            subtotal: float, discount: float, total: float, type: UpgradeChatItemType,
            is_subscription: bool, cancelled_at: dt, order_items: typing.List[UpgradeChatOrderItem],
            created: dt, updated: dt, deleted: dt = None, payment_processor: UpgradeChatPaymentProcessor = None,
            payment_processor_record_id: str = None):
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
    A wrapper around the UpgradeChat v1 API.
    """

    BASE = "https://api.upgrade.chat/v1/{endpoint}"
    USER_REQUEST_CACHE = collections.defaultdict(lambda: (dt(2000, 1, 1), None,))

    def __init__(self, client_id: str, client_secret: str):
        """
        Args:
            client_id (str): A valid client ID from your account.
            client_secret (str): A valid client secret from your account.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self._basic_auth_token = b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        self._access_token = None

    async def get_access_token(self) -> str:
        """
        Get an access token from their Oauth endpoint.

        Returns:
            str: The aquired access token.
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

    async def get_orders(
            self, limit: int = 100, offset: int = 0, discord_id: int = None,
            type: typing.Union[UpgradeChatItemType, str] = None) -> typing.List[UpgradeChatOrder]:
        """
        Get a list of order objects that adhere to the request parameters given.

        Args:
            limit (int, optional): The number of responses to get.
            offset (int, optional): The offset that you want to get.
            discord_id (int, optional): The ID of the Discord user that you want to look up.
            type (typing.Union[UpgradeChatItemType, str], optional): The item type that you want to search for.

        Warning:
            This method does *not* raise an error when failing to get an access token or failing to access
            the Upgrade.Chat API - it will only return an empty list.

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
        if type:
            if isinstance(type, UpgradeChatItemType):
                type = type.name
            params.update({"type": type})

        # Serialise our request so we can cache a response
        key = json.dumps(params, sort_keys=True)
        cached, expiry = self.USER_REQUEST_CACHE[key]
        if expiry > dt.utcnow():
            return cached

        # And our headers
        try:
            access_token = await self.get_access_token()
        except Exception:
            return []  # We got an error response when getting an Oauth token - let's just return nothing here
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }

        # Send the web request
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE.format(endpoint="orders"), params=params, headers=headers) as r:
                try:
                    data = await r.json()
                except Exception:
                    return []

        # Deal with our response
        if data.get("data"):
            v = [UpgradeChatOrder.from_api(i) for i in data.get("data")]
        else:
            v = []
        self.USER_REQUEST_CACHE[key] = (v, dt.utcnow() + timedelta(minutes=2),)
        return v
