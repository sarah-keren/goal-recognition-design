__author__ = 'sarah'

'''
Created on May 19, 2014
Containing evaluators of grd models
@author: sarahn
'''

#imports
import grd_defs,grd_utils,grd_task,grd_planning_converter,grd_planning,grd_planning_gen, grd_exploration, grd_wcd_reduction, grd_options
import os,time,sys,copy
import signal


# find the max wcd among multiple hyps
def calc_wcd_multiple_hyps (calc_method, grdTask, exec_time_limit, log_stream = None, original_optimal_costs= None, examined_combs = grd_defs.comb_all_ordered_pairs):

    # open a file to keep track of the wcd of all pairs
    pair_wcd_file_name = os.path.join(grdTask.destination_folder_name,'pair_wcd_file')
    pair_wcd_file = open(pair_wcd_file_name,'w')


    # start timer
    ts_start = int(time.time())

    # generate the pairs of hyps from the hyps file - later to be be solved separately
    [hyp_pairs_files_list,num_of_hyps] = generate_hyp_sets(grdTask.destination_folder_name, grdTask, examined_combs)

    # remaining time
    ts_current = int(time.time())
    cur_exec_time = ts_current-ts_start


    pair_index = 0
    max_wcd =  grd_defs.DEFAULT_MAX_VAL
    max_pair_result = None
    total_expanded_nodes = 0
    total_size_of_search_space  = -1

    #set timer (taken from http://stackoverflow.com/questions/366682/how-to-limit-execution-time-of-a-function-call-in-python)
    signal.signal(signal.SIGALRM, grd_utils.signal_handler)
    signal.alarm(exec_time_limit)

    try:
        # Find the wcd of every pair in the pair list generated above
        for hyp_pair_file in hyp_pairs_files_list:

            #get hyp names
            [first_hyp_index, second_hyp_index ] = get_hyps_names(hyp_pair_file)


            # create a grd_task with the pair of hyps
            cur_grdTask = grd_task.GrdTask()

            # initialize task: destination_folder_name,domain_file,template_file,hyps_file_name,observability_file_name = None,action_token_file_name = None,task_name=None
            cur_grdTask.initialize_with_files(grdTask.destination_folder_name, grdTask.domain_file_name, grdTask.template_file_name, hyp_pair_file,grdTask.observability_file_name, grdTask.action_tokens_file_name)
            if grdTask.bound_array != None:
                cur_grdTask.bound_array = [grdTask.bound_array[first_hyp_index],grdTask.bound_array[second_hyp_index]]


            # create current optimal costs array
            cur_optimal_costs = None
            if original_optimal_costs != None:
                cur_optimal_costs = [original_optimal_costs[first_hyp_index],original_optimal_costs[second_hyp_index]]


            # create a string with the current hyps names
            hyps_name_string = '[%s::%s<->%s::%s]'%(grdTask.hyps_set[first_hyp_index].name,grdTask.hyps_set[first_hyp_index].atoms,grdTask.hyps_set[second_hyp_index].name,grdTask.hyps_set[second_hyp_index].atoms)

            # measure the remaining time
            ts_current = int(time.time())
            cur_exec_time = ts_current - ts_start
            current_remaining_time = exec_time_limit - cur_exec_time


            # calculate current wcd
            res_cur_wcd_pair = calc_wcd_two_hyps(calc_method,cur_grdTask,current_remaining_time,log_stream,hyps_name_string,cur_optimal_costs)

            # advance the counter
            pair_index +=1

            # if the wcd value <0 the wcd value is not valid - this is the returned value
            if res_cur_wcd_pair.wcd_value < 0 :
                max_wcd = res_cur_wcd_pair.wcd_value
                max_pair_result = res_cur_wcd_pair
                break

            # keep the max wcd and other parameters
            if max_pair_result == None or  max_wcd < res_cur_wcd_pair.wcd_value:
                max_wcd =  res_cur_wcd_pair.wcd_value
                max_pair_result = res_cur_wcd_pair
                print('cur_max_wcd updated to be %d for hyps pair %s'%(max_wcd,max_pair_result))

            # update the aggregated counts
            total_expanded_nodes += 1
            total_size_of_search_space += res_cur_wcd_pair.size_of_search_space


            # set the actual hyps indexes
            pair_wcd_file.write('%d-%d : %s\n with common sequence %s\n\n\n'%(first_hyp_index,second_hyp_index,res_cur_wcd_pair.wcd_value,res_cur_wcd_pair.wcd_seq))

    except grd_utils.TimeoutException as e:
            print('\nIn calc_wcd_multiple_hyps Caught Timed out!\n')
            log_stream.write('\n In calc_wcd_multiple_hyps Caught Timed out! \n')
            max_wcd = grd_defs.TIME_OUT
            max_pair_result.optimal_plans = '**Time out exception'

    except Exception as e:
            print('\nIn calc_wcd_multiple_hyps Caught excpetion: %s\n' %e.args )
            log_stream.write('\nIn calc_wcd_multiple_hyps Caught excpetion: %s\n' %e.args)
            max_wcd = grd_defs.ERROR
            max_pair_result.optimal_plans = 'exception occured %s'%e.args

    #close file
    pair_wcd_file.close


    #return wcd
    res_wcd_multiple_hyps = ResFindWcd(grdTask,max_wcd,max_pair_result.optimal_plans_costs,max_pair_result.optimal_plans,max_pair_result.wcd_seq,cur_exec_time,total_expanded_nodes,total_size_of_search_space,max_pair_result.hyps_pair)
    return res_wcd_multiple_hyps

