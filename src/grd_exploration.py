'''
Created on May 20, 2014

@author: sarahn
'''

"""
Various methods for exploring the grd task
"""

import grd_defs,grd_planning_gen,grd_planning
from search import searchspace
import os
from collections import deque
import time


# keeping the results of the hypothesis
class hyp_result:

    def __init__(self,obs_seq, atoms, test_failed, optimal_cost):
        self.obs_seq = obs_seq
        self.atoms = atoms
        self.test_failed = test_failed
        self.optimal_cost = optimal_cost

    def getString(self):
        string_to_print = ''

        obs_seq_string = ''
        for obs in self.obs_seq :
            obs_seq_string += '%s'%obs.name

        string_to_print+='observation sequence :: %s\n'%obs_seq_string

        string_to_print+= 'atoms ::  %s\n'%self.cost_Not_O

        string_to_print+= 'test_failed :: %s\n'%self.test_failed

        string_to_print+= 'optimal cost :: %s\n'%self.optimal_cost

        return string_to_print

class sequence_result:

    def __init__(self, obs_seq, relevant_hyp_res_array, calculation_folder):
        self.obs_seq = obs_seq
        self.relevant_hyp_res_array = relevant_hyp_res_array
        self.calculation_folder = calculation_folder


    def getString(self):

        string_to_print = '\n'

        obs_seq_string = ''
        for obs in self.obs_seq :
            obs_seq_string += '%s'%obs.name
        string_to_print +='observation sequence :: %s\n'%obs_seq_string

        string_to_print +='observation length :: %d\n'%len(self.obs_seq)

        array_string = ''
        for hyp_prob in self.relevant_hyp_res_array:
            array_string += 'hyp:%s prob is %f\n'%(hyp_prob.atoms,hyp_prob.Probability_O)

        string_to_print += 'calculation folder is %s\n'%self.calculation_folder

        return string_to_print

class GrdSearchNode(searchspace.SearchNode):

    def __init__(self, state, parent, action, g, indices_of_relevant_hyps):
        super(GrdSearchNode, self).__init__(state, parent, action, g)
        self.relevant_hyps = indices_of_relevant_hyps
        self.goal_reached_hyps = []
        self.cost = 0



    def remove_hyp_from_relevant(self, name_of_hyp_to_remove):
        print('self.relevant_hyps')
        print(self.relevant_hyps)
        print('name_of_hyp_to_remove')
        print(name_of_hyp_to_remove)


        self.relevant_hyps.remove(name_of_hyp_to_remove)

        print('self.relevant_hyps after remove')
        print(self.relevant_hyps)


    def add_hyp_to_goal_reached(self, name_of_hyp_to_add):
        self.goal_reached_hyps.append(name_of_hyp_to_add)


