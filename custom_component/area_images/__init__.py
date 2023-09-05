"""Panel Nested component."""
from __future__ import annotations

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform

from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.area_registry import EVENT_AREA_REGISTRY_UPDATED
from homeassistant.helpers.dispatcher import dispatcher_send

DOMAIN = "area_images"
AREA_REGISTRY_UPDATE_EVENT = "area_registry_updated"
LISTENER = "event_listener"
PLATFORMS = [Platform.IMAGE]
SIGNAL_UPDATE_AREA_IMAGE = "area_images_update_signal"

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry) -> bool:
    """Set up the template integration."""

    @callback
    def area_registry_updated(_event: Event) -> None:
        """Notify image entities of update"""
        if _event.data.get("action") == "update":
            dispatcher_send(hass, SIGNAL_UPDATE_AREA_IMAGE, _event.data.get("area_id"))

    hass.data.setdefault(DOMAIN, {})

    listener = hass.bus.async_listen(EVENT_AREA_REGISTRY_UPDATED, area_registry_updated)

    # Store menu config data
    hass.data[DOMAIN][LISTENER] = listener
    await hass.config_entries.async_forward_entry_setups(config, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN][LISTENER]()
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
