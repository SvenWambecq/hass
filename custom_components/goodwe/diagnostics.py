"""Diagnostics support for Goodwe."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from . import GoodweUpdateCoordinator
from .const import DOMAIN, KEY_DEVICE_INFO, KEY_INVERTER


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, config_entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    inverter = hass.data[DOMAIN][config_entry.entry_id][KEY_INVERTER]
    device_info = hass.data[DOMAIN][config_entry.entry_id][KEY_DEVICE_INFO]

    diagnostics_data = {
        "config_entry": config_entry.as_dict(),
        "inverter": {
            "model_name": inverter.model_name,
            "firmware": inverter.firmware,
            "arm_firmware": inverter.arm_firmware,
            "dsp1_version": inverter.dsp1_version,
            "dsp2_version": inverter.dsp2_version,
            "dsp_svn_version": inverter.dsp_svn_version,
            "arm_version": inverter.arm_version,
            "arm_svn_version": inverter.arm_svn_version,
        },
    }

    return diagnostics_data
