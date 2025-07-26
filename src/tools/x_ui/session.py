import secrets

import orjson
from loguru import logger

from core.env import env
from core.types import (
    StringifiedUUID,
    TelegramUserId,
    UnixTimeStampInMilliseconds,
)
from tools.http import AiohttpClient

from .settings import XUISettings


class XUISession:
    def __init__(self, http_client: AiohttpClient) -> None:
        self.__http_client = http_client

        self._inbound_id = env.X_UI_INBOUND_ID

        self._public_key = None
        self._short_id = None
        self._fingerprint = None
        self._sni = None

    async def async_init(self) -> None:
        url = env.X_UI_API_URL + f'/get/{self._inbound_id}'
        response = await self.request_json(url=url)
        stream_settings = orjson.loads(response['obj']['streamSettings'])
        reality_settings = stream_settings['realitySettings']

        public_key = reality_settings['settings']['publicKey']
        short_id = reality_settings['shortIds'][0]
        fingerprint = reality_settings['settings']['fingerprint']
        sni = reality_settings['serverNames'][0]

        self._public_key = public_key
        self._short_id = short_id
        self._fingerprint = fingerprint
        self._sni = sni

    async def _authorize(self) -> bool:
        response = await self.__http_client.request_json(
            url=env.X_UI_LOGIN_URL,
            method='POST',
            data={
                'username': env.X_UI_USERNAME,
                'password': env.X_UI_PASSWORD,
            },
        )
        if response and response['success']:
            return True
        else:
            logger.critical(
                f'Problem with authorization. Response: {response}'
            )
            return False

    async def request_json(
        self, url: str, method: str = 'GET', data: dict | None = None
    ) -> dict:
        cookies = self.__http_client._session.cookie_jar.filter_cookies(
            request_url=env.X_UI_DOMAIN_BASE_URL
        )
        if not cookies:
            await self._authorize()

        response = await self.__http_client.request_json(
            url=url, method=method, data=data
        )
        if response and response['success']:
            return response
        else:
            logger.critical(
                'Error while processing response.json()\n\n'
                f'URL: {method} {url}\n'
                f'data: {data}\n\n'
                f'Response: {response}\n'
                f'Message: {response["msg"] if response else None}'
            )
            return {}

    async def get_all_online_clients(self) -> set[str]:
        url = env.X_UI_API_URL + '/onlines'
        response = await self.request_json(url=url, method='POST')
        online_clients = response['obj']
        if online_clients is None:
            return set()
        return set(online_clients)

    async def get_client_ip_addresses(self, email: str) -> list[str]:
        url = env.X_UI_API_URL + f'/clientIps/{email}'
        response = await self.request_json(url=url, method='POST')
        if response['obj'] == 'No IP Record':
            return []
        client_ips: list[str] = orjson.loads(response['obj'])
        if not isinstance(client_ips, list):
            return []
        return client_ips

    async def clear_client_ip_addresses(self, email: str) -> bool:
        url = env.X_UI_API_URL + f'/clearClientIps/{email}'
        response = await self.request_json(url=url, method='POST')
        return True if response else False

    async def get_all_subscriptions(self) -> list[XUISettings]:
        url = env.X_UI_API_URL + f'/get/{self._inbound_id}'
        response = await self.request_json(url=url)
        all_subscriptions = orjson.loads(response['obj']['settings'])
        return [
            XUISettings(**subscription)
            for subscription in all_subscriptions['clients']
        ]

    async def user_has_subscriptions(
        self, telegram_user_id: TelegramUserId
    ) -> bool:
        all_subscriptions = await self.get_all_subscriptions()
        all_emails = {email.email for email in all_subscriptions}
        return any(
            email.startswith(f'{telegram_user_id}-') for email in all_emails
        )

    async def get_all_users_telegram_ids(self) -> set[TelegramUserId]:
        telegram_users_ids = set()
        all_users = await self.get_all_subscriptions()
        for user in all_users:
            telegram_user_id = user.email.split('-')[0]
            telegram_users_ids.add(telegram_user_id)
        return telegram_users_ids

    async def get_user_subscriptions_by_telegram_id(
        self, telegram_user_id: TelegramUserId
    ) -> list[XUISettings]:
        list_of_user_subscriptions = []
        all_clients = await self.get_all_subscriptions()
        for client in all_clients:
            if client.email.startswith(f'{telegram_user_id}-'):
                list_of_user_subscriptions.append(client)
        return list_of_user_subscriptions

    async def add_new_subscription(
        self,
        telegram_user_id: TelegramUserId,
        subscription_uuid: StringifiedUUID,
        subscription_name: str,
        subscription_expiration: UnixTimeStampInMilliseconds,
    ) -> bool:
        new_client_email = f'{telegram_user_id}-{subscription_name}'
        new_client_subscription_id = secrets.token_hex(8).lower()
        new_client_settings = XUISettings(
            id=subscription_uuid,
            email=new_client_email,
            expiryTime=subscription_expiration,
            subId=new_client_subscription_id,
        )
        response = await self.request_json(
            url=env.X_UI_API_URL + '/addClient',
            method='POST',
            data={
                'id': self._inbound_id,
                'settings': str(new_client_settings),
            },
        )
        if response and response['success']:
            logger.success('Client added successfully.')
            return True
        else:
            logger.error(f'Client added unsuccessfully! Response: {response}')
            return False

    async def get_client_settings_by_uuid(
        self, client_uuid: StringifiedUUID
    ) -> XUISettings | None:
        all_subscriptions = await self.get_all_subscriptions()
        for subscription in all_subscriptions:
            if subscription.id == client_uuid:
                return subscription

    async def get_client_settings_by_email(
        self, email: str
    ) -> XUISettings | None:
        all_subscriptions = await self.get_all_subscriptions()
        for subscription in all_subscriptions:
            if subscription.email == email:
                return subscription

    async def _update_client(
        self,
        client_uuid: StringifiedUUID,
        settings: XUISettings,
        subscription_expiration: UnixTimeStampInMilliseconds | None = None,
        subscription_name: str | None = None,
        subscription_comment: str | None = None,
    ) -> bool:
        if subscription_expiration:
            settings.expiryTime = subscription_expiration
        if subscription_name:
            settings.email = (
                settings.email.split('-')[0] + f'-{subscription_name}'
            )
        if subscription_comment:
            settings.comment += f'{subscription_comment}, '

        response = await self.request_json(
            url=env.X_UI_API_URL + f'/updateClient/{client_uuid}',
            method='POST',
            data={'id': self._inbound_id, 'settings': str(settings)},
        )
        if response:
            logger.success(f'Client "{client_uuid}" updated successfully.')
            return True
        else:
            logger.critical(
                f'Error while updating client "{client_uuid}". Client settings:\n\n{settings}'
            )
            return False

    async def toggle_subscription_by_uuid(
        self, client_uuid: StringifiedUUID, enable: bool
    ) -> bool:
        current_settings = await self.get_client_settings_by_uuid(
            client_uuid=client_uuid
        )
        current_settings.enable = enable
        logger.info(
            f'Subscription was toggled. Current status of subscription: {enable:}'
        )
        return await self._update_client(
            client_uuid=client_uuid, settings=current_settings
        )

    async def update_client_by_uuid(
        self,
        client_uuid: StringifiedUUID,
        subscription_expiration: UnixTimeStampInMilliseconds | None = None,
        subscription_name: str | None = None,
        subscription_comment: str | None = None,
    ) -> bool:
        current_settings = await self.get_client_settings_by_uuid(
            client_uuid=client_uuid
        )
        return await self._update_client(
            client_uuid=client_uuid,
            settings=current_settings,
            subscription_expiration=subscription_expiration,
            subscription_name=subscription_name,
            subscription_comment=subscription_comment,
        )

    async def update_client_by_email(
        self,
        email: str,
        subscription_expiration: UnixTimeStampInMilliseconds | None = None,
        subscription_name: str | None = None,
        subscription_comment: str | None = None,
    ) -> bool:
        current_settings = await self.get_client_settings_by_email(email=email)
        return await self._update_client(
            client_uuid=current_settings.id,
            settings=current_settings,
            subscription_expiration=subscription_expiration,
            subscription_name=subscription_name,
            subscription_comment=subscription_comment,
        )
