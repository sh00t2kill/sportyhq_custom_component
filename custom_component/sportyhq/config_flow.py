from homeassistant import config_entries
import voluptuous as vol

from .const import DOMAIN

class SportyHQConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for SportyHQ."""

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="SportyHQ", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("session_cookie"): str,
                }
            ),
        )

    async def async_step_import(self, user_input=None):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)

    async def async_step_reconfigure(self, user_input=None):
        """Handle reconfiguration of the integration."""
        config_entry = self.hass.config_entries.async_get_entry(
            self.context["entry_id"]
        )

        if user_input is not None:
            self.hass.config_entries.async_update_entry(
                config_entry, data={**config_entry.data, **user_input}
            )
            await self.hass.config_entries.async_reload(config_entry.entry_id)
            return self.async_abort(reason="reconfigure_successful")

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "session_cookie",
                        default=config_entry.data.get("session_cookie"),
                    ): str,
                }
            ),
        )

    @staticmethod
    def async_get_options_flow(config_entry):
        return SportyHQOptionsFlowHandler(config_entry)


class SportyHQOptionsFlowHandler(config_entries.OptionsFlowWithConfigEntry):
    """Handle options flow for SportyHQ."""

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        "session_cookie",
                        default=self.config_entry.data.get("session_cookie"),
                    ): str,
                }
            ),
        )
