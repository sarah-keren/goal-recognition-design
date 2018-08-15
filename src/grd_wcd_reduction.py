__author__ = 'sarah'


import grd_defs,grd_utils,grd_task, grd_evaluator, grd_planning_gen
from pddl import parser,pddl #imports from pypaerplan_s
import os, copy, time




def reduce_wcd(cur_grd_task, design_budget_array, calc_method, optimal_costs, actions_to_remove = grd_defs.NA, log_stream=None, exec_time_limit = grd_defs.DEFAULT_TIME_LIMIT, Exhaustive = False, add_action_constraints = False, use_closed_list = grd_defs.USE_CLOSED_LIST):


    '''
    find the optimal action set to be removed - by examining the removal of all possible subset of grounded actions of size budget and lower
    optimization : removing all action sequences that have a wcd of 0 or -1 from further exploration
                   also - the only operations that are considered are on optimal paths

    @param domain_file_name,template_file_name,hyps_file_name
    @param destination_folder  - the folder in which the solution files will be generated
    @return:
    '''

    progress_log_file = open('Progress_log_file.txt','a')

    progress_log_file.write('\n1')

    print('-- > design_budget_array is')

    design_budget_array_string = '[='
    for budget in design_budget_array:
        print(budget)
        design_budget_array_string += '%d,'%budget

    design_budget_array_string += '=]'



    cur_time_remaining = exec_time_limit
    init_time = time.time()
    cur_exec_time = init_time

    extended_domain_file_name = get_reduce_domain_file_name(actions_to_remove,cur_grd_task,add_action_constraints)


    # keeps a closed list of operations combinations - making sure the same combination is not reexamined
    # is used only if use_closed_list is True
    op_combs_closed = []
    timeout = False
    zero_wcd_reached = False
    total_num_of_states_explored = 0
    total_num_of_nodes_explored = 0

    resFindInitWcd = grd_defs.DEFAULT_MAX_VAL
    init_wcd = grd_defs.DEFAULT_MAX_VAL
    init_wcd_optimal_costs = []
    init_wcd_optimal_plans = []
    init_wcd_hyps = []

    # init with empty op comb
    opt_op_comb = modification_combination(None,None, None, None)
    wcd_calc_time = 0

    #operations of newly found paths
    new_op_combs = []
    explored_op_comb = 0
    min_wcd = grd_defs.DEFAULT_MAX_VAL

    # keeping track of the redution achieved per budget
    reduction_per_budget_exhausted = {}

    progress_log_file.write('4')
    try:

        progress_log_file.write('5')

        #perform a wcd search to get the optimal plan with the wcd
        resFindInitWcd = grd_evaluator.calc_wcd_multiple_hyps(calc_method, cur_grd_task, cur_time_remaining, log_stream, optimal_costs)
        wcd_calc_time = time.time()- init_time

        #initialize values
        init_wcd = resFindInitWcd.wcd_value
        init_wcd_optimal_costs = resFindInitWcd.optimal_plans_costs
        init_wcd_optimal_plans = resFindInitWcd.optimal_plans
        init_wcd_hyps = resFindInitWcd.hyps_pair

        #keep current minimal wcd and measures
        min_wcd = init_wcd
        if min_wcd <  0:
            print('init wcd is invalid: %d'%init_wcd)
        if min_wcd == 0:
            zero_wcd_reached = True


        total_num_of_states_explored += resFindInitWcd.size_of_search_space
        total_num_of_nodes_explored += resFindInitWcd.expanded_nodes

        #log
        print('init wcd: %d for hyps %s '%(init_wcd,init_wcd_hyps))
        print('init wcd optimal_plans_costs %s'%init_wcd_optimal_costs)

        #check that all hyps are accessible
        bInaccessible = False
        for cost in optimal_costs:
            if cost < 0 :
                print("bInaccessible = True")
                return


        #add the solution to the list of paths to be explored - this is the current wcd path
        op_path = grd_utils.get_paths(init_wcd_optimal_plans, init_wcd, calc_method)

        # get all operator combinations for the first level
        empty_obs_comb = modification_combination(None,None, None,None)
        if use_closed_list:
            op_combs_closed.append(empty_obs_comb)
        op_combs = get_next_ops_combs(cur_grd_task, op_path, design_budget_array, calc_method, empty_obs_comb, op_combs_closed, Exhaustive, log_stream)

        #iterate while there are combinations to explore and the budget has not been reached
        while len(op_combs) > 0 and not timeout and not zero_wcd_reached:

            # get the current combination to explore
            op_comb = op_combs.pop(0)

            # keep an account of reduction achieved per budget
            track_design(op_comb,reduction_per_budget_exhausted,min_wcd,progress_log_file)


            print('---- > exploring op_comb: %s'%op_comb.getString())
            progress_log_file.write('---- > exploring op_comb: %s'%op_comb.getString())

            #increase counter
            explored_op_comb +=1

            #add op_comb to the closed list
            if use_closed_list:
                op_combs_closed.append(op_comb)


            # get the wcd value of the current combonation
            [curResFindWcd, bCostIncreased] = check_op_comb(op_comb, cur_grd_task, calc_method, optimal_costs, extended_domain_file_name)


            # log results
            total_num_of_states_explored += curResFindWcd.size_of_search_space
            total_num_of_nodes_explored += curResFindWcd.expanded_nodes

            print('---- > cur_wcd %d min_wcd %d'%(curResFindWcd.wcd_value,min_wcd))
            #update the current wcd_value
            if not bCostIncreased and curResFindWcd.wcd_value < min_wcd and curResFindWcd.wcd_value >= 0:
                print('\nmin wcd reduced from %d to %d at time %d with op_comb : %s:\n '%(min_wcd,curResFindWcd.wcd_value,cur_time_remaining,op_comb.getString()))
                min_wcd = curResFindWcd.wcd_value
                min_wcd_hyps = curResFindWcd
                opt_op_comb = op_comb


                #if wcd is 0 exit search
                if curResFindWcd.wcd_value == 0:
                    print('wcd reached 0 ')
                    zero_wcd_reached = True
                    break

            # within valid results only if the wcd_value is higher than 0 it should be further explored
            if min_wcd > 0 and not bCostIncreased:
                print('op_comb : %s added to op_combs_next '%(op_comb.getString()))
                # get the current wcd paths
                cur_op_path = grd_utils.get_paths(curResFindWcd.optimal_plans,curResFindWcd.wcd_value, calc_method)
                new_op_combs = get_next_ops_combs(cur_grd_task, cur_op_path, design_budget_array, calc_method, op_comb, op_combs_closed, Exhaustive,log_stream)
                #add the newly created op_combs to the listz
                for op_combination in new_op_combs:
                    op_combs.append(op_combination)

            else:
                print('op_comb : %s is not further explored with cur_wcd_value %d and b_cost_increased %d '%(op_comb.getString(),curResFindWcd.wcd_value,bCostIncreased))


            #check time left
            cur_exec_time = int(time.time()) - init_time
            cur_time_remaining = exec_time_limit - cur_exec_time

            if cur_time_remaining < 0:
                timeout = True

            if log_stream!=None:
                wcd_calc_method = '%s-%s'%(calc_method,Exhaustive)
                [total_cost,budget]= get_design_cost(op_comb)
                budget_string = '%s<--->%s'%(total_cost,budget)
                string_to_print = '%s;%s;%s;%s;%s;%s;%s;%s;%.2f;%s;%.2f;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n'%(cur_grd_task.full_template_file_name,cur_grd_task.hyps_file_name,wcd_calc_method,budget_string,init_wcd,min_wcd,init_wcd_hyps, opt_op_comb.getString(),wcd_calc_time,optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored,reduction_per_budget_exhausted,curResFindWcd.wcd_value,op_comb.getString(),design_budget_array_string,cur_grd_task.observability_file_name,cur_grd_task.action_tokens_file_name,cur_grd_task.get_sub_optimal_bound_array_string())
                log_stream.write(string_to_print)
                log_stream.flush()


    except grd_utils.TimeoutException as e:
            print('\nIn grd_wcd_reduction: Caught Timed out!\n')
            progress_log_file.write('\nIn grd_wcd_reduction: Caught Timed out!\n')
            log_stream.write('\nIn grd_wcd_reduction: Caught Timed out!\n')
            cur_exec_time = grd_defs.TIME_OUT
            raise e


    except Exception as ee:
            print('\nIn grd_wcd_reduction: Caught exception: %s' %(ee.args))
            progress_log_file.write('\nIn grd_wcd_reduction: Caught exception: %s' %(ee.args))
            log_stream.write('\nIn grd_wcd_reduction: Caught exception: %s' %(ee.args))
            cur_exec_time = grd_defs.ERROR
            raise ee




    res = [init_wcd,init_wcd_hyps,wcd_calc_time, optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored, min_wcd, opt_op_comb,reduction_per_budget_exhausted ]
    progress_log_file.close()
    return res


