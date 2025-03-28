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
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                }
            ),
        )

    async def async_step_import(self, user_input=None):
        """Handle import from configuration.yaml."""
        return await self.async_step_user(user_input)

    @staticmethod
    def async_get_options_flow(config_entry):
        return SportyHQOptionsFlowHandler(config_entry)


class SportyHQOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for SportyHQ."""

    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("email", default=self.config_entry.data.get("email")): str,
                    vol.Required("password", default=self.config_entry.data.get("password")): str,
                }
            ),
        )
