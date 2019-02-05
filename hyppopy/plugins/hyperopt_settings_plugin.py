# -*- coding: utf-8 -*-
#
# DKFZ
#
#
# Copyright (c) German Cancer Research Center,
# Division of Medical and Biological Informatics.
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE.txt or http://www.mitk.org for details.
#
# Author: Sven Wanner (s.wanner@dkfz.de)

import os
import logging
import numpy as np
from hyppopy.globals import DEBUGLEVEL
LOG = logging.getLogger(os.path.basename(__file__))
LOG.setLevel(DEBUGLEVEL)

from pprint import pformat

try:
    from hyperopt import hp
    from yapsy.IPlugin import IPlugin
except:
    LOG.warning("hyperopt package not installed, will ignore this plugin!")
    print("hyperopt package not installed, will ignore this plugin!")

from hyppopy.settingspluginbase import SettingsPluginBase
from hyppopy.settingsparticle import SettingsParticle


class hyperopt_Settings(SettingsPluginBase, IPlugin):

    def __init__(self):
        SettingsPluginBase.__init__(self)
        LOG.debug("initialized")

    def convert_parameter(self, input_dict):
        LOG.debug(f"convert input parameter\n\n\t{pformat(input_dict)}\n")

        solution_space = {}
        for name, content in input_dict.items():
            particle = hyperopt_SettingsParticle(name=name)
            for key, value in content.items():
                if key == 'domain':
                    particle.domain = value
                elif key == 'data':
                    particle.data = value
                elif key == 'type':
                    particle.dtype = value
            solution_space[name] = particle.get()
        return solution_space


class hyperopt_SettingsParticle(SettingsParticle):

    def __init__(self, name=None, domain=None, dtype=None, data=None):
        SettingsParticle.__init__(self, name, domain, dtype, data)

    def convert(self):
        if self.domain == "uniform":
            if self.dtype == "float" or self.dtype == "double":
                return hp.uniform(self.name, self.data[0], self.data[1])
            elif self.dtype == "int":
                data = list(np.arange(int(self.data[0]), int(self.data[1]+1)))
                return hp.choice(self.name, data)
            else:
                msg = f"cannot convert the type {self.dtype} in domain {self.domain}"
                LOG.error(msg)
                raise LookupError(msg)
        elif self.domain == "loguniform":
            if self.dtype == "float" or self.dtype == "double":
                return hp.loguniform(self.name, self.data[0], self.data[1])
            else:
                msg = f"cannot convert the type {self.dtype} in domain {self.domain}"
                LOG.error(msg)
                raise LookupError(msg)
        elif self.domain == "normal":
            if self.dtype == "float" or self.dtype == "double":
                return hp.normal(self.name, self.data[0], self.data[1])
            else:
                msg = f"cannot convert the type {self.dtype} in domain {self.domain}"
                LOG.error(msg)
                raise LookupError(msg)
        elif self.domain == "categorical":
            if self.dtype == 'str':
                return hp.choice(self.name, self.data)
            elif self.dtype == 'bool':
                data = []
                for elem in self.data:
                    if elem == "true" or elem == "True" or elem == 1 or elem == "1":
                        data .append(True)
                    elif elem == "false" or elem == "False" or elem == 0 or elem == "0":
                        data .append(False)
                    else:
                        msg = f"cannot convert the type {self.dtype} in domain {self.domain}, unknown bool type value"
                        LOG.error(msg)
                        raise LookupError(msg)
                return hp.choice(self.name, data)