#create the extended domain file that contains the name of actions to be removed
def get_reduce_domain_file_name(actions_to_remove,cur_grd_task,add_action_constraints):
    actions_to_remove_string = ''
    if grd_defs.NA in actions_to_remove:
        actions_to_remove_string = 'ALL'
        actions_to_remove = []
        for action_name in cur_grd_task.parsed_pddl_domain.actions:
            actions_to_remove.append(action_name)
    else:
        for action in actions_to_remove:
            actions_to_remove_string +='_%s'%action

    extended_domain = 'domain_%s.pddl'%actions_to_remove_string
    extended_domain_file_name = os.path.join(cur_grd_task.destination_folder_name,extended_domain)
    add_not_allowed_to_domain_file(cur_grd_task.full_domain_file_name, actions_to_remove, extended_domain_file_name,add_action_constraints,cur_grd_task)
    return extended_domain_file_name

def check_op_comb(op_comb, cur_grd_task, calc_method, optimal_costs, extended_domain_file_name, cur_time_remaining = grd_defs.DEFAULT_TIME_LIMIT, log_stream= None):

    #log
    print('\n exploring op_comb : %s'%op_comb.getString())

    #if 'Timed' in calc_method:
    #    parsed_op_comb = []
    #    print(op_comb)
    #    for op in op_comb:
    #        if 'time' in op:
    #            parsed_op = op.split(' time')[0]
    #            print('parsed op is %s'%parsed_op)
    #            parsed_op_comb.append(parsed_op)
    #    op_comb = parsed_op_comb


    #choose a name for the current template file
    extended_template_file_name = 'extended_template_file.pddl'
    #create the relevant template file with the dissallowed actions
    add_not_allowed_grouneded_actions_to_problem_file(cur_grd_task, op_comb, cur_grd_task.destination_folder_name,extended_template_file_name )

    #prepare the current non_obs file
    current_non_observable_actions_file_name = None
    if cur_grd_task.observability_actions_list != None:
        current_non_observable_actions_file_name = 'non-obs-%s.dat'%op_comb.getString()
        create_current_non_obs_file(cur_grd_task, op_comb, current_non_observable_actions_file_name)

    current_tokens_file_name = None
    if cur_grd_task.action_tokens_file_name != None:
        current_tokens_file_name = 'act-tok-%s.dat'%op_comb.getString()
        create_current_act_tok_file(cur_grd_task, op_comb, current_tokens_file_name)

    #perform wcd check for the selection  - if wcd is greater than 0 -add the resulting path to the paths to be explored
    cur_task = grd_task.GrdTask()
    cur_task.initialize_with_files(cur_grd_task.destination_folder_name, extended_domain_file_name, extended_template_file_name, cur_grd_task.hyps_file_name,current_non_observable_actions_file_name,current_tokens_file_name)
    cur_task.set_sub_optimal_bound_array(cur_grd_task.get_sub_optimal_bound_array())
    curResFindWcd = grd_evaluator.calc_wcd_multiple_hyps(calc_method, cur_task, cur_time_remaining, log_stream, optimal_costs)


    #check that the cost of achieving the goals has not increased
    index = 0
    bCostIncreased = False
    #optimal costs
    [cur_optimal_costs,cur_expanded_nodes,cur_solution_array] = grd_utils.check_optimal_costs(cur_task)
    for cost in cur_optimal_costs:
        #log_stream.write('\n cost is %d and init_optimal_cost is %d\n '%(cost, original_optimal_costs_all_hyps[index]))
        if cost < 0 or cost > optimal_costs[index] or cost >= grd_defs.INFINITE_COST:
            #log_stream.write('\n cost increased\n ')
            #print("cost increased")
            bCostIncreased = True
        index += 1



    return [curResFindWcd, bCostIncreased]