def calc_wcd_two_hyps(calc_method, grdTask, time_limit, log_stream=None, hyps_array=None, optimal_costs=None):
    '''
    calculate the wcd value of a pair of hyps
    :param grdTask: the task (containing two hyps) to evaluate
    :param exec_time_limit: time limit
    :param log_stream : the log file path
    :param hyps_array: the array of hyps
    :param optimal_costs: the optimal cost array of the hyps
    :return: a ResFindWcd struct containing the result
    '''

    #start timer
    ts_start = int(time.time())


    #init values
    wcd_value = grd_defs.DEFAULT_MIN_WCD


    #check the validity of the optimal costs array
    if optimal_costs != None :

        if optimal_costs[0] <= 0 or optimal_costs[1]<= 0:
            #check execution time
            print('no wcd for invalid costs for pair %s'%hyps_array)
            if log_stream != None:
                log_stream.write('\n no wcd for invalid costs for pair %s\n'%hyps_array)
                log_stream.flush()
            ts_current = int(time.time())
            cur_exec_time = ts_current-ts_start
            res = ResFindWcd(grdTask,wcd_value,optimal_costs,[[],[]],[],cur_exec_time,1,0,hyps_array)
            return res

    abs_split_grd_domain_file_name =''
    abs_split_grd_problem_file_name = ''
    #create the converted planning files
    if calc_method == grd_defs.LatestSplit:
        split_conv = grd_planning_converter.grd_converter_latestSplit()
        [abs_split_grd_domain_file_name,abs_split_grd_problem_file_name] = split_conv.grd_to_split(grdTask.full_domain_file_name,grdTask.full_template_file_name,grdTask.full_hyps_file_name,grdTask.destination_folder_name,log_stream)

    elif calc_method == grd_defs.LatestTimed:

        optimal_costs = grd_utils.check_optimal_costs(grdTask)[0]
        import sys
        split_conv = grd_planning_converter.grd_converter_timedLatestSplit(optimal_costs,grdTask.bound_array)
        [abs_split_grd_domain_file_name,abs_split_grd_problem_file_name] = split_conv.grd_to_split(grdTask.full_domain_file_name,grdTask.full_template_file_name,grdTask.full_hyps_file_name,grdTask.destination_folder_name,log_stream)

    elif calc_method == grd_defs.LatestExpose:

        # get optimal costs
        optimal_costs = grd_utils.check_optimal_costs(grdTask)[0]

        # activate the conversion with grd_task.are_observables_specified indicating if non observable or observable actions were specified
        split_conv = grd_planning_converter.grd_converter_latestExpose(grdTask.full_path_observability_file_name, grdTask.are_observables_specified,optimal_costs, grdTask.get_sub_optimal_bound_array())
        [abs_split_grd_domain_file_name,abs_split_grd_problem_file_name] = split_conv.grd_to_split(grdTask.full_domain_file_name,grdTask.full_template_file_name,grdTask.full_hyps_file_name,grdTask.destination_folder_name,log_stream)


    elif calc_method == grd_defs.CommonDeclare:

        # get optimal costs
        optimal_costs = grd_utils.check_optimal_costs(grdTask)[0]

        # convert the grd into planning problems
        split_conv = grd_planning_converter.grd_converter_commmonDeclare(grdTask.full_action_tokens_file_name, optimal_costs, grdTask.get_sub_optimal_bound_array())
        [abs_split_grd_domain_file_name,abs_split_grd_problem_file_name] = split_conv.grd_to_split(grdTask.full_domain_file_name,grdTask.full_template_file_name,grdTask.full_hyps_file_name,grdTask.destination_folder_name,log_stream)

    else:
        print('method %s not supported - error'%calc_method)

    #time remaining for execution
    ts_current = int(time.time())
    time_remaining= time_limit - (ts_current-ts_start)

    #perform the planning
    if grd_defs.HEURISTIC == None:
    	[plan_cmd,planning_failed,signal] = grd_planning.perform_planning(grdTask.destination_folder_name,abs_split_grd_domain_file_name,abs_split_grd_problem_file_name,time_remaining)
    else:
    	[plan_cmd,planning_failed,signal] = grd_planning.perform_planning(grdTask.destination_folder_name,abs_split_grd_domain_file_name,abs_split_grd_problem_file_name,time_remaining,grd_defs.HEURISTIC)
    #if there is no solution - return error
    if planning_failed or signal != 0:
        print('planning command failed for task %s '%grdTask.task_name)
        #log_stream.write('planning command failed for task %s '%grdTask.task_name)
        #log_stream.flush()
        wcd_value = 9000+signal
        ts_current = int(time.time())
        cur_exec_time = ts_current-ts_start
        res = ResFindWcd(grdTask,wcd_value,optimal_costs,[[],[]],[],signal,1,0,hyps_array)
        print('signal is %s'%signal)

        return res

    #extract the info from the files
    plan_cmd.gather_data()


    if hyps_array == None:
        hyps_array = [grdTask.hyps_set[0],grdTask.hyps_set[1]]

    #if there is no solution - return error
    if plan_cmd.plan_cost <= -1 :
        wcd_value = grd_defs.DEFAULT_MIN_WCD
        optimal_plans_costs = [-1,-1]
        optimal_plans = [[],[]]
        plan_cmd.num_expanded_states



    hyps_name_string = '[%s::%s,%s::%s]'%(grdTask.hyps_set[0].name,grdTask.hyps_set[0].atoms,grdTask.hyps_set[1].name,grdTask.hyps_set[1].atoms)

    [wcd_value,wcd_sequence,optimal_plans_costs,optimal_plans] = extract_wcd_value_from_result_file(grdTask,hyps_name_string,calc_method)
    print ('wcd value extracted')
    print (wcd_value)

    #end timer
    ts_after = int(time.time())
    exec_time = ts_after - ts_start

    res = ResFindWcd(grdTask,wcd_value,optimal_plans_costs,optimal_plans,wcd_sequence,exec_time,1,plan_cmd.num_expanded_states,hyps_array)
    return res

