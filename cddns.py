from logging import FileHandler, DEBUG, Formatter, getLogger
from requests import get
from cloudflare import Cloudflare
from time import sleep


def init_log() -> None:
    handler = FileHandler("cddns.log")
    format = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(format)
    logger = getLogger()
    logger.addHandler(handler)
    logger.setLevel(DEBUG)
    return logger


def get_current_ipv4() -> str:
    """Get current IPv4."""
    try:
        import settings

        ipv4_endpoint = settings.IPv4_ENDPOINT
    except:
        ipv4_endpoint = "https://api.ipify.org?format=json"
    try:
        response = get(ipv4_endpoint)
        if response.status_code != 200:
            raise Exception("Error to get IPv4.")
        return response.json()["ip"]
    except:
        raise Exception("Error to get IPv4.")


def main():
    logger = init_log()
    try:
        cloudflare = Cloudflare()
    except Exception as exc:
        logger.error(exc)
        exit(1)
    error_count = 0
    while True:
        try:
            current_ipv4 = get_current_ipv4()
            logger.info(f"Current IPv4: {current_ipv4}")
            cloudflare.update_dns(current_ipv4)
            logger.info("Sleeping for 5 minutes...")
            sleep(300)
        except Exception as exc:
            logger.error(exc)
            error_count += 1
            if error_count >= 10:
                logger.error("Too many errors. Exiting...")
                exit(1)
            logger.info("Sleeping for 1 minute...")
            sleep(60)
        except KeyboardInterrupt:
            logger.info("Exiting...")
            exit(0)
    else:
        # Reset error count
        error_count = 0


if __name__ == "__main__":
    main()