def get_next_ops_combs(cur_grd_task, op_path, design_budget_array, calc_method, cur_op_comb, closed_list, Exhaustive,log_stream= None):

    op_combs = []
    next_iteration_operations = []

    if Exhaustive:
        for op in cur_grd_task.planningTaskForExploration.operators:
            next_iteration_operations.append(op.name)
    else:
        next_iteration_operations = op_path


    #add the ops in the op_path to combinations to be explored if the op is non-observable add it twice - once to be removed and once to become observable
              #add the ops in the op_path to combinations to be explored
    #each op_comb contains a list of actions to remove and actions to trun to observable
    non_observable = False
    for op in next_iteration_operations:


        # parse the action name and check if it is non_observable or has a token that needs to be refined
        [op_name, non_observable, act_tok]= grd_utils.parse_action_name(op, calc_method)
        op_name = op_name.replace('(','')
        op_name = op_name.replace(')','')
        op_type = op_name.split()[0]
        to_dissallow = False
        if grd_utils.get_disallowed_actions(cur_grd_task) == None:
            to_dissallow = True
        else:
            if op_type in grd_utils.get_disallowed_actions(cur_grd_task):
                to_dissallow = True

        if to_dissallow:
            #create one copy where the action is to be removed
            #removed_obs_comb = modification_combination([op_name],None, None)
            removed_obs_comb = copy.deepcopy(cur_op_comb)
            removed_obs_comb.removed_actions_list.append(op_name)
            if not removed_obs_comb.is_in_combination(op_combs) and not removed_obs_comb.is_in_combination(closed_list):
                if check_budget_constraint(removed_obs_comb, design_budget_array):
                    op_combs.append(removed_obs_comb)

            #create one copy where the action constraint
            constraint_obs = grd_utils.get_constraints_inst(cur_grd_task,op_path,calc_method,op)

            if constraint_obs is not None:
                constraint_obs_comb = copy.deepcopy(cur_op_comb)
                constraint_obs_comb.constraints_list.append(constraint_obs)
                if not constraint_obs_comb.is_in_combination(op_combs) and not constraint_obs_comb.is_in_combination(closed_list):
                    if check_budget_constraint(constraint_obs_comb, design_budget_array):
                        op_combs.append(constraint_obs_comb)


        #if the action in unobservable - create one combination where it is removed and one where it is made observable
        if non_observable:
            observable_obs_comb = copy.deepcopy(cur_op_comb)
            observable_obs_comb.observed_actions_list.append(op_name)
            #observable_obs_comb = modification_combination(None,[op_name], None)

            #if it's unobservable create one copy where it is observable
            if not observable_obs_comb.is_in_combination(op_combs) and not observable_obs_comb.is_in_combination(closed_list):
                if check_budget_constraint(observable_obs_comb, design_budget_array):
                    op_combs.append(observable_obs_comb)


        #if the action emits a token (possible the nil token) - create a combination where it is refined
        if act_tok != None:
            #refined_obs_comb = modification_combination(None,None, [op_name] )
            refined_obs_comb = copy.deepcopy(cur_op_comb)
            refined_obs_comb.sensor_refined_actions_list.append(op_name)
            if not refined_obs_comb.is_in_combination(op_combs) and not refined_obs_comb.is_in_combination(closed_list):
                if check_budget_constraint(refined_obs_comb, design_budget_array):
                    op_combs.append(refined_obs_comb)

    print('---- > combinations for the next iteration are %d'%len(op_combs))
    for op in op_combs:
        print(op.getString())
    return op_combs

