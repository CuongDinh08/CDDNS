from logging import getLogger
from requests import get, post, put, patch
import json

try:
    import settings
except:
    raise Exception("Missing setting file.")

logger = getLogger()


class Cloudflare:
    def _request(self, method: str, endpoint: str, data: dict = None):
        url = "https://api.cloudflare.com/client/v4" + endpoint
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }
        if method.lower() == "get":
            return get(url=url, params=data, headers=headers)
        elif method.lower() == "post":
            return post(url=url, json=data, headers=headers)
        elif method.lower() == "put":
            return put(url=url, json=data, headers=headers)
        elif method.lower() == "patch":
            return patch(url=url, json=data, headers=headers)
        else:
            raise Exception("Invalid method.")

    def ping(self):
        """Test Clouflare token and zone ID."""
        logger.info("Testing Cloudflare connection...")
        response = self._request("get", f"/zones/{self._zone_id}/dns_records")
        if response.status_code != 200:
            logger.error(response.json())
            raise Exception("Error to connect to Cloudflare. Read log for more info.")
        return response

    def __init__(self) -> None:
        """Validate Cloudflare settings"""
        self._settings = settings

        try:
            self._token: str = getattr(settings, "CLOUDFLARE_TOKEN")
        except:
            raise Exception("Missing CLOUDFLARE_TOKEN in settings.")

        try:
            self._zone_id: str = getattr(settings, "CLOUDFLARE_ZONE_ID")
        except:
            raise Exception("Missing CLOUDFLARE_ZONE_ID in settings.")

        try:
            self._dns_names: list = getattr(settings, "CLOUDFLARE_DNS_NAMES")
        except:
            raise Exception("Missing CLOUDFLARE_DNS_NAMES in settings.")

        self.validate(self.ping().json())

    def validate(self, list_dns_records: dict) -> None:
        """Validate DNS names and save current data."""
        try:
            result = list_dns_records.get("result")
        except:
            raise Exception("Invalid response from Cloudflare.")
        for each_dns_name in self._dns_names:
            if each_dns_name not in [each["name"] for each in result]:
                raise Exception(f"DNS name {each_dns_name} not found in Cloudflare.")
        self._current_data = result
        logger.info("Cloudflare settings validated.")

    def update_dns(self, current_ipv4: str) -> None:
        # print(json.dumps(self._current_data, indent=4))
        for each_cloudflare_dns in self._current_data:
            if (
                each_cloudflare_dns["name"] not in self._dns_names
                or each_cloudflare_dns["type"] != "A"
            ):
                continue
            if each_cloudflare_dns["content"] != current_ipv4:
                logger.info(f"Updating {each_cloudflare_dns['name']}...")
                response = self._request(
                    "put",
                    f"/zones/{self._zone_id}/dns_records/{each_cloudflare_dns['id']}",
                    {
                        "content": current_ipv4,
                        "name": each_cloudflare_dns["name"],
                        "type": "A",
                    },
                )
                if response.status_code != 200:
                    logger.error(response.json())
                    raise Exception("Error to update DNS record.")
                each_cloudflare_dns["content"] = current_ipv4
                logger.info(f"DNS record {each_cloudflare_dns['name']} updated.")
            else:
                logger.info(f"{each_cloudflare_dns['name']} is up to date.")
        logger.info("All DNS records updated.")
