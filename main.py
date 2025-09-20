from cloudflare import Cloudflare
from tldextract import extract

import threading
import argparse
import requests
import logging
import os

DNS_RECORD = os.getenv("CLOUDFLARE_DNS_RECORD")
ZONE = extract(DNS_RECORD).top_domain_under_public_suffix

class CloudflareDDNS:
    def __init__(self, autostart: bool = False, timer: int = 1800, debug: bool = False) -> None:
        self._timer = timer
        self._debug = debug
        self._setupLogging()

        self._logger.debug(f"Using DNS record {DNS_RECORD} in zone {ZONE}")
        self._logger.debug(f"Logging in with Cloudflare..")

        self._previousIP = "restart"
        self._cloudflare = Cloudflare(
            api_token=os.getenv("CLOUDFLARE_API_TOKEN")
        )

        self._collectRecords()

        if autostart:
            self.start()

    def _setupLogging(self) -> None:
        handlers = [logging.StreamHandler()]

        logging.basicConfig(
            level=logging.DEBUG if self._debug else logging.INFO,
            format='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=handlers
        )

        self._logger = logging.getLogger(__name__)

    def _collectRecords(self) -> None:
        # collect the zone id first
        zones = self._cloudflare.zones.list(
            name=ZONE
        )

        if len(zones.result) < 1:
            raise ValueError(f"No zones found for zone {ZONE}")
        
        self._zone = zones.result[0]

        # find the relevant dns record within that zone
        records = self._cloudflare.dns.records.list(
            zone_id=self._zone.id,
            name=DNS_RECORD
        )

        if len(records.result) < 1:
            raise ValueError(f"No records found for record {DNS_RECORD} - does it exist?")
        
        self._record = records.result[0]

    def _retrievePublicIPV4(self) -> str:
        response = requests.get("https://api.ipify.org")
        response.raise_for_status()
        return response.text
    
    def _makeComment(self, ip: str) -> str:
        comment = f"Initial DDNS update to {ip}" if self._previousIP == "restart" else f"DDNS update from {self._previousIP} to {ip}"
        self._logger.debug(f"Generated comment: {comment}")
        return comment

    def _tick(self):
        currentIP = self._retrievePublicIPV4()
        self._logger.debug(f"Retrieved current public IP: {currentIP}")

        if currentIP == self._previousIP:
            return
        
        self._logger.info(f"IP changed from {self._previousIP} to {currentIP}, updating DNS record")

        comment = self._makeComment(currentIP)
        result = self._cloudflare.dns.records.edit(
            # required parameters
            zone_id=self._zone.id,
            dns_record_id=self._record.id,
            name=DNS_RECORD,
            ttl=1,
            type="A",

            # optional parameters
            comment=comment,
            content=currentIP
        )

        self._previousIP = currentIP
        self._logger.info(f"Updated DNS record {DNS_RECORD} to {result.content} with comment '{result.comment}'")
        self._logger.debug(f"Set previous IP to {self._previousIP}")
        self._logger.debug(result)

    def start(self):
        if hasattr(self, "_thread") and self._thread.is_alive():
            self._logger.warning("DDNS service is already running")
            return
        
        self._logger.info("Starting DDNS service")

        self._running = True

        def loop():
            while self._running:
                self._logger.debug("Running DDNS update tick")

                try:
                    self._tick()
                except Exception as e:
                    self._logger.error(f"Error during DDNS update: {e}")

                threading.Event().wait(self._timer)

        self._thread = threading.Thread(target=loop, daemon=False)
        self._logger.info("DDNS service started")
        self._thread.start()

    def stop(self):
        if not hasattr(self, "_thread") or not self._thread.is_alive():
            self._logger.warning("DDNS service is not running")
            return

        self._logger.info("Stopping DDNS service")
        self._running = False

        if hasattr(self, "_thread"):
            self._thread.join()

        self._logger.info("DDNS service stopped")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloudflare DDNS Updater")

    parser.add_argument("--autostart", action="store_true", help="Start the updater automatically")
    parser.add_argument("--timer", type=int, default=1800, help="Update interval in seconds")
    parser.add_argument("--debug", type=bool, default=False, help="Enable debug logging")

    args = parser.parse_args()

    CloudflareDDNS(
        autostart=args.autostart,
        timer=args.timer,
        debug=args.debug
    )