def add_not_allowed_to_domain_file(original_domain_file_name,actions_to_remove,extended_domain_file_name,add_action_constraints,cur_grd_task):

        extended_planning_domain = add_not_allowed_predicates(original_domain_file_name,actions_to_remove,add_action_constraints,cur_grd_task)

        #TODO SARAH - the requirement string is hard coded
        grd_planning_gen.generate_domain_file(extended_planning_domain,extended_domain_file_name,':strips :typing :action-costs  :equality','','')

def add_not_allowed_predicates(domain_file_name,action_names,add_action_constraints,cur_grd_task):


        pddl_parser = parser.Parser( domain_file_name )
        planning_domain = pddl_parser.parse_domain()


        for action_name in action_names :
            #add the relevant predicate to the predicate list
            dis_predicate_name = 'not_allowed_%s'%action_name
            action = planning_domain.actions[action_name]
            predicate = pddl.Predicate(dis_predicate_name,action.signature)
            planning_domain.predicates[dis_predicate_name]=predicate

            #add the precondition to the relevant action
            predicate.IsNot = True
            action.precondition.append(predicate)


        if add_action_constraints is True:

            actionsToConstrain_names = action_names#grd_utils.get_constraints_actions(cur_grd_task)
            actionsToConstrain = []
            if actionsToConstrain_names is None:
                actionsToConstrain_names = []
                for action_name in planning_domain.actions.keys():
                    actionsToConstrain.append(planning_domain.actions[action_name])
                    actionsToConstrain_names.append(action_name)
            else:
                for action_name in action_names:#actionsToConstrain_names:
                    actionsToConstrain.append(planning_domain.actions[action_name])

            for constraint_action_def in actionsToConstrain:

                # add predicate to domain
                param_count = len(constraint_action_def.signature)
                #(constrained_obj)
                predicate_name_constraint = 'constraint_%d'%param_count
                signature_full = copy.deepcopy(constraint_action_def.signature)
                for param in constraint_action_def.signature:
                    param_name = '%s-d'%param[0]
                    signature_full.append(('%s'%param_name,('object')))
                predicate_constraint = pddl.Predicate(predicate_name_constraint,signature_full)
                planning_domain.predicates[predicate_name_constraint]=predicate_constraint

                # if act is in the list add the constraints
                realActionsToConstrain_names = grd_utils.get_constraints_actions(cur_grd_task)
                if constraint_action_def.name in realActionsToConstrain_names:
                    # token assignment
                    constraint_action_def.precondition.append(predicate_constraint)

                    # token performed
                    #for act in actionsToConstrain_names:
                    actionsToConstrain_names = grd_utils.get_constraints_actions(cur_grd_task)
                    for act in actionsToConstrain_names:
                        preidcate_name_cur = 'not_allowed_%s'%act
                        signature_dis = []
                        for param in constraint_action_def.signature:
                            param_name = '%s-d'%param[0]
                            signature_dis.append(('%s'%param_name,('%s'%param[1])))
                        predicate_add_dissallow = pddl.Predicate(preidcate_name_cur,signature_dis)
                        constraint_action_def.effect.addlist.add(predicate_add_dissallow)

                    # add constraints params to signature
                    constraint_action_def.signature = copy.deepcopy(signature_full)


        return planning_domain