# use a bfs exploration to calculate the wcd (see our ICAPS'14 paper)
def calc_wcd_bfs(grd_task, exec_time_limit, log_stream = None):

    # calculation depth limit is constrained by the maximal length
    optimal_costs = grd_utils.check_optimal_costs(grd_task)[0]
    depth_limit = max(optimal_costs)

    # return an array of [obs_seq,prob_check_res] of the observations sequences that comply with the specified requirements
    [all_obs_seqences_res, exec_time, num_of_explored_states, num_of_explored_nodes, original_optimal_costs] = grd_exploration.explore_grd_task(grd_task, depth_limit)

    for obs_seq in all_obs_seqences_res:
        print(obs_seq)
        print('\n')

    #transform the observation sequences into ResFindWcd results that can be later used
    obs_seqences_res = []
    for obs_seq,cur_obs_sequence_res,cur_optimal_costs in all_obs_seqences_res:
        if len(obs_seq)== 0:
            cur_res_find_wcd_result = ResFindWcd(pgrd_task,len(cur_obs_sequence_res.obs_seq),cur_optimal_costs,None,cur_obs_sequence_res.obs_seq,0,0,0,'all')
            obs_seqences_res.append([cur_obs_sequence_res.obs_seq,cur_res_find_wcd_result])
        else:
            string_of_index_of_valid_hyps = ''
            for hyp in cur_obs_sequence_res.index_of_valid_hyps:
                string_of_index_of_valid_hyps += '|%s :: %s |'%(hyp,pgrd_task.hyps_set[hyp].atoms)
            obs_sequence = []
            for op in cur_obs_sequence_res.obs_seq:
                obs_sequence.append(op.name)

            cur_res_find_wcd_result = ResFindWcd(pgrd_task,len(obs_sequence),cur_optimal_costs,[],obs_sequence,0,0,num_of_explored_states,string_of_index_of_valid_hyps)
            obs_seqences_res.append([cur_obs_sequence_res.obs_seq,cur_res_find_wcd_result])


    max_length_obs_seq = -1
    max_prob_check_res = None

    for obs_seq,prob_check_res in obs_seqences_res:

        #get the maximal length sequence and update the current wcd
        if len(obs_seq) > max_length_obs_seq:
            print('updating max obs')
            max_length_obs_seq =  len(obs_seq)
            max_prob_check_res = prob_check_res
            if log_stream != None:
                log_stream.write('updating max obs %s'%max_prob_check_res.wcd_seq)


    max_prob_check_res.exec_time = exec_time


    #max_prob_check_res.optimal_plans_costs = optimal_costs
    max_prob_check_res.expanded_nodes =  num_of_explored_nodes

    #set_original_optimal_costs
    max_prob_check_res.set_original_optimal_costs(original_optimal_costs)

    return max_prob_check_res


