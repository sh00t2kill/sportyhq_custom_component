"""SportyHQ custom integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
import logging
from aiohttp import ClientSession, CookieJar
from bs4 import BeautifulSoup

from .const import DOMAIN, SESSION_COOKIE_NAME
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SportyHQ from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    async def async_fetch_data():
        """Fetch data from SportyHQ."""
        my_stats_url = "https://www.sportyhq.com/my_stats"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

        # Use an unsafe cookie jar so the bare domain cookie is accepted
        jar = CookieJar(unsafe=True)
        async with ClientSession(cookie_jar=jar) as session:
            session.cookie_jar.update_cookies(
                {SESSION_COOKIE_NAME: entry.data["session_cookie"]},
                response_url=__import__("yarl").URL("https://www.sportyhq.com"),
            )

            async with session.get(my_stats_url, headers=headers, allow_redirects=True) as stats_response:
                final_url = str(stats_response.url)
                if "my_stats" not in final_url:
                    _LOGGER.error(
                        "SportyHQ: redirected to %s — session cookie is expired or invalid",
                        final_url,
                    )
                    return {}
                stats_page_content = await stats_response.text()

        soup = BeautifulSoup(stats_page_content, "html.parser")
        rating_group = soup.find("div", class_="card-group mb-4")

        data = {}
        if rating_group:
            cards = rating_group.find_all("div", class_="card")
            data = {
                "sportyhq_rating": cards[0].find("h6").text,
                "rating_confidence": cards[1].find("h6").text,
                "matches_ytd": cards[2].find("h6").text,
                "matches_all_time": cards[3].find("h6").text,
            }

        _LOGGER.debug("Fetched data from SportyHQ: %s", data)
        return data

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="sportyhq",
        update_method=async_fetch_data,
        update_interval=timedelta(minutes=60),  # Fix: Use timedelta from datetime
    )

    await coordinator.async_config_entry_first_refresh()

    # Log the initial data fetched by the coordinator
    _LOGGER.debug("Initial data from coordinator: %s", coordinator.data)

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])  # Fix: Use async_forward_entry_setups

    # Listen for updates to the config entry
    entry.async_on_unload(
        entry.add_update_listener(async_update_entry)
    )
    return True

async def async_update_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle updates to the config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