#holds the modifications combination used in the reduced method
class modification_combination(object):
    '''
    classdocs
    '''
    def __init__(self,removed_actions, observed_actions, sensor_refined_actions, constraints):
        '''
        Constructor
        '''
        self.removed_actions_list= []
        if removed_actions != None:
            self.removed_actions_list  = removed_actions
        self.observed_actions_list= []
        if observed_actions != None:
            self.observed_actions_list  = observed_actions

        self.sensor_refined_actions_list= []
        if sensor_refined_actions != None:
            self.sensor_refined_actions_list  = sensor_refined_actions

        self.constraints_list  = []
        if constraints != None:
            self.constraints_list  = constraints

    def compare(self,other_mod_combination):
        bEqual = True

        for mod in self.removed_actions_list:
            if mod not in other_mod_combination.removed_actions_list:
              bEqual = False
        for mod in self.observed_actions_list:
            if mod not in other_mod_combination.observed_actions_list:
              bEqual = False
        for mod in self.sensor_refined_actions_list:
            if mod not in other_mod_combination.sensor_refined_actions_list:
              bEqual = False
        for mod in self.constraints_list:
            if mod not in other_mod_combination.constraints_list:
              bEqual = False

        return bEqual

    def getString(self):

        mod_comb_string = '[['

        for mod in self.removed_actions_list:
            mod_comb_string += mod
            mod_comb_string += ' '

        mod_comb_string += ']--['

        for mod in self.observed_actions_list:
            mod_comb_string += mod
            mod_comb_string += ' '

        mod_comb_string += ']--['

        for mod in self.sensor_refined_actions_list:
            mod_comb_string += mod
            mod_comb_string += ' '

        mod_comb_string += ']--['

        for mod in self.constraints_list:
            mod_comb_string += mod[0]
            mod_comb_string += ' '
            for param in mod[1]:
                mod_comb_string += param
                mod_comb_string += ' '
            mod_comb_string = mod_comb_string.replace('(','')
            mod_comb_string = mod_comb_string.replace(')','')

        mod_comb_string += ']]'

        return mod_comb_string

    def is_in_combination(self,mod_combs):
        if mod_combs is None or len(mod_combs) == 0:
            return False

        in_combination = False

        for mod in mod_combs:
            if self.compare(mod):
                in_combination = True

        return  in_combination

    def get_count(self):
        return [len(self.removed_actions_list,len(self.observed_actions_list)),len(self.sensor_refined_actions_list),len(self.constraints_list)]