MAX_WCD = 10000000000

def create_string_ops(operators,actions_to_remove):
    '''
    This method will add to the list only the operators that belong to the list of actions to be removed
    '''
    operators_list = []
    for op in operators :
        op_name = op.name.replace('(','')
        op_name = op_name.replace(')','')
        action_name  = op_name.split()[0]
        if action_name in actions_to_remove:
                operators_list.append('(%s)'%op_name)
    return operators_list


#holds the observation combination used in the reduced method
class obs_combination(object):
    '''
    classdocs
    '''
    def __init__(self,removed_actions,observed_actions):
        '''
        Constructor
        '''
        self.removed_actions_list= []
        if removed_actions != None:
            self.removed_actions_list  = removed_actions
        self.observed_actions_list= []
        if observed_actions != None:
            self.observed_actions_list  = observed_actions

    def compare(self,other_obs_combination):
        bEqual = True

        for op in self.removed_actions_list:
            if op not in other_obs_combination.removed_actions_list:
              bEqual = False
        for op in self.observed_actions_list:
            if op not in other_obs_combination.observed_actions_list:
              bEqual = False

        return bEqual


# generating the sets of hyps files from the original hyp file according to the generation type
def generate_hyp_sets(destination_folder_name, grd_task, combs_examined_type = grd_defs.comb_all_pairs):
    '''
    :param folder_name: destination folder
    :param hyp_file_name: file specifying the hyps
    :param combs_examined_type: the combination of hyps to examine (as defined in grd_defs)
    :return: list of generated files
    '''

    # create the list of generated files
    generated_hyp_files = []

    # read all hyps
    f = open(grd_task.full_hyps_file_name)
    hyp_lines = f.readlines()
    f.close()

    import itertools
    s = list(hyp_lines)
    combs = itertools.combinations(range(len(s)), 2)

    # add to the combination list the pair in reversed order
    if combs_examined_type == grd_defs.comb_all_ordered_pairs:

        ordered_combs = []
        for pair in combs:
            ordered_combs.append((pair[0],pair[1]))
            ordered_combs.append((pair[1],pair[0]))
        combs = ordered_combs

        # generate the hyps files
        index = 0
        first_hyp = -1
        second_hyp = -1
        for pair in combs:
            first_hyp = (int)(pair[0])
            second_hyp = (int)(pair[1])
            new_file_name = 'hyp_@_%d_@_%d.dat'%(first_hyp,second_hyp)
            full_new_file_name = os.path.join(destination_folder_name,new_file_name)
            new_file = open(full_new_file_name,'w')
            new_file.write(hyp_lines[first_hyp])
            new_file.write(hyp_lines[second_hyp])
            new_file.close
            generated_hyp_files.append(new_file_name)
            index += 1

    # return the list of generated files
    return [generated_hyp_files,len(s)]
#extacst the names of the hyps from the file name
def get_hyps_names( hyp_pair_file):

        #hyp_%d_%d.dat
        hyp_names = hyp_pair_file.replace('.dat','')
        hyp_names = hyp_names.split('_@_')

        first_hyp_index = int(hyp_names[1])
        second_hyp_index = int(hyp_names[2])
        return [first_hyp_index,second_hyp_index]

