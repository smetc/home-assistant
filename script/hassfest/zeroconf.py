"""Generate zeroconf file."""
from collections import OrderedDict
import json
from typing import Dict

from .model import Integration, Config

BASE = """
\"\"\"Automatically generated by hassfest.

To update, run python3 -m hassfest
\"\"\"


SERVICE_TYPES = {}
""".strip()


def generate_and_validate(integrations: Dict[str, Integration]):
    """Validate and generate zeroconf data."""
    service_type_dict = {}

    for domain in sorted(integrations):
        integration = integrations[domain]

        if not integration.manifest:
            continue

        service_types = integration.manifest.get('zeroconf')

        if not service_types:
            continue

        try:
            with open(str(integration.path / "config_flow.py")) as fp:
                if ' async_step_zeroconf(' not in fp.read():
                    integration.add_error(
                        'zeroconf', 'Config flow has no async_step_zeroconf')
                    continue
        except FileNotFoundError:
            integration.add_error(
                'zeroconf',
                'Zeroconf info in a manifest requires a config flow to exist'
            )
            continue

        for service_type in service_types:

            if service_type not in service_type_dict:
                service_type_dict[service_type] = []

            service_type_dict[service_type].append(domain)

    data = OrderedDict((key, service_type_dict[key])
                       for key in sorted(service_type_dict))

    return BASE.format(json.dumps(data, indent=4))


def validate(integrations: Dict[str, Integration], config: Config):
    """Validate zeroconf file."""
    zeroconf_path = config.root / 'homeassistant/generated/zeroconf.py'
    config.cache['zeroconf'] = content = generate_and_validate(integrations)

    with open(str(zeroconf_path), 'r') as fp:
        current = fp.read().strip()
        if current != content:
            config.add_error(
                "zeroconf",
                "File zeroconf.py is not up to date. "
                "Run python3 -m script.hassfest",
                fixable=True
            )
        return


def generate(integrations: Dict[str, Integration], config: Config):
    """Generate zeroconf file."""
    zeroconf_path = config.root / 'homeassistant/generated/zeroconf.py'
    with open(str(zeroconf_path), 'w') as fp:
        fp.write(config.cache['zeroconf'] + '\n')