# if the bound has one element - it is a general bound on the number of allowed modifications
# otherwise - it is a specific bound for each modification type
def check_budget_constraint( mod_comb, budget_array):

        # integrated design bound
        if len(budget_array) == 1:
            if len(mod_comb.removed_actions_list) + len(mod_comb.observed_actions_list) + len(mod_comb.sensor_refined_actions_list) + len(mod_comb.constraints_list) <= budget_array[0]:
                print('---- > op_comb: %s respects the budget which is %d'%(mod_comb.getString(),budget_array[0]))
                return True
            else:
                print('---- > op_comb: %s exceedes the budget %d'%(mod_comb.getString(), budget_array[0]))
                return False
        #type specific
        else:
            if len(budget_array) == 3:

                if len(mod_comb.removed_actions_list)<= budget_array[0] and len(mod_comb.observed_actions_list) <= budget_array[1] and len(mod_comb.sensor_refined_actions_list) <= budget_array[2]:
                    #print('\nTrue')
                    return True
                else:
                    #print('\nFalse')
                    return False

            else:

                if len(budget_array) == 4:
                    print('%s-%s-%s-%s-%s-%s-%s-%s'%(len(mod_comb.removed_actions_list),budget_array[0],len(mod_comb.observed_actions_list), budget_array[1], len(mod_comb.sensor_refined_actions_list), budget_array[2], len(mod_comb.constraints_list),budget_array[3]))

                    if len(mod_comb.removed_actions_list)<= budget_array[0] and len(mod_comb.observed_actions_list) <= budget_array[1] and len(mod_comb.sensor_refined_actions_list) <= budget_array[2] and len(mod_comb.constraints_list) <= budget_array[3]:
                        #print('\nTrue')
                        print('---- > op_comb: %s respects the ind budget'%(mod_comb.getString()))
                        return True
                    else:
                        print('---- > op_comb: %s violates the ind budget'%(mod_comb.getString()))
                        return False

                else:
                    print('Invalid budget array')
                    import sys
                    sys.exit()

def get_design_cost(mod_comb):

    # integrated design bound
    total_cost = len(mod_comb.removed_actions_list) + len(mod_comb.observed_actions_list) + len(mod_comb.sensor_refined_actions_list)  + len(mod_comb.constraints_list)
    sep_cost = []
    sep_cost.append(len(mod_comb.removed_actions_list))
    sep_cost.append(len(mod_comb.observed_actions_list))
    sep_cost.append(len(mod_comb.sensor_refined_actions_list))
    sep_cost.append(len(mod_comb.constraints_list))

    return [total_cost,sep_cost]



