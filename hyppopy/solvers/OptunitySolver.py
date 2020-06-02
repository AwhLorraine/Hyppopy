# Hyppopy - A Hyper-Parameter Optimization Toolbox
#
# Copyright (c) German Cancer Research Center,
# Division of Medical Image Computing.
# All rights reserved.
#
# This software is distributed WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.
#
# See LICENSE

import os
import logging
import optunity
from pprint import pformat

from hyppopy.CandidateDescriptor import CandidateDescriptor, CandicateDescriptorWrapper
from hyppopy.globals import DEBUGLEVEL

LOG = logging.getLogger(os.path.basename(__file__))
LOG.setLevel(DEBUGLEVEL)

from hyppopy.solvers.HyppopySolver import HyppopySolver


class OptunitySolver(HyppopySolver):

    def __init__(self, project=None):
        """
        The constructor accepts a HyppopyProject.

        :param project: [HyppopyProject] project instance, default=None
        """
        HyppopySolver.__init__(self, project)

    def define_interface(self):
        """
        This function is called when HyppopySolver.__init__ function finished. Child classes need to define their
        individual parameter here by calling the _add_member function for each class member variable need to be defined.
        Using _add_hyperparameter_signature the structure of a hyperparameter the solver expects must be defined.
        Both, members and hyperparameter signatures are later get checked, before executing the solver, ensuring
        settings passed fullfill solver needs.
        """
        self._add_member("max_iterations", int)
        self._add_hyperparameter_signature(name="domain", dtype=str,
                                          options=["uniform", "categorical"])
        self._add_hyperparameter_signature(name="data", dtype=list)
        self._add_hyperparameter_signature(name="type", dtype=type)

    def loss_function_call(self, params):
        """
        This function is called within the function loss_function and encapsulates the actual blackbox function call
        in each iteration. The function loss_function takes care of the iteration driving and reporting, but each solver
        lib might need some special treatment between the parameter set selection and the calling of the actual blackbox
        function, e.g. parameter converting.

        :param params: [dict] hyperparameter space sample e.g. {'p1': 0.123, 'p2': 3.87, ...}

        :return: [float] loss
        """
        for key in params.keys():
            if self.project.get_typeof(key) is int:
                params[key] = int(round(params[key]))
        return self.blackbox(**params)

    def loss_function_batch(self, **candidates):
        """
        This function is called  with a list of candidates. This list is driven by the solver lib itself.
        The purpose of this function is to take care of the iteration reporting and the calling
        of the callback_func if available. As a developer you might want to overwrite this function (or the 'non-batch'-version completely (e.g.
        HyperoptSolver) but then you need to take care for iteration reporting for yourself. The alternative is to only
        implement loss_function_call (e.g. OptunitySolver).

        :param candidates: [list of CandidateDescriptors]

        :return: [dict] result e.g. {'loss': 0.5, 'book_time': ..., 'refresh_time': ...}
        """

        candidate_list = []

        keysValue = candidates.keys()
        temp = {}
        for key in keysValue:
            temp[key] = candidates[key].get()

        for i, pack in enumerate(zip(*temp.values())):
            candidate_list.append(CandidateDescriptor(**(dict(zip(keysValue, pack)))))

        result = super(OptunitySolver, self).loss_function_batch(candidate_list)
        self.best = self._trials.argmin

        return [x['loss'] for x in result.values()]

    def hyppopy_optunity_solver_pmap(self, f, seq):
        # Check if seq is empty. I so, return an empty result list.
        if len(seq) == 0:
            return []

        candidates = []
        for elem in seq:
            can = CandidateDescriptor(**elem)
            candidates.append(can)

        cand_list = CandicateDescriptorWrapper(keys=seq[0].keys())
        cand_list.set(candidates)

        f_result = f(cand_list)

        # If one candidate does not match the constraints, f() returns a single default value.
        # This is a problem as all the other candidates are not calculated either.
        # The following is a workaround. We split the candidate_list into 2 lists and call the map function recursively until all valid parameters are processed.
        if not isinstance(f_result, list):
            # First half
            seq_A = seq[:len(seq) // 2]
            temp_result_a = self.hyppopy_optunity_solver_pmap(f, seq_A)

            seq_B = seq[len(seq) // 2:]
            temp_result_b = self.hyppopy_optunity_solver_pmap(f, seq_B)
            # f_result = [42]

            f_result = temp_result_a + temp_result_b

        return f_result

    def execute_solver(self, searchspace):
        """
        This function is called immediately after convert_searchspace and get the output of the latter as input. It's
        purpose is to call the solver libs main optimization function.

        :param searchspace: converted hyperparameter space
        """
        LOG.debug("execute_solver using solution space:\n\n\t{}\n".format(pformat(searchspace)))
        try:
            optunity.minimize_structured(f=self.loss_function_batch,
                                         num_evals=self.max_iterations,
                                         search_space=searchspace,
                                         pmap=self.hyppopy_optunity_solver_pmap)
            print('bla')
        except Exception as e:
            LOG.error("internal error in optunity.minimize_structured occured. {}".format(e))
            raise BrokenPipeError("internal error in optunity.minimize_structured occured. {}".format(e))

    def split_categorical(self, pdict):
        """
        This function splits the incoming dict into two parts, categorical only entries and other.

        :param pdict: [dict] input parameter description dict

        :return: [dict],[dict] categorical only, others
        """
        categorical = {}
        uniform = {}
        for name, pset in pdict.items():
            for key, value in pset.items():
                if key == 'domain' and value == 'categorical':
                    categorical[name] = pset
                elif key == 'domain':
                    uniform[name] = pset
        return categorical, uniform

    def convert_searchspace(self, hyperparameter):
        """
        This function gets the unified hyppopy-like parameterspace description as input and, if necessary, should
        convert it into a solver lib specific format. The function is invoked when run is called and what it returns
        is passed as searchspace argument to the function execute_solver.

        :param hyperparameter: [dict] nested parameter description dict e.g. {'name': {'domain':'uniform', 'data':[0,1], 'type':'float'}, ...}

        :return: [object] converted hyperparameter space
        """
        LOG.debug("convert input parameter\n\n\t{}\n".format(pformat(hyperparameter)))
        # split input in categorical and non-categorical data
        cat, uni = self.split_categorical(hyperparameter)
        # build up dictionary keeping all non-categorical data
        uniforms = {}
        for key, value in uni.items():
            for key2, value2 in value.items():
                if key2 == 'data':
                    if len(value2) == 3:
                        uniforms[key] = value2[0:2]
                    elif len(value2) == 2:
                        uniforms[key] = value2
                    else:
                        raise AssertionError("precondition violation, optunity searchspace needs list with left and right range bounds!")

        if len(cat) == 0:
            return uniforms
        # build nested categorical structure
        inner_level = uniforms
        for key, value in cat.items():
            tmp = {}
            optunity_space = {}
            for key2, value2 in value.items():
                if key2 == 'data':
                    for elem in value2:
                        tmp[elem] = inner_level
            optunity_space[key] = tmp
            inner_level = optunity_space
        return optunity_space
