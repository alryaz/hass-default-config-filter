import logging
import re
from typing import Any, Collection, Dict, Final, FrozenSet, Mapping, Optional

import voluptuous as vol
from homeassistant import data_entry_flow
from homeassistant.config_entries import ConfigEntry, ConfigEntryState, ConfigFlow, OptionsFlow
from homeassistant.core import callback
from homeassistant.helpers import config_validation

from custom_components.default_config_filter import DOMAIN

_LOGGER: Final = logging.getLogger(__name__)

CONF_DISABLED_DOMAINS: Final = "disabled_domains"
CONF_EXTRA_DOMAINS: Final = "extra_domains"
CONF_CONFIGURE_DOMAINS: Final = "configure_domains"

FMT_FAILED_DOMAINS: Final = "failed_domains"


class DefaultConfigFilterFlow(data_entry_flow.FlowHandler):
    def __init__(self) -> None:
        self.__base_dependencies_cache: Optional[FrozenSet[str]] = None

    async def async_get_base_dependencies(self) -> FrozenSet[str]:
        original_dependencies = self.__base_dependencies_cache

        if original_dependencies is None:
            from custom_components.default_config_filter import (
                async_get_original_manifest_contents,
                extract_manifest_dependencies,
            )

            original_manifest_contents = await async_get_original_manifest_contents(self.hass)
            original_dependencies = extract_manifest_dependencies(
                original_manifest_contents
            ).difference(
                ("config",)
            )  # remove 'config' from base dependencies to avoid locking user out

            self.__base_dependencies_cache = original_dependencies

        return original_dependencies

    def async_create_config_entry(self, options: Mapping[str, bool]) -> data_entry_flow.FlowResult:
        raise NotImplementedError

    @property
    def currently_disabled_domains(self) -> Collection[str]:
        return ()

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        errors = {}
        description_placeholders = {}
        if user_input:
            disabled_domains = set(user_input[CONF_DISABLED_DOMAINS])
            extra_domains = user_input.pop(CONF_EXTRA_DOMAINS, None)
            if extra_domains:
                domain_format_verification = {
                    domain: bool(re.fullmatch("[a-zA-Z0-9_]+", domain))
                    for domain in map(str.strip, extra_domains.split(","))
                }

                if all(domain_format_verification.values()):
                    disabled_domains.update(
                        filter(
                            domain_format_verification.__getitem__,
                            domain_format_verification.keys(),
                        )
                    )
                else:
                    errors[CONF_EXTRA_DOMAINS] = "invalid_format"
                    description_placeholders[FMT_FAILED_DOMAINS] = "failed_domains"

            if not errors:
                return self.async_create_config_entry(dict.fromkeys(disabled_domains, True))
        else:
            user_input = {}

        currently_disabled_domains = set(self.currently_disabled_domains).union(
            user_input.get(CONF_DISABLED_DOMAINS) or []
        )
        all_domains = sorted(
            (await self.async_get_base_dependencies()).union(currently_disabled_domains)
        )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_DISABLED_DOMAINS, default=list(currently_disabled_domains)
                    ): config_validation.multi_select(dict(zip(all_domains, all_domains))),
                    vol.Optional(
                        CONF_EXTRA_DOMAINS, default=user_input.get(CONF_EXTRA_DOMAINS, "")
                    ): config_validation.string,
                }
            ),
            errors=errors,
            description_placeholders=description_placeholders,
        )


class DefaultConfigFilterConfigFlow(DefaultConfigFilterFlow, ConfigFlow, domain=DOMAIN):
    def async_create_config_entry(self, options: Mapping[str, bool]) -> data_entry_flow.FlowResult:
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title="Default Config Override", data={}, options=options)

    async def async_step_import(self, user_input: Dict[str, Any]) -> data_entry_flow.FlowResult:
        await self.async_set_unique_id(DOMAIN)
        return self.async_create_config_entry(user_input)

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        return await super().async_step_user(user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> "DefaultConfigFilterOptionsFlow":
        return DefaultConfigFilterOptionsFlow(config_entry)


class DefaultConfigFilterOptionsFlow(DefaultConfigFilterFlow, OptionsFlow):
    def __init__(self, config_entry: ConfigEntry) -> None:
        super().__init__()
        self._config_entry = config_entry

    @property
    def currently_disabled_domains(self) -> Collection[str]:
        options = self._config_entry.options
        return tuple(filter(options.__getitem__, options.keys()))

    # noinspection PyUnusedLocal
    async def async_step_init(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> data_entry_flow.FlowResult:
        if self._config_entry.state in (ConfigEntryState.NOT_LOADED, ConfigEntryState.SETUP_ERROR):
            if user_input:
                if not user_input.get(CONF_CONFIGURE_DOMAINS):
                    from homeassistant.core import DOMAIN as HA_DOMAIN
                    from homeassistant.const import SERVICE_HOMEASSISTANT_RESTART

                    await self.hass.services.async_call(HA_DOMAIN, SERVICE_HOMEASSISTANT_RESTART)
                    return self.async_abort(reason="restart_pending")

            else:
                return self.async_show_form(
                    step_id="init",
                    data_schema=vol.Schema(
                        {
                            vol.Optional(
                                CONF_CONFIGURE_DOMAINS, default=False
                            ): config_validation.boolean
                        }
                    ),
                )

        return await self.async_step_user()

    def async_create_config_entry(self, options: Mapping[str, bool]) -> data_entry_flow.FlowResult:
        _LOGGER.debug(f"Will save options entry data: {options}")
        return self.async_create_entry(title="", data=options)