def get_optimal_costs_string(optimal_costs,first_hyp_index = None,second_hyp_index = None):

    cur_optimal_costs_string = ''

    if optimal_costs != None:
        #get only the specified pair
        if(first_hyp_index != None):
            cur_optimal_costs = [optimal_costs[first_hyp_index],optimal_costs[second_hyp_index]]
            for cost in cur_optimal_costs:
                cur_optimal_costs_string += '|%s|'%cost
        #get all hyps
        else:
            for cost in optimal_costs:
                cur_optimal_costs_string += '|%s|'%cost


    return  cur_optimal_costs_string

def extract_wcd_value_from_result_file(grd_task,hyps_name_string,calc_method_name,budget_array_string=''):

        '''
        extract the wcd from the result file
        :param grd_task: the current task
        :param hyps_name_string: the name of the hyps being analyzed
        :param calc_method_name: the method name (latestSplit etc)
        :param budget_array_string: if relevant - the budget array
        :return:[wcd_value,wcd_sequence,optimal_plans_costs,optimal_plans]
        '''


        #get the solution file name from the
        sol_file_name = os.path.join(grd_task.destination_folder_name,grd_planning.RESULT_FILE_NAME)
        sol_file  = open(sol_file_name)

        action_counter = -1
        wcd_value = 0
        last_action_cost = 0
        wcd_sequence = []
        #initialize plan costs
        optimal_plans_costs = [0,0]
        optimal_plans = ([],[])

        #ccreate a copy of the result file for the pair of hyps
        #import shutil
        #shutil.copy2(sol_file_name, '%s_%s_%s_%s'%(sol_file_name,hyps_name_string,calc_method_name,budget_array_string))

        split_occurred = False
        for line in sol_file:
            #ignore the delcare actions when counting the actions for the wcd calculation
            if 'declare' in line:
                if '#' in line: #token was declared separately
                    break
            else:

                if 'split' in line:
                    split_occurred = True
                    continue

                #print('\nline is %s'%line)

                #ignore the timer operations
                if 'timer' in line:
                    continue

                action_counter += 1
                line = line.strip()



                #an action performed together
                if 'together' in line:
                    #action = line.replace('_together','')
                    action = line.replace('','')

                    optimal_plans[0].append(action)
                    optimal_plans[1].append(action)
                    wcd_sequence.append(action)
                    #If actions costs are specified: add to the wcd value the cost of the function,
                    action_cost = 0
                    if grd_task.actionCosts == True:
                        action_name = action.replace('(','')
                        action_name = action_name.split('_')[0]
                        action_cost = grd_task.parsed_pddl_domain.actions[action_name].cost

                    else: #uniform cost
                        action_cost = 1

                    wcd_value += action_cost

                    optimal_plans_costs[0] += 1
                    optimal_plans_costs[1] += 1

                else:
                    if 'seperate' in line :
                        #action = line.replace('_seperate','')
                        action = line.replace('','')


                        if ('_#0') in line:
                            action_cost = 0
                            optimal_plans[0].append(action)
                            optimal_plans_costs[0] += 1
                            if split_occurred == False:
                                wcd_sequence.append(action)
                                #If actions costs are specified: add to the wcd value the cost of the function,
                                if grd_task.actionCosts == True:
                                    action_name = action.replace('(','')
                                    action_name = action_name.split('_')[0]
                                    action_cost = grd_task.parsed_pddl_domain.actions[action_name].cost
                                    last_action_cost = action_cost

                                else: #uniform cst
                                    action_cost = 1
                                    last_action_cost = action_cost


                                if calc_method_name == grd_defs.CommonDeclare or calc_method_name == grd_defs.LatestExpose:
                                    wcd_value += action_cost



                        if ('_#1') in line:
                            optimal_plans[1].append(action)
                            optimal_plans_costs[1] += 1
        if calc_method_name == grd_defs.CommonDeclare:
            wcd_value -= last_action_cost


        return [wcd_value,wcd_sequence,optimal_plans_costs,optimal_plans]