def add_not_allowed_grouneded_actions_to_problem_file(grd_task, op_comb , working_directory, extended_problem_file_name, cur_non_obs_file = None):
    '''
    This methods works with template or problem files
    '''
    #open problem file

    print('performing extention for file %s and comb %s'%(extended_problem_file_name,op_comb.getString()))
    instream_problem  = open(grd_task.full_template_file_name)

    #open destination file
    extended_problem_file_name = os.path.join(working_directory,extended_problem_file_name)

    with open(extended_problem_file_name, 'w') as outstream:

        line = instream_problem.readline()

        init_line_reached = False
        while line and not init_line_reached:

            #print('line is %s'%line)

            line = line.strip()
            if '(:init' in line or '(:INIT' in line :
                line_to_print = generate_not_allowed_init_state(grd_task,line,instream_problem,op_comb,cur_non_obs_file)
            else:
                if grd_defs.CONSTRAINT_DESIGN and '(:objects' in line:
                    add_closing_bracet = False
                    if ')' in line:
                        line = line.replace(')','')
                        add_closing_bracet = True

                    const_type = grd_utils.get_constraint_type(grd_task)
                    line_to_print = line + ' \n dummy_obj - %s \n'%const_type
                    if add_closing_bracet:
                        line_to_print += ')'


                else:
                    line_to_print = line

            print(line_to_print,file = outstream)
            line = instream_problem.readline()

        outstream.close()
    instream_problem.close()



    return extended_problem_file_name

def generate_not_allowed_init_state(grd_task, init_line, instream_template, op_comb, cur_non_obs_file= None):

        init_statement = init_line +'\n'
        next_line = instream_template.readline()
        while ')\n' != next_line :
            init_statement = init_statement + next_line
            next_line = instream_template.readline()


        for action in op_comb.removed_actions_list:

            print('action in not allowed %s'%action)

            action = action.replace('(','')
            action = action.replace(')','')
            if 'dummy_obj' in action:
                print('debug')
            param_count = grd_utils.get_param_count(grd_task,action)
            split_action = action.split()
            action_list = split_action[:param_count+1]
            action_string = ''
            for elm in action_list:
                action_string += '%s '%elm

            not_allowed_string = '(not_allowed_%s)'%(action_string)
            init_statement += not_allowed_string+'\n'


        #if the non-obs file is defined - add the relevant predicates to the initial state
        if cur_non_obs_file != None:
            f = open(cur_non_obs_file)
            non_obs_lines = f.readlines()
            f.close()

            for non_obs in non_obs_lines:
                non_obs = non_obs.replace('(','')
                non_obs = non_obs.replace(')','')
                non_obs = non_obs.replace('\n','')

                not_observable_string = '(non-observable_%s)'%(non_obs)
                init_statement += not_observable_string+'\n'



        # get every operator in the task and figure out if it is in the list of actions to constrain
        for op in grd_task.planningTaskForExploration.operators:

            op_params_string = ''
            constrain_param_string = ''
            parsed_op_name = op.name.replace('(','')
            parsed_op_name = parsed_op_name.replace(')','')
            op_type = parsed_op_name.split()[0]
            ops_to_constraint = grd_utils.get_constraints_actions(grd_task)
            to_constraint = False
            if ops_to_constraint is None:
                to_constraint = True
            elif op_type in ops_to_constraint:
                to_constraint = True


            if to_constraint is True:
                param_count = grd_utils.get_param_count(grd_task,op.name)
                if len(op_comb.constraints_list) != 0:

                    # figure our if an op is in the constraint list
                    for const_op,const_params in op_comb.constraints_list:
                        const_op = const_op.replace(' )',')')
                        op_name = op.name.replace(')','')
                        op_name = op_name.replace('(','')
                        if const_op == op_name:
                            for param in parsed_op_name.split()[1:]:
                                op_params_string += '%s '%param
                            for param in const_params:
                                constrain_param_string += '%s '%param

                        else:
                            for param in parsed_op_name.split()[1:]:
                                op_params_string += '%s '%param
                                constrain_param_string += ' dummy_obj '
                else:

                    for param in parsed_op_name.split()[1:]:
                        op_params_string += '%s '%param
                        constrain_param_string += ' dummy_obj '


                constrain_string= '(constraint_%d %s %s)\n'%(param_count,op_params_string,constrain_param_string)
                init_statement += constrain_string


        init_statement += ')' +'\n'



        return init_statement

def create_current_non_obs_file(grd_task, obs_comb, current_non_observable_actions_file_name):
        original_non_obs_file = open(grd_task.observability_file_name )
        cur_non_obs_file_name = os.path.join(grd_task.destination_folder_name,current_non_observable_actions_file_name)
        cur_non_obs_file = open(cur_non_obs_file_name,'w')

        #open original obs file and check if the non-observable actions appears in the list of observables to remove
        for line in original_non_obs_file :
            #go through all combs to observable and check if the line contains one of them
            is_to_observable = False
            for op in obs_comb.observed_actions_list:
                op_string = op.replace('(','')
                op_string = op_string.replace(')','')
                if line.lower().startswith(op_string.lower(),1):
                    is_to_observable  = True

            if not is_to_observable:
                cur_non_obs_file.write(line)

        original_non_obs_file.close()
        cur_non_obs_file.close()

