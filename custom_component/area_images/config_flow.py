"""
Config Flow for Area Images.
@msp1974
"""
from __future__ import annotations

import logging

from homeassistant import config_entries
from . import DOMAIN

_LOGGER = logging.getLogger(__name__)


class AreaImagesFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle a config flow start."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is None:
            return self.async_show_form(step_id="user")
        return self.async_create_entry(title="Area Images", data={})