# struct to keep the result of the wcd calculation
class ResFindWcd(object):

    def __init__(self,task,wcd_value,optimal_plans_costs,optimal_plans,wcd_seq,exec_time,expanded_nodes,size_of_search_space,hyps_pair,non_obs_sequence = None):
        '''
        Constructor
        '''
        self.task = task
        self.wcd_value  = wcd_value
        self.optimal_plans_costs = optimal_plans_costs
        self.optimal_plans = optimal_plans
        self.wcd_seq = wcd_seq
        self.exec_time = exec_time
        self.expanded_nodes = expanded_nodes
        self.size_of_search_space = size_of_search_space
        self.hyps_pair = hyps_pair
        self.original_optimal_costs = None

    def set_original_optimal_costs(self,orginal_optimal_costs):
        self.original_optimal_costs = orginal_optimal_costs

    # get the string to be printed
    def getStringTuple(self):
        string_to_print = ''
        string_to_print+='%d%s'%(self.wcd_value, grd_defs.DELIMINATOR)
        if grd_defs.TIME_OUT > self.exec_time:
            string_to_print+='%s%s'%('TIME-OUT', grd_defs.DELIMINATOR)
            return string_to_print
        else:
            string_to_print+='%d%s'%(self.exec_time, grd_defs.DELIMINATOR)
        string_to_print+='%d%s'%(self.expanded_nodes, grd_defs.DELIMINATOR)
        string_to_print+='%d%s'%(self.size_of_search_space, grd_defs.DELIMINATOR)

        optimal_costs_string = '['
        for optimal_cost in self.optimal_plans_costs:
                optimal_costs_string+='%d|'%optimal_cost

        optimal_costs_string+= ']%s'%(grd_defs.DELIMINATOR)

        string_to_print += optimal_costs_string

        obs_sequence_string = '['
        for obs in self.wcd_seq:
            obs_sequence_string += ' %s '%obs
        obs_sequence_string += ']%s'%(grd_defs.DELIMINATOR)

        string_to_print += obs_sequence_string

        if self.original_optimal_costs != None:
            original_optimal_costs_string = '['
            for org_optimal_cost in self.original_optimal_costs:
                    original_optimal_costs_string+='%d|'%org_optimal_cost

            original_optimal_costs_string+= ']%s'%(grd_defs.DELIMINATOR)

            string_to_print += original_optimal_costs_string
        else:
            string_to_print += '[ ]%s'%(grd_defs.DELIMINATOR)

        if self.task.observability_file_name != None:
            string_to_print += self.task.observability_file_name
        else:
            string_to_print += '[ ]%s'%(grd_defs.DELIMINATOR)




        return string_to_print

    def getString(self):

        string_to_print = ''
        string_to_print+='wcd value :: %d\n'%self.wcd_value
        if grd_defs.TIME_OUT == self.exec_time:
            string_to_print+='execution time :: %s\n'%'TIME-OUT'
        else:
            string_to_print+='execution time :: %d\n'%self.exec_time
        string_to_print+='expanded nodes :: %d\n'%self.expanded_nodes
        string_to_print+='size of search space :: %d\n'%self.size_of_search_space

        if self.original_optimal_costs != None:
            original_optimal_costs_string = 'original_optimal_costs :: ['
            for org_optimal_cost in self.original_optimal_costs:
                    original_optimal_costs_string+='%d|'%org_optimal_cost

            original_optimal_costs_string+= ']\n'

            string_to_print += original_optimal_costs_string


        if self.optimal_plans_costs != None:
            optimal_costs_string = 'optimal costs :: ['
            for optimal_cost in self.optimal_plans_costs:
                optimal_costs_string+='%d|'%optimal_cost

            optimal_costs_string+= ']\n'

            string_to_print += optimal_costs_string

        obs_sequence_string = '['
        for obs in self.wcd_seq:
            obs_sequence_string += ' %s '%obs
        obs_sequence_string += ']'
        string_to_print += 'wcd sequence :: %s\n' %obs_sequence_string

        string_to_print += 'Hyps are :: %s'%self.hyps_pair




        return string_to_print

def get_task_list(options, combs = grd_defs.comb_max):

    grd_tasks_list = []

    domain_file_name = options.domain_file_name
    template_file_name = options.template_file_name
    hyps_file_name = options.hyps_file_name

    if combs == grd_defs.comb_max:
        grd_tasks_list.append([domain_file_name,template_file_name,hyps_file_name])

    else:
        [hyps_files,len] = grd_utils.generate_hyp_sets_with_index(grd_defs.gen_files_dir ,hyps_file_name, combs)
        for hyp_file in hyps_files:
           grd_tasks_list.append([domain_file_name,template_file_name,hyp_file])

    return grd_tasks_list



'''
The main function used to run the GRD commands 
'''

