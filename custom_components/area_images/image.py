"""
Blah blah
"""

import logging
import mimetypes
import os

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import area_registry
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import now

from . import DOMAIN, SIGNAL_UPDATE_AREA_IMAGE

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Add image entities for areas"""
    entities = []
    area_reg = area_registry.async_get(hass)

    for area in area_reg.areas:
        entities.extend([AreaImage(hass, area_reg.async_get_area(area))])

    async_add_entities(entities)


class AreaImage(ImageEntity):
    def __init__(self, hass: HomeAssistant, area: area_registry.AreaEntry) -> None:
        """Initialize Local File Camera component."""
        super().__init__(hass)
        self._area = area
        self._attr_image_last_updated = now()
        self._attr_name = area.name + " Area Image"
        self._attr_unique_id = f"{DOMAIN}--{self._attr_name}"
        self.hass = hass

        self._area_image_path = self.get_area_image()
        if self._area_image_path:
            self.check_file_path_access(self._area_image_path)
            self._attr_state = True
            # Set content type of local file
            content, _ = mimetypes.guess_type(self._area_image_path)
            if content is not None:
                self.content_type = content

    def get_area_image(self) -> str | None:
        if self._area.picture:
            return self.hass.config.config_dir + self._area.picture.replace(
                "api/", ""
            ).replace("serve/", "")

    def image(self) -> bytes | None:
        """Return image response."""
        if self._area_image_path:
            try:
                with open(self._area_image_path, "rb") as file:
                    return file.read()
            except FileNotFoundError:
                _LOGGER.warning(
                    "Could not read %s area image from file: %s",
                    self._area.name,
                    self._area_image_path,
                )
        return None

    def check_file_path_access(self, file_path):
        """Check that filepath given is readable."""
        if not os.access(file_path, os.R_OK):
            _LOGGER.warning(
                "Could not read %s area image from file: %s",
                self._area.name,
                file_path,
            )

    async def async_added_to_hass(self) -> None:
        """Call to update image."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, SIGNAL_UPDATE_AREA_IMAGE, self._update_callback
            )
        )

    @callback
    def _update_callback(self, *args) -> None:
        """Call update method."""
        if self._area.id in args:
            area_reg = area_registry.async_get(self.hass)
            self._area = area_reg.async_get_area(self._area.id)
            self._area_image_path = self.get_area_image()
            self._attr_image_last_updated = now()
            self.async_write_ha_state()
