# wrapper.py
#
# Copyright 2023 Mirko Brombin
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import os
import shutil
import logging
import subprocess
import gettext

_ = gettext.gettext
logger = logging.getLogger("PrimeUtility:Wrapper")


class UnsupportedPrimeSetup(Exception):
    pass


class PrimeUtilityWrapper:
    def __init__(self):
        self.__binary = shutil.which("prime-switch")
        self.__available_profiles = ["nvidia", "integrated", "on-demand"]

    @staticmethod
    def can_transact() -> bool:
        return not os.path.exists("/tmp/ABSystem.Upgrade.lock")

    def is_supported(self) -> bool:
        if "prime" in os.environ.get("DISABLED_MODULES", []):
            logger.info(_("PRIME module disabled"))
            return False

        if self.__binary is None:
            logger.info(_("prime-select not found"))
            return False

        if not self.__is_laptop():
            logger.info(_("prime-select not supported for this device"))
            return False

        try:
            self.get_gpus()
        except UnsupportedPrimeSetup:
            logger.info(_("prime-select is not supported for this setup"))
            return False

        return True

    @staticmethod
    def available_profiles() -> list:
        return [
            {
                "id": "nvidia",
                "title": _("Discrete GPU"),
                "description": _("Use the discrete GPU for all applications."),
            },
            {
                "id": "integrated",
                "title": _("Integrated GPU"),
                "description": _("Use the integrated GPU for all applications."),
            },
            {
                "id": "on-demand",
                "title": _("On-demand"),
                "description": _(
                    "Use the integrated GPU for all applications, and the discrete GPU on demand."
                ),
            },
        ]

    def __is_laptop(self) -> bool:
        path = "/sys/devices/virtual/dmi/id/chassis_type"
        if not os.path.isfile(path):
            return False

        with open(path, "r") as f:
            if chassis_type := f.read():
                chassis_type = int(chassis_type.strip())
            else:
                return False

            if chassis_type in (8, 9, 10, 31):
                return True

        return False

    def get_current(self) -> str:
        return subprocess.check_output([self.__binary, "query"], text=True).strip()

    def get_set_profile_command(self, profile: str) -> str:
        if not self.can_transact():
            return None

        if profile not in self.__available_profiles:
            raise ValueError(_("Invalid profile name"))

        return " ".join(["pkexec", self.__binary, profile])

    def get_gpus(self) -> dict:
        gpus = {"integrated": "", "discrete": ""}
        found = {}

        res = subprocess.check_output(["lspci", "-k"], text=True)
        for line in res.splitlines():
            if ("VGA" in line or "3D" in line) and not "Non-VGA" in line:
                _gpu = line.split("controller:")[1].strip()
                if "intel" in _gpu.lower():
                    found["intel"] = _gpu
                elif "nvidia" in _gpu.lower():
                    found["nvidia"] = _gpu
                elif "amd" in _gpu.lower() or "ati" in _gpu.lower():
                    found["amd"] = _gpu

        if "intel" in found and "nvidia" in found:
            gpus[_("integrated")] = found["intel"]
            gpus[_("discrete")] = found["nvidia"]
        elif "intel" in found and "amd" in found:
            gpus[_("integrated")] = found["intel"]
            gpus[_("discrete")] = found["amd"]
        elif "nvidia" in found and "amd" in found:
            gpus[_("integrated")] = found["amd"]
            gpus[_("discrete")] = found["nvidia"]
        else:
            raise UnsupportedPrimeSetup

        return gpus