def evaluate(options):


    if options.delete_log_folders is True or not os.path.exists(grd_defs.log_files_dir):
        print("creating new log folders")
        grd_utils.empty_or_create_log_and_gen_dir()

    print('calc method')
    print(options.calc_methods)
    calc_method = options.calc_methods[0]
    combs = options.comb_examined
    output_file_name = grd_defs.results_file_name
    output_file = open(output_file_name,'a')
    bechnmarks_domain_name = options.domain_name
    grd_tasks_list = get_task_list(options, combs)

    for [domain_file_name,template_file_name,hyps_file_name] in grd_tasks_list:

        try:



            exec_time_limit = grd_defs.DEFAULT_TIME_LIMIT



            #calc wcd bfs
            if grd_defs.WcdBfs in calc_method:

                grd_test_task = grd_task.GrdTask()
                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name)

                # perform evaluation
                res = calc_wcd_bfs(grd_test_task, exec_time_limit)

            #calc latestSplit
            elif grd_defs.LatestSplit == calc_method:

                grd_test_task = grd_task.GrdTask()
                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name)

                # perform evaluation
                res = calc_wcd_multiple_hyps(calc_method, grd_test_task, exec_time_limit)

                #TODO SARAH : Change this to a log function
                print('wcd is %d with wcd_sequence %s'%(res.wcd_value,res.wcd_seq))


            elif grd_defs.LatestTimed == calc_method:

                grd_test_task = grd_task.GrdTask()
                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name)

                #get the bound array and save it in the grd task
                sub_optimal_bound_array = options.sub_optimal_bound_array
                if grd_test_task.actionCosts and sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array:
                    print("Non optimal agents supported only for uniform action costs. Exiting")
                    return

                #parse the budget array
                grd_test_task.sub_optimal_bound_array(sub_optimal_bound_array)
                #get optimal costs
                optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]

                print('The sub-optimal-bound-array is %s'%grd_test_task.sub_optimal_bound_array)

                # perform evaluation
                res = calc_wcd_multiple_hyps(calc_method, grd_test_task, exec_time_limit, None, optimal_costs)

                #TODO SARAH : Change this to a log function
                print('wcd is %d with wcd_sequence %s'%(res.wcd_value,res.wcd_seq))

            elif grd_defs.LatestExpose == calc_method:

                sub_optimal_bound_array = options.sub_optimal_bound_array
                observability_file_name = options.observability_file_name
                recobservability_file_name = options.reciproceobservability_file_name


                #create problem
                grd_test_task = grd_task.GrdTask()

                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name, observability_file_name, None, None, None, recobservability_file_name )

                if grd_test_task.actionCosts and sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array :
                    print("Non optimal agents supported only for uniform action costs. Exiting"%calc_method)
                    return

                optimal_costs = None
                sub_optimal_bound_array = options.sub_optimal_bound_array
                if sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array:
                    #parse the budget array
                    grd_test_task.sub_optimal_bound_array(sub_optimal_bound_array)

                    #get optimal costs
                    optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]

                # perform evaluation
                res = calc_wcd_multiple_hyps(calc_method, grd_test_task, exec_time_limit, None, optimal_costs)

                #TODO SARAH : Change this to a log function
                print('wcd is %d with wcd_sequence %s'%(res.wcd_value,res.wcd_seq))

            elif grd_defs.CommonDeclare == calc_method:

                sub_optimal_bound_array = options.sub_optimal_bound_array
                action_tokens_file = options.action_tokens_file_name


                #create problem
                grd_test_task = grd_task.GrdTask()
                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name, None, action_tokens_file)

                if grd_test_task.actionCosts and sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array :
                    print("Non optimal agents supported only for uniform action costs. Exiting")
                    return


                optimal_costs = None
                sub_optimal_bound_array = options.sub_optimal_bound_array
                if sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array :
                    #parse the budget array
                    grd_test_task.sub_optimal_bound_array(sub_optimal_bound_array)

                    #get optimal costs
                    optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]

                # perform evaluation
                res = calc_wcd_multiple_hyps(calc_method, grd_test_task, exec_time_limit, None, optimal_costs)

                #TODO SARAH : Change this to a log function
                print('wcd is %d with wcd_sequence %s'%(res.wcd_value,res.wcd_seq))

            elif grd_defs.WcdReduce == calc_method or grd_defs.WcdReduceExhaustive == calc_method:


                output_file.write("\nPerforming:: %s %s %s %s %s %s \n---------------------------\n"%(options.calc_methods,options.hyps_file_name,options.design_budget_array_string,options.sub_optimal_bound_array,options.observability_file_name,options.action_tokens_file_name))

                Exhaustive = False
                if grd_defs.WcdReduceExhaustive == calc_method:
                    Exhaustive = True

                add_action_constraints = grd_defs.CONSTRAINT_DESIGN

                wcd_calc_method = options.calc_methods[1]
                design_budget_array_string = options.design_budget_array_string
                budget_array = design_budget_array_string.split(':')
                design_budget_array = [int(i) for i in budget_array]


                observability_file_name = None
                recobservability_file_name = None
                action_tokens_file = None


                if grd_defs.LatestExpose in wcd_calc_method:
                    observability_file_name = options.observability_file_name
                    recobservability_file_name = options.reciproceobservability_file_name

                if grd_defs.CommonDeclare in wcd_calc_method and grd_defs.NA not in options.action_tokens_file_name:
                    action_tokens_file = options.action_tokens_file_name


                actions_to_remove = grd_defs.NA
                if options.actions_to_remove:
                    actions_to_remove = options.actions_to_remove


                #create problem
                grd_test_task = grd_task.GrdTask()
                grd_test_task.initialize_with_files(grd_defs.gen_files_dir, domain_file_name, template_file_name, hyps_file_name, observability_file_name, action_tokens_file,None,None,recobservability_file_name,bechnmarks_domain_name)

                if grd_test_task.are_observables_specified:
                    print('reduction currently only supported for specification of non-observables')
                    return

                sub_optimal_bound_array = options.sub_optimal_bound_array
                if sub_optimal_bound_array and grd_defs.NA not in sub_optimal_bound_array :
                    #parse the budget array
                    grd_test_task.set_sub_optimal_bound_array(sub_optimal_bound_array)

                if design_budget_array:
                    grd_test_task.set_design_budget_array(design_budget_array)



                #get optimal costs
                optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]
                reduction_log_file = open(grd_defs.log_file_name_reduction,'a')




                res = grd_wcd_reduction.reduce_wcd(grd_test_task, design_budget_array, wcd_calc_method, optimal_costs, actions_to_remove, reduction_log_file, grd_defs.DEFAULT_TIME_LIMIT, Exhaustive, add_action_constraints)


                print('\n\n[init_wcd,init_wcd_hyps,wcd_calc_time, optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored, min_wcd, opt_op_comb]\n\n')
                print(res)

                [init_wcd,init_wcd_hyps,wcd_calc_time, optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored, min_wcd, opt_op_comb, reduction_per_budget_exhausted] = res
                wcd_calc_method = '%s-%s'%(wcd_calc_method,Exhaustive)
                design_budget_array_string_parsed= design_budget_array_string.replace(',','=')
                string_to_print = '%s;%s;%s;%s;%s;%s;%s;%s;%.2f;%s;%.2f;%s;%s;%s;%s;%s;%s;%s;%s\n'%(template_file_name,hyps_file_name,wcd_calc_method,design_budget_array_string_parsed,init_wcd,min_wcd,init_wcd_hyps, opt_op_comb.getString(),wcd_calc_time,optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored,reduction_per_budget_exhausted,grd_defs.NA,grd_test_task.observability_file_name,grd_test_task.action_tokens_file_name,grd_test_task.get_sub_optimal_bound_array_string())
                output_file.write(string_to_print)
                output_file.flush()

            else:
                print("Calc method %s not supported. Exiting"%calc_method)


        except grd_utils.TimeoutException as e:
            print('Caught Timed out! return error val\n')
            #string_to_print = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(template_file_name,hyps_file_name,wcd_calc_method,sub_optimal_bound_array,grd_test_task.budget_array,init_wcd,init_wcd_hyps,wcd_calc_time,optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored, min_wcd, 'Caught Timed out! return error val: %s'%e.args)
            output_file.write('In grd_evaluator: Caught Timed out! return error val\n')
            output_file.flush()
        except Exception as e:

            print('Caught excpetion: ')
            print(e.args)
            print('\n')
            #string_to_print = '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n'%(template_file_name,hyps_file_name,wcd_calc_method,sub_optimal_bound_array,grd_test_task.budget_array,init_wcd,init_wcd_hyps,wcd_calc_time,optimal_costs, cur_exec_time, explored_op_comb, total_num_of_nodes_explored, total_num_of_states_explored, min_wcd, 'Caught excpetion: %s' %e.args)
            output_file.write('In grd_evaluator: Caught excpetion: %s'%e  )
            output_file.write('Existing \n')
            output_file.flush()
            raise(e)

        #output_file.close()

if __name__ == '__main__' :
    options = grd_options.Program_Options( sys.argv[1:] )
    evaluate(options)


