def create_current_non_obs_file(grd_task, obs_comb, current_non_observable_actions_file_name):
    original_non_obs_file = open(grd_task.full_path_observability_file_name )
    cur_non_obs_file_name = os.path.join(grd_task.destination_folder_name,current_non_observable_actions_file_name)
    cur_non_obs_file = open(cur_non_obs_file_name,'w')

    #open original obs file and check if the non-observable actions appears in the list of observables to remove
    for line in original_non_obs_file :
        #go through all combs to observable and check if the line contains one of them
        is_to_observable = False
        for op in obs_comb.observed_actions_list:
            op_string = op.replace('(','')
            op_string = op_string.replace(')','')
            if line.lower().startswith(op_string.lower(),1):
                is_to_observable  = True

        if not is_to_observable:
            cur_non_obs_file.write(line)

    original_non_obs_file.close()
    cur_non_obs_file.close()

def create_current_act_tok_file(grd_task, obs_comb, current_tokens_file_name):

    original_token_file = open(grd_task.full_action_tokens_file_name )
    cur_token_file_name = os.path.join(grd_task.destination_folder_name,current_tokens_file_name)
    cur_token_file = open(cur_token_file_name,'w')

    if len(obs_comb.sensor_refined_actions_list)>1:
        print ('two actions')

    # open original token file and check if the sensored-refined actions appears in the list of tokens
    for line in original_token_file :

        # check if the line reprsents a token that needs to be refined
        is_to_refined = check_if_token_is_to_be_refined(line, obs_comb.sensor_refined_actions_list)

        # if it is create a token that refines it
        if is_to_refined:
            #cur_token_file.write(line)
            grd_defs.REFINEMENT_INDEX =grd_defs.REFINEMENT_INDEX +  1
            params_string = ''
            line_split = line.split()
            for param in line_split[2:]:
                params_string += param
                params_string += ' '

            refined_line = '%s %s%d %s\n' %(line_split[0],grd_defs.token_prefix,grd_defs.REFINEMENT_INDEX, params_string)
            cur_token_file.write(refined_line)
            print("refined %s to %s"%(line, refined_line))
        else:
            cur_token_file.write(line)

    original_token_file.close()
    cur_token_file.close()


def check_if_token_is_to_be_refined(line, sensor_refined_actions):

    for op in sensor_refined_actions:

        inconsistent = False

        op = op.replace('(','')
        op = op.replace(')','')

        op_split= op.split()
        line = line.replace('(','')
        line = line.replace(')','')
        line_split = line.split()

        # make sure the action name is the same and they have the same number of params
        if line_split[0] != op_split[0] or len(line_split) != len(op_split)+1:
            continue

        # check params - if a params that does not fit is found - break the loop and move to the next op
        index = 2
        for line_param in line_split[2:]:
            op_param = op_split[index-1]
            if line_param != op_param:
                inconsistent = True
                break
            index += 1

        if not inconsistent:
            return True

    # if the execution is here - it means all tokens have been examined and the token is not to be refined
    return False

def track_design(op_comb,reduction_per_budget_exhausted,min_wcd,log_file=None):

    [total_cost,sep_cost] = get_design_cost(op_comb)
    if not reduction_per_budget_exhausted.get(total_cost):
        reduction_per_budget_exhausted[total_cost] = min_wcd
        if log_file is not None:
            log_file.write('Inserting value for budget: reduction_per_budget_exhausted[%d] = %d\n'%(total_cost,min_wcd))

    else:
        wcd_for_budget = reduction_per_budget_exhausted.get(total_cost)
        if wcd_for_budget> min_wcd:
            reduction_per_budget_exhausted[total_cost] = min_wcd
            if log_file is not None:
                log_file.write('Updating value for budget::: reduction_per_budget_exhausted[%s] = %d\n'%(total_cost,min_wcd))


