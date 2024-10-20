################################################################################
#
#  Copyright 2014-2016 Eric Lacombe <eric.lacombe@security-labs.org>
#
################################################################################
#
#  This file is part of fuddly.
#
#  fuddly is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  fuddly is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with fuddly. If not, see <http://www.gnu.org/licenses/>
#
################################################################################


from fuddly.framework.comm_backends import Serial_Backend
from fuddly.framework.plumbing import *
from fuddly.framework.knowledge.information import *
from fuddly.framework.knowledge.feedback_handler import TestFbkHandler
from fuddly.framework.scenario import *
from fuddly.framework.global_resources import UI
from fuddly.framework.evolutionary_helpers import DefaultPopulation, CrossoverHelper
from fuddly.framework.data import DataProcess

project = Project()
project.default_dm = ['mydf', 'myproto']

project.map_targets_to_scenario('ex1', {0: 7, 1: 8, None: 8})

logger = Logger(record_data=False, explicit_data_recording=False,
                export_raw_data=False, enable_file_logging=False,
                highlight_marked_nodes=True)

### KNOWLEDGE ###

project.add_knowledge(
    Hardware.X86_64,
    Language.C,
    # Test.OnlyInvalidCases
)

project.register_feedback_handler(TestFbkHandler())

### PROJECT SCENARIOS DEFINITION ###

def cbk_print(env, step):
    print(env.user_context)
    print(env.user_context.prj)

open_step = Step('ex', do_before_sending=cbk_print)
open_step.connect_to(FinalStep())

sc_proj1 = Scenario('proj1', anchor=open_step, user_context=UI(prj='proj1'))
sc_proj2 = sc_proj1.clone('proj2')
sc_proj2.user_context = UI(prj='proj2')


step1 = Step(DataProcess(process=['tTYPE'], seed='4tg1'))
step2 = Step(DataProcess(process=['tTYPE#2'], seed='4tg2'))

step1.connect_to(step2, dp_completed_guard=True)
step2.connect_to(FinalStep(), dp_completed_guard=True)

sc_proj3 = Scenario('proj3', anchor=step1)

project.register_scenarios(sc_proj1, sc_proj2, sc_proj3)

### EVOLUTIONNARY PROCESS EXAMPLE ###

init_dp1 = DataProcess([('tTYPE', UI(fuzz_mag=0.2))], seed='exist_cond')
init_dp1.append_new_process([('tSTRUCT', UI(deep=True))])

init_dp2 = DataProcess([('tTYPE#2', UI(fuzz_mag=0.2))], seed='exist_cond')
init_dp2.append_new_process([('tSTRUCT#2', UI(deep=True))])

project.register_evolutionary_processes(
    ('evol1', DefaultPopulation,
     {'init_process': init_dp1,
      'max_size': 80,
      'max_generation_nb': 3,
      'crossover_algo': CrossoverHelper.crossover_algo1}),
    ('evol2', DefaultPopulation,
     {'init_process': init_dp2,
      'max_size': 80,
      'max_generation_nb': 3,
      'crossover_algo': CrossoverHelper.get_configured_crossover_algo2()})
)

### OPERATOR DEFINITION ###

@operator(project,
          args={'mode': ('strategy mode (0 or 1)', 0, int),
                'max_steps': ('maximum number of test cases', 10, int)})
class MyOp(Operator):

    def start(self, fmk_ops, dm, monitor, target, logger, user_input):
        monitor.set_probe_delay(P1, 1)
        monitor.set_probe_delay(P2, 0.2)
        if not monitor.is_probe_launched(P1) and self.mode == 0:
            monitor.start_probe(P1)
        if not monitor.is_probe_launched(P2) and self.mode == 0:
            monitor.start_probe(P2)

        self.cpt = 0
        self.detected_error = 0

        if self.mode == 1:
            fmk_ops.set_sending_delay(0)
        else:
            fmk_ops.set_sending_delay(0.5)

        return True

    def stop(self, fmk_ops, dm, monitor, target, logger):
        pass

    def plan_next_operation(self, fmk_ops, dm, monitor, target, logger, fmk_feedback):

        op = Operation()

        p1_ret = monitor.get_probe_status(P1).value
        p2_ret = monitor.get_probe_status(P2).value

        logger.print_console('*** status: p1: %d / p2: %d ***' % (p1_ret, p2_ret))

        if fmk_feedback.is_flag_set(FmkFeedback.NeedChange):
            change_list = fmk_feedback.get_flag_context(FmkFeedback.NeedChange)
            for dmaker, idx in change_list:
                logger.log_fmk_info('Exhausted data maker [#{:d}]: {:s} '
                                    '({:s})'.format(idx, dmaker['dmaker_type'],dmaker['dmaker_name']),
                                    nl_before=True, nl_after=False)
            op.set_flag(Operation.Stop)
            return op

        if p1_ret + p2_ret > 0:
            actions = [('SEPARATOR', UI(determinist=True)),
                       ('tSTRUCT', UI(deep=True)),
                       ('Cp', UI(idx=1)), ('Cp#1', UI(idx=3))]
        elif -5 < p1_ret + p2_ret <= 0:
            actions = ['SHAPE#specific', ('C#2', UI(path='.*prefix.$')), ('Cp#2', UI(idx=1))]
        else:
            actions = ['SHAPE#3', 'tTYPE#3']

        op.add_instruction(actions, tg_ids=[7,8])

        if self.mode == 1:
            actions_sup = ['SEPARATOR#2', ('tSTRUCT#2', UI(deep=True)), ('SIZE', UI(sz=10))]
            op.add_instruction(actions_sup)

        self.cpt += 1

        return op


    def do_after_all(self, fmk_ops, dm, monitor, target, logger):
        linst = LastInstruction()

        if not monitor.is_target_ok():
            self.detected_error += 1
            linst.set_instruction(LastInstruction.RecordData)
            linst.set_operator_feedback('This input has crashed the target!')
            linst.set_operator_status(0)
        if self.cpt > self.max_steps and self.detected_error < 9:
            linst.set_operator_feedback("We have less than 9 data that trigger some problem with the target!"
                                        " You win!")
            linst.set_operator_status(-8)
        elif self.cpt > self.max_steps:
            linst.set_operator_feedback("Too many errors! ... You loose!")
            linst.set_operator_status(-self.detected_error)

        return linst