def explore_grd_task(grd_task, depth_limit):
    """
    #BFS exporation of the grd task up to the depth_limit
    return the resulting observation sequences
    :param
    """

    #timer
    init_time = int(time.time())

    #get hyps names
    hyp_index_set = []
    for hyp in grd_task.hyps_set:
        hyp_index_set.append(hyp.name)    
        
    # a queue keeping track of all explored nodes
    queue = deque()           
    # get the initial state of the planning task
    root_node = make_grd_root_node(grd_task.planningTaskForExploration.initial_state, hyp_index_set)
    queue.append(root_node)

    # a list to hold the states that are reached
    # the actual check on these states needs not be duplicated whereas they do need to be entered to the queue
    explored_states = []
    explored_states.append(root_node.state)

    # counts the number of iterations
    iteration_num = 0
    obs_sequences_res = []
    num_of_explored_states = 0
    optimal_costs = []
    index = -1
    # loop as long as there are nodes to explore
    while queue:

        index += 1

        # get the next node to explore
        grd_node = queue.popleft()
        # the observation sequence examined in the current iteration
        obs_seq = grd_node.extract_solution()

        # holding the relevant hyps of a sequence
        cur_relevant_hyps = []

        # For the empty observation we check the planning costs
        if len(obs_seq) == 0:

            bFurtherExplore = True

            [optimal_costs, cur_count_expaneded_states, solution_array] = check_optimal_costs(grd_task, grd_node, index)

            # stats
            num_of_explored_states += cur_count_expaneded_states

            # set optimal costs
            grd_task.set_optimal_costs(optimal_costs)
            original_optimal_costs = optimal_costs

            # populate the result
            hyp_res_array = []
            cur_hyp_index = 0
            for hyp in grd_task.hyps_set:
                hyp_res = hyp_result(obs_seq, hyp.atoms, False, optimal_costs[index])
                hyp_res_array.append(hyp_res)
                if optimal_costs[cur_hyp_index] >= 0:
                    cur_relevant_hyps.append(cur_hyp_index)

                # check if the problem is worth exploring
                if len(cur_relevant_hyps) <= 0:
                    bFurtherExplore = False

                cur_hyp_index += 1


            check_res = sequence_result(obs_seq, hyp_res_array, grd_task.destination_folder_name)
            obs_sequences_res.append([obs_seq, check_res, optimal_costs, solution_array])

        #not an empty sequence
        else:
            [bFurtherExplore, cur_node_relevant_hyps] = perform_check_on_obs(grd_node, grd_task, depth_limit)

            num_of_explored_states += cur_count_expaneded_states

            # append the current result only if it should be explored
            if bFurtherExplore :
                # append the observation sequence to the results
                obs_sequences_res.append([obs_seq, check_res, cur_node_optimal_costs, solution_array])



        # If the node is to be further explored - add its successor states to the queue 
        if bFurtherExplore:
            # create the successor states which are extracted from the task for which the relevance analysis was not performed
            successor_states = grd_task.planningTaskForExploration.get_successor_states(grd_node.state)
            for operator, successor_state in successor_states:
                child_node = make_grd_child_node(grd_node, operator, successor_state, cur_relevant_hyps)
                queue.append(child_node)
                print('appending %s'%child_node.extract_solution())

        iteration_num = iteration_num +1

    # total time
    exec_time = int(time.time()) - init_time

    # return result
    return [obs_sequences_res, exec_time, num_of_explored_states, iteration_num, original_optimal_costs]

def perform_check_on_obs(grd_node, grd_task, depth_limit):
    """
    #performs the check the validity of the number of hyps the observation sequences satisfies
    """
    bFurtherExplore = True

    obs_seq = grd_node.extract_solution()
    obs_seq_names = []
    for obs in obs_seq :
        obs_seq_names.append(obs.name)
    # get the cost of the obs_seq
    seq_cost = grd_task.get_action_sequence_cost(obs_seq_names )

    # if there is a maximal depth allowed - check if it has been exceeded
    if depth_limit != -1:
        if seq_cost > depth_limit:
            bFurtherExplore = False

    # check which hyps the observation sequence satisfies - if it is distinctive (satisfies one or less) do not explore it further
    current_plans = check_plans(grd_task, grd_node, grd_node.relevant_hyps)
    # go through the resluts and see what the current relevant hyps are
    current_relevant_hyps = []
    for [hyp_index, current_solution, test_failed] in current_plans:
        solution_sequence = current_solution.solution_seq
        if grd_task.is_path_legal(obs_seq, solution_sequence, hyp_index):
            current_relevant_hyps.append(hyp_index)

    if len(current_relevant_hyps) <= 1:
        bFurtherExplore = False

    return [bFurtherExplore, current_relevant_hyps]


            
def get_observable_projection(obs_seq,pgrd_task):
    observable_obs_seq= []
    for obs in obs_seq:
        obs_name = obs.name
        obs_name = obs_name.replace('(','')
        obs_name = obs_name.replace(')','')
        is_non_observable = False

        for non_obs_action in pgrd_task.non_observable_actions_list :
            if obs_name.lower() in non_obs_action.lower():
                is_non_observable = True

        if is_non_observable == False:
            observable_obs_seq.append(obs)

    return observable_obs_seq

