"""Services for Goodwe integration."""
from __future__ import annotations

from goodwe import OperationMode
import logging
import voluptuous as vol

from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry, entity_registry
from homeassistant.const import (
    EntityCategory,
    Platform,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)


from .const import (
    ATTR_DEVICE_ID,
    ATTR_ENTITY_ID,
    ATTR_PARAMETER,
    ATTR_VALUE,
    DOMAIN,
    KEY_DEVICE_INFO,
    KEY_INVERTER,
    SERVICE_GET_PARAMETER,
    SERVICE_SET_PARAMETER,
)

SERVICE_LOAD_BATTERY = "load_battery"
SERVICE_GENERAL_MODE = "general_mode"

_LOGGER = logging.getLogger(__name__)

SERVICE_GET_PARAMETER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): str,
        vol.Required(ATTR_PARAMETER): str,
        vol.Required(ATTR_ENTITY_ID): str,
    }
)

SERVICE_SET_PARAMETER_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): str,
        vol.Required(ATTR_PARAMETER): str,
        vol.Required(ATTR_VALUE): vol.Any(str, int, bool),
    }
)

SERVICE_OPERATION_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): str,
        vol.Required("power"): vol.Any(int),
        vol.Required("soc"): vol.Any(int),
    }
)

SERVICE_GENERAL_MODE_SCHEMA = vol.Schema(
    {
        vol.Required(ATTR_DEVICE_ID): str,
    }
)


async def async_setup_services(hass: HomeAssistant) -> None:
    """Set up services for Goodwe integration."""

    if hass.services.has_service(DOMAIN, SERVICE_GET_PARAMETER):
        return

    async def _get_inverter_by_device_id(hass: HomeAssistant, device_id: str):
        """Return a inverter instance given a device_id."""
        device = device_registry.async_get(hass).async_get(device_id)
        for entry_values in hass.data[DOMAIN].values():
            if device.identifiers == entry_values[KEY_DEVICE_INFO].get("identifiers"):
                return entry_values[KEY_INVERTER]
        raise ValueError(f"Inverter for device id {device_id} not found")

    async def async_get_parameter(call):
        """Service for setting inverter parameter."""
        device_id = call.data[ATTR_DEVICE_ID]
        parameter = call.data[ATTR_PARAMETER]
        entity_id = call.data[ATTR_ENTITY_ID]

        _LOGGER.debug("Reading inverter parameter '%s'", parameter)
        inverter = await _get_inverter_by_device_id(hass, device_id)
        value = await inverter.read_setting(parameter)

        entity = entity_registry.async_get(hass).async_get(entity_id)
        await hass.services.async_call(
            entity.domain,
            "set_value",
            {ATTR_ENTITY_ID: entity_id, ATTR_VALUE: value},
            blocking=True,
        )

    async def async_set_parameter(call):
        """Service for setting inverter parameter."""
        device_id = call.data[ATTR_DEVICE_ID]
        parameter = call.data[ATTR_PARAMETER]
        value = call.data[ATTR_VALUE]

        _LOGGER.info("Setting inverter parameter '%s' to '%s'", parameter, value)
        inverter = await _get_inverter_by_device_id(hass, device_id)
        await inverter.write_setting(parameter, value)
    
    async def async_load_battery(call):
        """Service for setting inverter parameter."""
        device_id = call.data[ATTR_DEVICE_ID]
        power = call.data["power"]
        soc = call.data["soc"]
        _LOGGER.info("Configure loading battery %s with power %s upto %s", device_id, power, soc)
        inverter = await _get_inverter_by_device_id(hass, device_id)
        await inverter.set_operation_mode(
                    OperationMode.ECO_CHARGE, int(power), int(soc)
                )
    
    async def async_to_general_mode(call):
        """Service for setting inverter parameter."""
        device_id = call.data[ATTR_DEVICE_ID]
        _LOGGER.info("Configure general mode")
        inverter = await _get_inverter_by_device_id(hass, device_id)
        await inverter.set_operation_mode(
                    OperationMode.GENERAL, 1, 1
                )

    hass.services.async_register(
        DOMAIN,
        SERVICE_LOAD_BATTERY,
        async_load_battery,
        schema=SERVICE_OPERATION_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERAL_MODE,
        async_to_general_mode,
        schema=SERVICE_GENERAL_MODE_SCHEMA,
    )

    hass.services.async_register(
        DOMAIN,
        SERVICE_GET_PARAMETER,
        async_get_parameter,
        schema=SERVICE_GET_PARAMETER_SCHEMA,
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_PARAMETER,
        async_set_parameter,
        schema=SERVICE_SET_PARAMETER_SCHEMA,
    )


async def async_unload_services(hass: HomeAssistant) -> None:
    """Unload services for Goodwe integration."""

    if hass.services.has_service(DOMAIN, SERVICE_GET_PARAMETER):
        hass.services.async_remove(DOMAIN, SERVICE_GET_PARAMETER)

    if hass.services.has_service(DOMAIN, SERVICE_SET_PARAMETER):
        hass.services.async_remove(DOMAIN, SERVICE_SET_PARAMETER)
    
    if hass.services.has_service(DOMAIN, SERVICE_LOAD_BATTERY):
        hass.services.async_remove(DOMAIN, SERVICE_LOAD_BATTERY)
