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
from pprint import pformat
from hyppopy.globals import DEBUGLEVEL
LOG = logging.getLogger(os.path.basename(__file__))
LOG.setLevel(DEBUGLEVEL)

from yapsy.IPlugin import IPlugin


from hyppopy.helpers import sample_domain
from hyppopy.settingspluginbase import SettingsPluginBase
from hyppopy.settingsparticle import split_categorical
from hyppopy.settingsparticle import SettingsParticle


class gridsearch_Settings(SettingsPluginBase, IPlugin):

    def __init__(self):
        SettingsPluginBase.__init__(self)
        LOG.debug("initialized")

    def convert_parameter(self, input_dict):
        LOG.debug("convert input parameter\n\n\t{}\n".format(pformat(input_dict)))

        solution_space = {}
        # split input in categorical and non-categorical data
        cat, uni = split_categorical(input_dict)
        # build up dictionary keeping all non-categorical data
        uniforms = {}
        for name, content in uni.items():
            particle = gridsearch_SettingsParticle(name=name)
            for key, value in content.items():
                if key == 'domain':
                    particle.domain = value
                elif key == 'data':
                    particle.data = value
                elif key == 'type':
                    particle.dtype = value
            uniforms[name] = particle.get()

        # build nested categorical structure
        inner_level = uniforms
        for key, value in cat.items():
            tmp = {}
            tmp2 = {}
            for key2, value2 in value.items():
                if key2 == 'data':
                    for elem in value2:
                        tmp[elem] = inner_level
            tmp2[key] = tmp
            inner_level = tmp2
        if len(cat) > 0:
            solution_space = tmp2
        else:
            solution_space = inner_level
        return solution_space


class gridsearch_SettingsParticle(SettingsParticle):

    def __init__(self, name=None, domain=None, dtype=None, data=None):
        SettingsParticle.__init__(self, name, domain, dtype, data)

    def convert(self):
        assert isinstance(self.data, list), "Precondition Violation, invalid input type for data!"
        if self.domain == "categorical":
            return self.data
        else:
            assert len(self.data) >= 2, "Precondition Violation, invalid input data!"
            if len(self.data) < 3:
                self.data.append(10)
                LOG.warning("Grid sampling has set number of samples automatically to 10!")
                print("WARNING: Grid sampling has set number of samples automatically to 10!")

            samples = sample_domain(start=self.data[0], stop=self.data[1], count=self.data[2], ftype=self.domain)
            if self.dtype == "int":
                data = []
                for s in samples:
                    val = int(np.round(s))
                    if len(data) > 0:
                        if val == data[-1]: continue
                    data.append(val)
                return data
            return list(samples)
