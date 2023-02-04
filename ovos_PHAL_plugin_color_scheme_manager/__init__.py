import os
import re
from os.path import join

from mycroft_bus_client.message import Message
from ovos_plugin_manager.phal import PHALPlugin
from ovos_utils import classproperty
from ovos_utils.log import LOG
from ovos_utils.network_utils import NetworkRequirements
from ovos_utils.xdg_utils import xdg_data_home, xdg_config_home


class ColorSchemeManager(PHALPlugin):

    def __init__(self, bus=None, config=None):
        super().__init__(bus=bus, name="ovos-PHAL-plugin-color-scheme-manager", config=config)
        self.theme_path = join(xdg_data_home(), "OVOS", "ColorSchemes")
        self.bus.on("ovos.shell.gui.color.scheme.generate", self.generate_theme)
        self.bus.on("ovos.theme.get", self.provide_theme)

        # Emit theme on init
        self.provide_theme(Message("ovos.theme.get"))

    @classproperty
    def network_requirements(self):
        """ developers should override this if they do not require connectivity
         some examples:
         IOT plugin that controls devices via LAN could return:
            scans_on_init = True
            NetworkRequirements(internet_before_load=False,
                                 network_before_load=scans_on_init,
                                 requires_internet=False,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=False)
         online search plugin with a local cache:
            has_cache = False
            NetworkRequirements(internet_before_load=not has_cache,
                                 network_before_load=not has_cache,
                                 requires_internet=True,
                                 requires_network=True,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
         a fully offline plugin:
            NetworkRequirements(internet_before_load=False,
                                 network_before_load=False,
                                 requires_internet=False,
                                 requires_network=False,
                                 no_internet_fallback=True,
                                 no_network_fallback=True)
        """
        return NetworkRequirements(internet_before_load=False,
                                   network_before_load=False,
                                   requires_internet=False,
                                   requires_network=False,
                                   no_internet_fallback=True,
                                   no_network_fallback=True)

    def generate_theme(self, message):
        if "primaryColor" not in message.data or "secondaryColor" not in message.data or "textColor" not in message.data:
            return

        if "theme_name" not in message.data:
            return

        theme_name = message.data["theme_name"]
        file_name = theme_name.replace(" ", "_").lower() + ".json"

        LOG.info(f"Creating ColorScheme For {theme_name}")

        if not os.path.exists(self.theme_path):
            os.makedirs(self.theme_path)

        if file_name in os.listdir(self.theme_path):
            os.remove(join(self.theme_path, file_name))

        theme_file = open(join(self.theme_path, file_name), "w")
        theme_file.write("{\n")
        theme_file.write('"name":"' + theme_name + '",\n')
        theme_file.write('"primaryColor":"' + message.data["primaryColor"] + '",\n')
        theme_file.write('"secondaryColor":"' + message.data["secondaryColor"] + '",\n')
        theme_file.write('"textColor":"' + message.data["textColor"] + '"\n')
        theme_file.write("}\n")
        theme_file.close()
        self.bus.emit(Message("ovos.shell.gui.color.scheme.generated",
                              {"theme_name": theme_name,
                               "theme_path": self.theme_path}))

    def provide_theme(self, message):
        file_name = "OvosTheme"
        xdg_system_path = "/etc/xdg"
        user_file = f"{xdg_config_home()}/{file_name}"
        system_file = f"{xdg_system_path}/{file_name}"
        if os.path.isfile(user_file):
            with open(user_file) as f:
                theme = f.read()
        elif os.path.isfile(system_file):
            with open(system_file) as f:
                theme = f.read()
        else:
            LOG.error("OvosTheme file not found")
            return

        try:
            name = re.search(r"name=(.*)", theme).group(1)
            primaryColor = re.search(r"primaryColor=(.*)", theme).group(1)
            secondaryColor = re.search(r"secondaryColor=(.*)", theme).group(1)
            textColor = re.search(r"textColor=(.*)", theme).group(1)

            self.bus.emit(message.response({"name": name,
                                            "primaryColor": primaryColor,
                                            "secondaryColor": secondaryColor,
                                            "textColor": textColor}))

        except Exception as e:
            LOG.error(e)
            return
