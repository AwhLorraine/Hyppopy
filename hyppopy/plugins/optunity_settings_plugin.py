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
from hyppopy.globals import DEBUGLEVEL
LOG = logging.getLogger(os.path.basename(__file__))
LOG.setLevel(DEBUGLEVEL)

from pprint import pformat

try:
    import optunity
    from yapsy.IPlugin import IPlugin
except:
    LOG.warning("optunity package not installed, will ignore this plugin!")
    print("optunity package not installed, will ignore this plugin!")

from hyppopy.settingspluginbase import SettingsPluginBase


class optunity_Settings(SettingsPluginBase, IPlugin):

    def __init__(self):
        SettingsPluginBase.__init__(self)
        LOG.debug("initialized")

    def convert_parameter(self, input_dict):
        LOG.debug(f"convert input parameter\n\n\t{pformat(input_dict)}\n")

        # define function spliting input dict
        # into categorical and non-categorical
        def split_categorical(pdict):
            categorical = {}
            uniform = {}
            for name, pset in pdict.items():
                for key, value in pset.items():
                    if key == 'domain' and value == 'categorical':
                        categorical[name] = pset
                    elif key == 'domain':
                        uniform[name] = pset
            return categorical, uniform

        solution_space = {}
        # split input in categorical and non-categorical data
        cat, uni = split_categorical(input_dict)
        # build up dictionary keeping all non-categorical data
        uniforms = {}
        for key, value in uni.items():
            for key2, value2 in value.items():
                if key2 == 'data':
                    uniforms[key] = value2

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
        solution_space = tmp2
        return solution_space