def check_optimal_costs(grd_task,grd_node=None,index=0):
    
    optimal_costs = []
    count_expanded_states = 0
    solution_array = []
    
    

    #if the node is not specified take the root node
    if grd_node == None :
        
        pgrd_node = make_grd_root_node(grd_task.planningTaskForExploration.initial_state,None)
    
      
    # go through all the hyps of the problem and get the optimal costs for their achievement

    cur_relevant_hyps = []
    if grd_node.relevant_hyps != [] and grd_node.relevant_hyps != None:
        cur_relevant_hyps = grd_node.relevant_hyps

    hyp_index = 0
    
    for hyp in grd_task.hyps_set:
        
        #in order to prevent uneeded calculations
        if cur_relevant_hyps !=[] and hyp_index not in cur_relevant_hyps:            
            optimal_costs.append(grd_defs.INFINITE_COST)
            solution_array.append([])
            
                    
        else:

            #problem file
            current_problem_file = grd_planning_gen.generate_current_problem_file(grd_task.hyps_set[hyp_index], grd_node, grd_task.full_template_file_name, grd_task.destination_folder_name, hyp_index, index, grd_task)
            [current_solution,test_failed,signal] = grd_planning.perform_planning(grd_task.destination_folder_name, grd_task.full_domain_file_name, os.path.abspath(current_problem_file))
            count_expanded_states += current_solution.num_expanded_states
            solution_array.append(current_solution)
            #if this fails for one of the hyps - update value to -1 since one of the hyps is unreachable
            if test_failed == True :
                                   
                #update original optimal cost
                optimal_costs.append(grd_defs.INFINITE_COST)
                print('In check_optimal_costs test_failed for task %s and hyp:'%pgrd_task.task_name)
                print('hyp.atoms : %s'%hyp.atoms)
                                    
            else:
                #update optimal costs
                optimal_costs.append(int(current_solution.plan_cost))
                                                
        hyp_index +=1

    print('before leaving optimal costs they are ')
    print(optimal_costs)
    return [optimal_costs,count_expanded_states,solution_array]
           


def get_successor_states(grd_task,state):
    successor_states = grd_task.planningTaskForExploration.get_successor_states(state)
    return successor_states

def make_grd_root_node(initial_state,relevant_hyps):
    """
    Construct an initial search node. The root node of the search space
    does not links to a parent node, does not contains an action and the
    g-value is zero.

    @param initial_state: The initial state of the search space.
    """   
    return GrdSearchNode(initial_state, None, None, 0,relevant_hyps)
def make_grd_child_node(parent_node, action, state,relevant_hyps):
    """
    Construct a new search node containing the state and the applied action.
    The node is linked to the given parent node.
    The g-value is set to the parents g-value + 1.
    """
    #TODO: the g here is hard coded to be the path length - change it to be the cost of the operation
    return GrdSearchNode(state, parent_node, action, parent_node.g + 1,relevant_hyps)


        
def check_plans(grd_task, grd_node, relevant_hyps):

    plans = []
    hyp_index = -1
    #iterate though hyps and for the relevant ones, perform a search from the current location
    for hyp in grd_task.hyps_set:
                
        hyp_index += 1

        # explore the hyps that are relevant to the node
        if(hyp_index in relevant_hyps):
                        
            #generate curret problem file
            current_problem_file = grd_planning_gen.generate_current_problem_file(grd_task.hyps_set[hyp_index], grd_node, grd_task.template_file_name, grd_task.destination_folder_name, hyp_index, 0, grd_task)
            [current_solution,test_failed,signal] = grd_planning.perform_planning(grd_task.destination_folder_name,os.path.abspath(grd_task.domain_file_name),os.path.abspath(current_problem_file))
            plans.append([hyp_index, current_solution, test_failed])
            
    return plans

           
     
