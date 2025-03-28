"""SportyHQ custom integration."""
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from datetime import timedelta
import asyncio
import logging
from aiohttp import ClientSession
from bs4 import BeautifulSoup
from http.cookies import SimpleCookie

DOMAIN = "sportyhq"
_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up SportyHQ from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    async def async_fetch_data():
        """Fetch data from SportyHQ."""
        base_url = "https://www.sportyhq.com/login"
        login_url = "https://www.sportyhq.com/authentication/login"
        my_stats_url = "https://www.sportyhq.com/my_stats"

        user_agent_header = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
        }

        async with ClientSession() as session:
            # Fetch CSRF token
            async with session.get(base_url, headers=user_agent_header) as login_response:
                raw_cookies = login_response.headers.get("Set-Cookie", "")
                cookie = SimpleCookie(raw_cookies)
                csrf_token = cookie.get("sportyhq_cookie_v6sportyhq_csrf_cookie").value if cookie.get("sportyhq_cookie_v6sportyhq_csrf_cookie") else None
                _LOGGER.debug("CSRF token: %s", csrf_token)

            # Login
            login_data = {
                "sportyhq_csrf_token": csrf_token,
                "email": entry.data["email"],
                "password": entry.data["password"],
                "remember_me": "yes",
            }
            _LOGGER.debug("Login data: %s", login_data)
            async with session.post(login_url, data=login_data, headers=user_agent_header) as login_post_response:
                if login_post_response.status != 200:
                    _LOGGER.error("Failed to log in to SportyHQ")
                    return {}

            # Fetch stats
            async with session.get(my_stats_url, headers=user_agent_header) as stats_response:
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
