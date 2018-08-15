__author__ = 'sarah'

'''
Generates classical planning files using the various compilations from grd problems to classical planning.
The various compilations are divided into equivalent classes with the base class containing common functionality
'''

#imports
import os,copy
import grd_defs, grd_planning_gen, grd_utils
from pddl import parser,pddl #imports from pypaerplan_s
import itertools



#defs relevant only for the conversions
DEFAULT_EPSILON = 10
DEFAULT_ACTION_COST = 10000
PENALTY_CONST = 100


total_cost_statement = '(= (total-cost) 0)'
metric_min_statement ='(:metric minimize (total-cost))'

#used to prepare the relevant predicates
split_string = 'split'
not_split_string = 'not_split'
done_0_string = 'ag0_done'
done_1_string = 'ag1_done'
not_done_0_string = 'not_ag0_done'
not_done_1_string = 'not_ag1_done'
action_cost_predicate_string = 'increase (total-cost) %d'
timer_predicate_string = 'next_%s ?t - time ?tnext - time'
timer_action_predicate_string = 'next_%s ?t ?tnext'
next_time_string = '(next_%s time%d time%d)'

observability_predicate_string = 'observable_%s'
observable_string = 'observable'
non_observability_predicate_string = 'non-observable_%s'
non_observable_string = 'non-observable'
not_observable_predicate_string = 'not_observable_%s'

# common_declare

# flag indicating if there is a pending token for agent %s
pending_token_declared_predicate_string = 'pending_token_declared'

# indicating the token that token %s has been emmited by agent A
token_emitted_string = 'token_emitted'

# action token assignment (# number of tokens and params)
action_token_assignment_string = 'action_token_ParamsNum_%s'




'''
Base class for all compilations
'''
class grd_converter:
    domain_file_name = ''
    problem_file_name = ''
    action_predicates = {}
    isActionCosts = False
    static_predicates = []
    actionsCostsList = []


    def __init__(self):

        return

    def grd_to_split(self, domain_file_name, template_file_name, hyps_file_name, destination_folder_name, epsilon = DEFAULT_EPSILON,log_stream = None,is_poi_grd = False):
        '''
            Converts from goal recognition design problem into classical planning roblems

            @param domain, template and hyps files
            @param destination_folder_name : where to create the resulting files
            @param epsilon : the discount for performing together actions
            @param log_stream - log

            @return full names of domain and problem files
        '''



        # if epsilon was not specified (and equal to None) replace it with the default
        if epsilon == None:
            epsilon = DEFAULT_EPSILON

        # keeping the planning domain
        pddl_parser = parser.Parser( domain_file_name )
        self.planning_domain = pddl_parser.parse_domain()


        # generate split domain file
        [split_domain_file_name, predicates_to_duplicate] = self.generate_domain_file(os.path.abspath(domain_file_name), os.path.abspath(destination_folder_name),epsilon,is_poi_grd)


        # generate split problem file
        split_problem_file_name = self.generate_split_problem_file(template_file_name, hyps_file_name, predicates_to_duplicate,destination_folder_name,is_poi_grd)


        abs_split_domain_file_name  =  os.path.abspath(split_domain_file_name)
        abs_split_problem_file_name =  os.path.abspath(split_problem_file_name)



        return [abs_split_domain_file_name,abs_split_problem_file_name]

    # add the executing agent to the predicate
    def add_agent_param_to_predicate(self,predicate , index = -1):

        agent_type = 'agent'
        if index == -1 :
            agent_name = '?a'
            predicate.signature.append ([agent_name,(agent_type)])
        else:
            agent_name = 'agent_%d'%index
            predicate.signature.append ([agent_name,(agent_type)])

    # add the executing agent to the signature of an action
    def add_agent_param_to_signature(self,signature):
        agent_type = 'agent'
        agent_name = '?a'
        signature.append ([agent_name,(agent_type)])

    # create actions list with all actions duplicated three times: togheter, and seperate for each agent
    def create_actions_list(self,planning_domain,epsilon,create_together_actions = True, create_split_action = True, create_done_action = True):

        #create predicates that will be used to add a cost to the actions
        self.action_predicates[split_string] = pddl.Predicate(split_string,[])
        #self.action_predicates[not_split_string] = pddl.Predicate(not_split_string,[])
        self.action_predicates[not_split_string] = pddl.Predicate('not(%s)'%split_string,[])
        self.action_predicates[done_0_string] = pddl.Predicate('ag0_done',[])
        self.action_predicates[not_done_0_string] = pddl.Predicate('not(ag0_done)',[])
        self.action_predicates[done_1_string] = pddl.Predicate('ag1_done',[])
        self.action_predicates[not_done_1_string] = pddl.Predicate('not(ag1_done)',[])


        #create three copies of each action : together and separate(for each agent)
        new_action_list = planning_domain.actions.copy()
        for action_name in planning_domain.actions.keys():

            #get the action
            action = planning_domain.actions[action_name]

            #remove the action from the list
            del new_action_list[action_name]

            #create the together copy of the action and add to actions list
            if create_together_actions :
                action_together = self.generate_together_action(action,planning_domain)
                new_action_list[action_together.name] = action_together

            for index in [0,1] :
                # create a copy for separated action and add to actions list for each agent
                action_separate = self.generate_separate_action(action,index,planning_domain)
                # this is an action list
                if type(action_separate) is list:
                    for sep_action in action_separate:
                        new_action_list[sep_action.name] = sep_action
                #this is a single
                else:
                    new_action_list[action_separate.name] = action_separate

        if create_split_action:
            #add the split action
            signature = []
            precondition = [self.action_predicates[not_split_string]]
            effect = pddl.Effect()
            effect.addlist = [self.action_predicates[split_string],pddl.Predicate(action_cost_predicate_string%0,[])]
            split_action = pddl.Action('split-agents', signature ,precondition, effect)
            new_action_list['split-agents'] = split_action

        if create_done_action:
            #add the agent 0 done
            signature = []
            precondition = [self.action_predicates['not_ag0_done'],self.action_predicates[split_string]]
            effect = pddl.Effect()
            effect.addlist = [self.action_predicates['ag0_done'],pddl.Predicate(action_cost_predicate_string%0,[])]
            agent_0_done_action =  pddl.Action('agent-0-done', signature , precondition, effect)
            new_action_list['agent-0-done'] = agent_0_done_action

        return  new_action_list

    # generate the relevant problem file
    def generate_split_problem_file(self,template_file_name,hyp_file_name,predicates_to_duplicate,destination_folder_name,is_poi_grd = False):
        '''
        generates a problem with the goal of each agent achieving a different hyp

        The format that is supported requires that:
        init is starts with '(:init' and is terminated by a separate line containing only ')'
        the goal/hyp is the last element in the file


        @param template_file_name : original template.
        @param hyp_file_name: original hyp
        @predicates_to_duplicate: the predicates that are necessary to be seperate for each agent
        @param destination_folder_name : the folder in which the new file is generated
        @return: the path to the generated file
        '''
        hyps = self.generate_hyps(hyp_file_name)

        #open template file
        instream_template  = open(template_file_name)

        #destination file name
        split_problem_file_name = os.path.join(destination_folder_name,self.problem_file_name)


        with open(split_problem_file_name, 'w') as outstream:

            line = instream_template.readline()
            goal_line_reached = False

            while line and not goal_line_reached:
                line = line.strip()
                print(line)
                if ';' in line :
                    line = instream_template.readline()
                    continue

                if '(:objects' in line.lower():
                    # empty objects statement
                    add_barckets = False
                    #if '(:objects)' in line.replace(" ", ""):
                    #    add_barckets = True
                    line_to_print = self.add_objects(line,instream_template)


                else:

                    if '(:init' in line.lower() :
                        # add the closing brackets for the obejects
                        line_to_print = self.generate_init_state_stmt(line,instream_template,len(hyps),predicates_to_duplicate,True)
                        goal_line_reached = True

                    else:

                        line_to_print = line

                #add line to the file
                print(line_to_print,file = outstream)
                line = instream_template.readline()

            #add goal
            line_to_print = self.generate_goal_stmt(hyps)
            line_to_print += ')\n'
            print(line_to_print,file = outstream)


        outstream.close()
        instream_template.close()

        return split_problem_file_name

    # generate the pair of hyps
    def generate_hyps(self,hyp_file_name):
        '''
        generates the hyps for two hyps only
        @return: the pair of hyps
        '''

        # open hyps file
        instream_hyps = open( hyp_file_name )


        hyps = []
        index =0

        #each line in the file represents a hyp comprised of atoms seperated by comma
        for line in instream_hyps :
            split_line = line.split(',')
            hyp = []
            for atom in split_line:
                atom = atom.strip()
                atom = atom.strip('(')
                atom = atom.strip(')')
                hyp.append(atom)

            if index < 2 :
                hyps.append(hyp)
            else:
                raise ValueError('generate_hyps with %s - converter can handle only 2 hyps'%hyp_file_name)

            index = index +1

        instream_hyps.close()
        return hyps

    # get the cost of a together action for an action with non-uniform cost
    def get_action_cost(self, action = None, planning_domain = None, is_discounted = False, is_together= False, epsilon = DEFAULT_EPSILON ):
        if is_discounted:
            discount = epsilon
        else:
            discount = 0

        if is_together:
            agent_count = 2
        else:
            agent_count = 1

        if planning_domain == None:
            return (agent_count*DEFAULT_ACTION_COST -2*discount)

        if planning_domain.actionCosts:
            return action.cost*(agent_count*DEFAULT_ACTION_COST -2*discount)
        else:#arbitrary action cost
           return (agent_count*DEFAULT_ACTION_COST) - 2*discount

    #generate the domain file according to the appropriate conversion method
    def generate_domain_file(self,domain_file_name,destination_folder_name,epsilon, is_poi_grd = False):

        '''
        generates a domain file with actions for agents acting together and separately

        @param domain_file_name: original domain.
        @param destination_folder_name :  the folder in which the new problem is generated
        @param epsilon - the reward/penalty for performing certain actions
        @return: the path to the generated file
        '''

        #parse the domain file using 3rdParty pyperplan_s pddl parser
        predicates_to_duplicate = []
        pddl_parser = parser.Parser( domain_file_name )
        planning_domain = pddl_parser.parse_domain()
        self.static_predicates = get_static_predicates(planning_domain)


        if(planning_domain.actionCosts == True):
            self.isActionCosts = True
            #find all the different action costs in the model (1 is included for the timer)
            for action_name in planning_domain.actions.keys():
                action = planning_domain.actions[action_name]
                if action.cost not in self.actionsCostsList:
                    self.actionsCostsList.append(action.cost)

        #requirements
        requirements_string = ':strips :typing :action-costs  :equality'

        #add agent to types
        planning_domain.types['agent'] = pddl.Type('agent',planning_domain.types['object'])

        #if poi_grd is true add goal to the types
        if is_poi_grd == True:
            planning_domain.types['goal'] = pddl.Type('goal',planning_domain.types['object'])

        #set functions
        functions_string = '(:functions (total-cost) - number)'

        #constants string
        constants_string = self.generate_constants_statement(planning_domain)

        #add agent parameter to all existing predicates
        for predicate_key in planning_domain.predicates.keys():
            predicate = planning_domain.predicates[predicate_key]

            if predicate.name not in self.static_predicates or grd_defs.duplicate_all_predicates:
                self.add_agent_param_to_predicate(predicate)
                predicates_to_duplicate.append(predicate.name)


        #extend the domain predicates according to the specific calculation method
        self.extend_domain_predicates(planning_domain)

        #create the action specific to the calculation method
        new_action_list = self.create_actions_list(planning_domain,epsilon)

        #make the switch
        planning_domain.actions = new_action_list

        split_domain_file_name =  os.path.join(destination_folder_name,self.domain_file_name)

        #generate the resulting domain
        grd_planning_gen.generate_domain_file(planning_domain,split_domain_file_name,requirements_string, functions_string,constants_string)

        return [split_domain_file_name,predicates_to_duplicate]

    def generate_constants_statement(self,planning_domain,generate_closing_bracket = True):

        constants_statment = '(:constants\n agent_0 agent_1 - agent\n'

        for constant in planning_domain.constants.keys():
            constants_statment += '%s - %s\n'%(constant, planning_domain.constants[constant])

        if generate_closing_bracket:
            constants_statment += ')\n'

        return constants_statment


    def generate_together_action(self,action,planning_domain):
        '''
        :param action: action name
        :param predicates: the action predicates
        :param action_cost: the cost of the action
        :return: togehter action
        '''

        together_action_name = '%s_together'%action.name
        together_signature = copy.deepcopy(action.signature)


        # preconditions
        together_precondition = []
        for predicate in action.precondition:

            if predicate.name =='=':

                together_precondition.append(predicate)

            else:

                predicate_0 = pddl.Predicate(copy.deepcopy(predicate.name),copy.deepcopy(predicate.signature),copy.deepcopy(predicate.IsNot))
                predicate_1 = pddl.Predicate(copy.deepcopy(predicate.name),copy.deepcopy(predicate.signature),copy.deepcopy(predicate.IsNot))

                if predicate.name not in self.static_predicates or grd_defs.duplicate_all_predicates:
                    self.add_agent_param_to_predicate(predicate_0,0)
                    self.add_agent_param_to_predicate(predicate_1,1)

                together_precondition.append(predicate_0)
                together_precondition.append(predicate_1)

        together_precondition.append(self.action_predicates[not_split_string])

        #add list
        together_add_list = []
        for predicate in action.effect.addlist:
            #skip the cost predicate which is later added
            if not 'increase' in predicate.name:
                cur_predicate_0 = copy.deepcopy(predicate)
                self.add_agent_param_to_predicate(cur_predicate_0,0)

                cur_predicate_1 = copy.deepcopy(predicate)
                self.add_agent_param_to_predicate(cur_predicate_1,1)

                together_add_list.append(cur_predicate_0)
                together_add_list.append(cur_predicate_1)

        #append cost
        action_cost = self.get_action_cost(action,planning_domain,True,True)
        together_add_list.append(pddl.Predicate(action_cost_predicate_string%action_cost,[]))


        #del list
        together_del_list = []
        for predicate in action.effect.dellist:
            cur_predicate_0 = copy.deepcopy(predicate)
            self.add_agent_param_to_predicate(cur_predicate_0,0)

            cur_predicate_1 = copy.deepcopy(predicate)
            self.add_agent_param_to_predicate(cur_predicate_1,1)

            together_del_list.append(cur_predicate_0)
            together_del_list.append(cur_predicate_1)



        #effect
        together_effect = pddl.Effect()
        together_effect.addlist = together_add_list
        together_effect.dellist = together_del_list
        #create a copy for together
        action_together = pddl.Action(together_action_name, together_signature, together_precondition, together_effect)

        return action_together


    # generate a copy of an action performed seperately by agent agent_num
    def generate_separate_action(self, action, agent_num, planning_domain, indicate_split = True, is_after_split = True, is_discounted = False, add_done_conditions = True, assign_original_cost = True, add_paid_indication = False):


            separate_action_name = '%s_seperate_#%d'%(action.name,agent_num)
            separate_signature = copy.deepcopy(action.signature)

            #precondition
            separate_precondition = []
            for predicate in action.precondition:
                new_predicate = pddl.Predicate(copy.deepcopy(predicate.name),copy.deepcopy(predicate.signature),copy.deepcopy(predicate.IsNot))

                if (predicate.name != '=' and predicate.name not in self.static_predicates) or grd_defs.duplicate_all_predicates:
                    self.add_agent_param_to_predicate(new_predicate,agent_num)

                separate_precondition.append(new_predicate)

            if indicate_split:
                # add split and that agent 0 finished to the preconditions
                #if not is_split add the precondition
                if not is_after_split :
                    separate_precondition.append(self.action_predicates[not_split_string])
                else:
                    separate_precondition.append(self.action_predicates[split_string])

            if add_done_conditions:
                if agent_num == 1 :
                    separate_precondition.append(self.action_predicates[done_0_string])
                else:
                    separate_precondition.append(self.action_predicates[not_done_0_string])



            #add agent to effect and add increase in cost
            separate_add_list = []
            for predicate in action.effect.addlist:
                #skip the cost predicate which is later added
                if not 'increase' in predicate.name:
                    cur_predicate = copy.deepcopy(predicate)
                    self.add_agent_param_to_predicate(cur_predicate,agent_num)
                    separate_add_list.append(cur_predicate)


            separate_del_list = []
            for predicate in action.effect.dellist:
                cur_predicate = copy.deepcopy(predicate)
                self.add_agent_param_to_predicate(cur_predicate,agent_num)
                separate_del_list.append(cur_predicate)


            if assign_original_cost is False and planning_domain.actionCosts:
                action_cost = 0
                
            else:
                action_cost = self.get_action_cost(action, planning_domain, is_discounted, False)




            # append cost
            separate_add_list.append(pddl.Predicate(action_cost_predicate_string%action_cost,[]))

            # add predicates that are specific to the non-uniform cost setting
            if planning_domain.actionCosts and agent_num == 0 and add_paid_indication:
                separate_precondition.append(pddl.Predicate('paid_agent_0',[]))
                separate_del_list.append(pddl.Predicate('paid_agent_0',[]))

            # prepare effect
            separate_effect = pddl.Effect()
            separate_effect.addlist = separate_add_list
            separate_effect.dellist = separate_del_list



            # create the action
            action_separate = pddl.Action(separate_action_name, separate_signature, separate_precondition, separate_effect)

            return action_separate

    def generate_init_state_stmt(self, init_line, instream_template, num_of_hyps, predicates_to_duplicate, gen_closing_bracet = True):
        '''
        :param init_line: the first line - note that for files with action costs  (:metric minimize (total-cost)) is assuemd to appear after the goal statement
        :param instream_template: the template file being parsed
        :param num_of_hyps:
        :param predicates_to_duplicate: predicates to duplicate for agents
        :return:init_to_print
        '''
        #get the entire init statement from the file whose end is indicated by a ')\n'
        init_statement = ''

        #if IPC_GRID
        first_line = init_line.replace('(:init','')
        if('(' in first_line):
            init_statement += first_line

        next_line = instream_template.readline()

        #read all init statement lines up to the goal statement
        while '(:goal' not in next_line :

            if ';' in next_line :
                next_line = instream_template.readline()
                continue

            init_statement = init_statement + next_line
            next_line = instream_template.readline()


        #remove all newlines - giving us a statement with predicates
        init_statement = init_statement.replace('\n','')

        #remove the total cost statement
        init_statement = init_statement.replace(total_cost_statement,'')

        #remove ')'
        init_statement = init_statement.replace(')','')

        init_statement_array = init_statement.split('(')

        #initialize the init to be printed
        init_to_print = ''
        init_to_print += '(:init' + '\n'



        #for pred in init_statement.split('\n') :
        for line in init_statement_array :

            stripped_var =  line.replace(')','')
            stripped_var =  stripped_var.replace('(','')

            #if the line is empty
            stripped_var_no_space = stripped_var.strip()
            if not stripped_var_no_space:
                continue

            #check if the predicate needs to be duplicated
            isStatic = False
            for pred in self.static_predicates:
                if pred.lower() in stripped_var.lower() :
                    isStatic= True

            #only if the predicate is not static add the agent variable to it
            new_split_line = ''
            if isStatic == False or grd_defs.duplicate_all_predicates:
                hyp_index = 0
                while (hyp_index < num_of_hyps) :
                    new_split_line += ('(' +stripped_var.lower() + ' agent_%s)'%(hyp_index))
                    hyp_index+=1
            else:
                new_split_line += ('(' +stripped_var.lower() + ')')

            init_to_print += new_split_line
        init_to_print += '( not ( ' + split_string +' ) )'

        init_to_print = '\n'+ init_to_print + '(= (total-cost) 0)'+'\n'

        if(gen_closing_bracet):
            init_to_print += ')' +'\n'

        return init_to_print


    def generate_goal_stmt(self,hyps, add_metric_and_goal_closing_bracket = False):
        '''
        :param hyps:the pair of hyps
        :return: goal string
        '''
        hyp_index = 0
        goal_statement =  '(:goal \n (and \n'

        for hyp in hyps :
            agent_hyp_string = ''
            for atom in hyp:
                agent_hyp_string = '(%s agent_%d)'%(atom.lower(),hyp_index)
                goal_statement += agent_hyp_string
            hyp_index += 1


        #goal_statement += ')\n'

        if(add_metric_and_goal_closing_bracket):
            goal_statement += ')' + ')\n%s\n'%metric_min_statement

        return goal_statement

    #Used for adding compilation specific objects like the timing mechanims in the timedLatestSplit compilation
    def add_objects(self, line, instream_template):
        object_statement = '\n(:objects'
        return object_statement

#latestSplit (exetended version of the latestSplit compilation from Goal Recognition Design (ICAPS14'))
class grd_converter_latestSplit(grd_converter):

    def __init__(self):

        self.domain_file_name = "latest_split_domain.pddl"
        self.problem_file_name = "latest_split_problem.pddl"
        return



    def extend_domain_predicates(self,planning_domain):
        '''
        Add relevant predicates to the domain definition
        '''

        # add predicates relevant fot all calc_methods
        planning_domain.predicates['split'] = pddl.Predicate('split',[])
        planning_domain.predicates['ag0_done'] = pddl.Predicate('ag0_done',[])

    def generate_goal_stmt(self,hyps, add_metric_and_goal_closing_bracket = False):
        return grd_converter.generate_goal_stmt(self, hyps, True)


#BoundedNATimed (exetended version of the timed-latest-split compilation from Goal Recognition Design for Non-Optimal Agents (AAAI15'))
class grd_converter_timedLatestSplit(grd_converter):

    def __init__(self, optimal_costs, budget_pair):
        print ('optimal_costs')
        print (optimal_costs)
        print ('budget_pair')
        print (budget_pair)

        self.domain_file_name = "timed_split_domain.pddl"
        self.problem_file_name = "timed_split_problem.pddl"
        self.optimal_costs = optimal_costs
        self.budget_pair = budget_pair
        #pre-process the task using the optimal costs to figure out the needed additions to the goal costs
        #this is done in order to artificially unify the costs of all agents
        self.extension_pair = [self.optimal_costs[0] + self.budget_pair[0], self.optimal_costs[1] + self.budget_pair[1]]
        #the different action costs in the domain (1 is assumed to always exist for uniform cost)
        self.actionsCostsList = [1]
        return

    def extend_domain_predicates(self, planning_domain):
        '''
        Add relevant predicates to the domain definition
        '''

        #add time object
        planning_domain.types['time'] = pddl.Type('time',planning_domain.types['object'])


        # add specific predicates
        #(split)
        planning_domain.predicates['split'] = pddl.Predicate('split',[])
        #(ag0_done)
        planning_domain.predicates['ag0_done'] = pddl.Predicate('ag0_done',[])
        #(ag1_done)
        planning_domain.predicates['ag1_done'] = pddl.Predicate('ag1_done',[])
        #(time-of ?a - agent ?t - time)
        planning_domain.predicates['time-of ?a - agent ?t - time'] = pddl.Predicate('time-of ?a - agent ?t - time', [])


        #Add the (next_x ?t1 - time ?t2 - time) predicates
        #if action costs are uniform
        if(planning_domain.actionCosts == False):
            planning_domain.predicates[timer_predicate_string%'1'] = pddl.Predicate(timer_predicate_string%'1', [])
            self.action_predicates[timer_action_predicate_string%'1'] = pddl.Predicate(timer_action_predicate_string%'1', [])

        #non uniform action costs
        else:
            #find the maixmal optimal cost including extentions
            max_value = max(self.optimal_costs[0] + self.budget_pair[0],self.optimal_costs[1] + self.budget_pair[1])

            #find all the different action costs in the model (1 is included for the timer)
            for action_name in planning_domain.actions.keys():
                action = planning_domain.actions[action_name]
                if action.cost not in self.actionsCostsList:
                    self.actionsCostsList.append(action.cost)

            #addd all predicates
            for cost in self.actionsCostsList:
                planning_domain.predicates[timer_predicate_string%cost] = pddl.Predicate(timer_predicate_string%cost, [])
                self.action_predicates[timer_action_predicate_string%cost] = pddl.Predicate(timer_action_predicate_string%cost, [])

    def create_actions_list(self, planning_domain, epsilon,create_together_actions = True , add_exposed = False  ):

        #todo : change these to string constants
        self.action_predicates['time_of_0_t'] = pddl.Predicate('time-of agent_0 ?t',[])
        self.action_predicates['time_of_0_tnext'] = pddl.Predicate('time-of agent_0 ?tnext',[])
        self.action_predicates['time_of_1_t'] = pddl.Predicate('time-of agent_1 ?t',[])
        self.action_predicates['time_of_1_tnext'] = pddl.Predicate('time-of agent_1 ?tnext',[])


        #execute the mehthod of the super class
        new_action_list = grd_converter.create_actions_list(self,planning_domain,epsilon,create_together_actions)
        print(new_action_list)

     
        #add agent_1 done
        signature = []
        precondition = [self.action_predicates['not_ag1_done'],self.action_predicates[split_string]]
        effect = pddl.Effect()
        effect.addlist = [self.action_predicates['ag1_done'],pddl.Predicate(action_cost_predicate_string%0,[])]
        agent_0_done_action =  pddl.Action('agent-1-done', signature , precondition, effect)
        new_action_list['agent-1-done'] = agent_0_done_action


        #add idle actions - with unit cost
        for agent_index in [0,1]:

            #signature
            signature = []
            signature.append (['?t',('time')])
            signature.append (['?tnext',('time')])

            #preconditions
            precondition = []
            precondition.append(self.action_predicates['ag%d_done'%agent_index])
            precondition.append(self.action_predicates['time_of_%d_t'%agent_index])

            #(next ?t ?tnext agent_0)(time-of agent_0 ?t)
            #arbitrary action costs
            if planning_domain.actionCosts == True:
                precondition.append(self.action_predicates[timer_action_predicate_string%'1'])
            else:#uniform
                precondition.append(self.action_predicates[timer_action_predicate_string%'1'])


            #effect
            effect = pddl.Effect()

            #addlist

            #cost
            action_cost = self.get_action_cost()
            effect.addlist=[pddl.Predicate(action_cost_predicate_string%action_cost,[])]
            if add_exposed:
                effect.addlist.append(pddl.Predicate('exposed',[]))

            #(time-of agent_0 ?tnext)
            effect.addlist.append(self.action_predicates['time_of_%d_tnext'%agent_index])


            #dellist
            effect.dellist = [self.action_predicates['time_of_%d_t'%agent_index]]

            agent_idle_wait_action =  pddl.Action('idle-wait-%d'% agent_index, signature , precondition, effect)
            new_action_list['idle-wait-%d'%agent_index] = agent_idle_wait_action



        return new_action_list

    def generate_together_action(self, action,planning_domain):
        '''
        :param action: action name
        :param predicates: the action predicates
        :param action_cost: the cost of the action
        :return: togehter action
        '''

        action_together = grd_converter.generate_together_action(self,action, planning_domain)

        #add timing to signature
        action_together.signature.append (['?t',('time')])
        action_together.signature.append (['?tnext',('time')])

        #add timing to preconditions
        if self.isActionCosts:
            action_together.precondition.append(self.action_predicates[timer_action_predicate_string % action.cost])
        else:
            action_together.precondition.append(self.action_predicates[timer_action_predicate_string % '1'])

        action_together.precondition.append(self.action_predicates['time_of_0_t'])
        action_together.precondition.append(self.action_predicates['time_of_1_t'])

        #add timing to effects
        action_together.effect.addlist.append(self.action_predicates['time_of_0_tnext'])
        action_together.effect.addlist.append(self.action_predicates['time_of_1_tnext'])
        action_together.effect.dellist.append(self.action_predicates['time_of_0_t'])
        action_together.effect.dellist.append(self.action_predicates['time_of_1_t'])

        return action_together

    # generate a copy of an action performed seperately by agent agent_num
    def generate_separate_action(self, action, agent_num, planning_domain, is_after_split = True, is_discounted = False, add_done_conditions = True):


        action_separate = grd_converter.generate_separate_action(self, action, agent_num, planning_domain, True, True, False, add_done_conditions)

        #add timing to signature
        action_separate.signature.append (['?t',('time')])
        action_separate.signature.append (['?tnext',('time')])

        #add timing to preconditions
        if self.isActionCosts:
            action_separate.precondition.append(self.action_predicates[timer_action_predicate_string % action.cost])
        else:
            action_separate.precondition.append(self.action_predicates[timer_action_predicate_string % '1'])

        action_separate.precondition.append(self.action_predicates['time_of_%d_t'%agent_num])


        #add timing to effects
        action_separate.effect.addlist.append(self.action_predicates['time_of_%d_tnext'%agent_num])
        action_separate.effect.dellist.append(self.action_predicates['time_of_%d_t'%agent_num])

        return action_separate

    #generate the hyps of the problem file
    def generate_hyps(self,hyp_file_name):
        hyps = grd_converter.generate_hyps(self,hyp_file_name)
        return hyps


    def generate_goal_stmt(self,hyps,add_metric_and_goal_closing_bracket = True):

        goal_stmt = ''
        goal_stmt += grd_converter.generate_goal_stmt(self, hyps, False)
        goal_stmt += '(time-of agent_0 time%d)'%self.extension_pair[0]
        goal_stmt += '(time-of agent_1 time%d)'%self.extension_pair[1]
        goal_stmt += '(ag0_done)(ag1_done)'

        if add_metric_and_goal_closing_bracket :
            goal_stmt += '))\n%s\n'%metric_min_statement

        return goal_stmt

    def generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate,gen_closing_bracket = True):
        init_stmt = grd_converter.generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate, False)

        # the agents' initial state
        init_stmt += '(time-of agent_0 time0)'
        init_stmt += '(time-of agent_1 time0)'

        #add timing mechanism

        #getting max time to know how many pairs of time points need to be generated
        max_time = max(self.extension_pair)
        if len(self.actionsCostsList) == 1: #uniform cost
            index = 0
            while index <= max_time:
                init_stmt += next_time_string%('1',index, index+1)
                index +=1

        else: #arbitrary cost
            for cost in self.actionsCostsList:
                index = 0
                while index+cost <= max_time:
                    init_stmt += next_time_string%(cost,index,index+cost)
                    index +=1

        if gen_closing_bracket :
            init_stmt += ')' + '\n'

        return init_stmt

    def add_objects(self, line,instream_template):

        objects_statement = '\n%s\n'%line

        next_line = instream_template.readline()
        while (')' not in next_line):
            objects_statement += next_line
            next_line = instream_template.readline()
        if ')' in next_line:
            trimmed_next_line = next_line.replace(')','')
            if any(c.isalpha() for c in trimmed_next_line):
                objects_statement += trimmed_next_line

        #add timer objects
        num_of_timer = max(self.extension_pair)
        index = 0
        while index <= num_of_timer:
            objects_statement += 'time%d\n'%index
            index +=1
        objects_statement += '- time\n'

        return objects_statement


#LatestExpose (exetended version of the latest-expose compilation from Goal Recognition Design With Non-Observable Actions (AAAI16'))
class grd_converter_latestExpose(grd_converter_timedLatestSplit):


    def __init__(self, observability_file_name, are_observables_specified, optimal_costs = None, budget_pair=None):
        '''
        Initializes the converter

        @param observability_file_name : specifying the observable/non-observable actions
        @param are_observables_specified : are the actions specified in observability_file_name observable or non-observable

        '''

        self.budget_pair = None

        if budget_pair:
            self.budget_pair = budget_pair
            grd_converter_timedLatestSplit.__init__(self,optimal_costs,budget_pair)

        if not self.budget_pair:
            self.domain_file_name = "latest_expose_domain.pddl"
            self.problem_file_name = "latest_expose_problem.pddl"
        else:
            self.domain_file_name = "latest_expose_timed_domain.pddl"
            self.problem_file_name = "latest_expose_timed_problem.pddl"

        self.are_observables_specified = are_observables_specified
        self.observability_file_name = observability_file_name
        instream = open(self.observability_file_name)
        self.obs_actions_set = []
        #load action names from observability_file_name file
        for line in instream :
            line = line.strip()
            self.obs_actions_set.append(line)

        return

    def create_actions_list(self, planning_domain, epsilon):
        # optimal agents
        if not self.budget_pair:
            return grd_converter.create_actions_list(self, planning_domain, epsilon)
        else:
            return grd_converter_timedLatestSplit.create_actions_list(self, planning_domain, epsilon)

    def add_objects(self, line,instream_template):

        # optimal agents
        if not self.budget_pair:
            return grd_converter.add_objects(self, line,instream_template)
        else:
            return grd_converter_timedLatestSplit.add_objects(self, line,instream_template)

    def extend_domain_predicates(self, planning_domain):
        '''
        Add relevant predicates to the domain definition
        '''

        if self.budget_pair:
            grd_converter_timedLatestSplit.extend_domain_predicates(self,planning_domain)


        #(split)
        planning_domain.predicates[split_string] = pddl.Predicate(split_string,[])
        #(ag0_done)
        planning_domain.predicates['ag0_done'] = pddl.Predicate('ag0_done',[])


        # Add observability predicates (e.g. (observable_up ?r - robot ?x - tile ?y - tile))
        # We support both non-observable and observable actions specified
        for action_name in planning_domain.actions.keys():

            # get original action
            action = planning_domain.actions[action_name]

            # create relevant predicates (both model and action)
            predicate_name_observable = observability_predicate_string%action_name
            predicate_name_non_observable = non_observability_predicate_string%action_name

            non_obs_action_predicate = pddl.Predicate(predicate_name_non_observable,[])
            obs_action_predicate = pddl.Predicate(predicate_name_observable,[])
            # add params
            for param in action.signature:
                if '-d' not in param[0]: # indicating the param is only because of constraints
                    non_obs_action_predicate.signature.append(param)
                    obs_action_predicate.signature.append(param)

            # create the not(observable_X ) predicate for the grounded action
            param_string = ''
            for param in planning_domain.actions[action_name].signature:
                if '-d' not in param[0]:
                    param_string += param[0]
                    param_string += ' '
            not_obs_action_predicate = pddl.Predicate('not(%s %s)'%(predicate_name_observable,param_string),[])


            # if the non-observable actions are specified (we need the predicate non-observable_unstack ?x - block ?y - block)
            if not self.are_observables_specified:
                # non observable
                planning_domain.predicates[non_observability_predicate_string%action_name] = non_obs_action_predicate
                self.action_predicates[non_observability_predicate_string%action_name] = non_obs_action_predicate

            # observable action are specified (we need the predicate observable_unstack ?x - block ?y - block and not(observable_unstack ?x - block ?y - block))
            else:
                planning_domain.predicates[observability_predicate_string%action_name] = obs_action_predicate
                self.action_predicates[observability_predicate_string%action_name] = obs_action_predicate
                self.action_predicates[not_observable_predicate_string%action_name] = not_obs_action_predicate

    def generate_constants_statement(self,planning_domain, generate_closing_bracket = True):

        # optimal agents
        if not self.budget_pair:
            return grd_converter.generate_constants_statement(self, planning_domain)
        # suboptimal agents
        else:
            return grd_converter_timedLatestSplit.generate_constants_statement(self, planning_domain)

    def generate_together_action(self, action,planning_domain):
        # optimal agents
        if self.budget_pair is None:
            return grd_converter.generate_together_action(self, action, planning_domain)
        # non-optimal agents
        else:
            return grd_converter_timedLatestSplit.generate_together_action(self, action, planning_domain)

    # generate a copy of an action performed seperately by agent agent_num - a copy for observable and non-observable
    def generate_separate_action(self, action, agent_num, planning_domain):


        action_separate_observable = None
        action_separate_non_observable = None
        # optimal agents
        if not self.budget_pair:
            # the flags indicate is_split(for action peformed after split and ) and is_discounted (for discounted actions)
            action_separate_observable = grd_converter.generate_separate_action(self,action,agent_num, planning_domain,True ,True,False)
            # we discount only non observable actions performed by agent 0
            if agent_num == 0:
                action_separate_non_observable = grd_converter.generate_separate_action(self,action,agent_num,planning_domain,True, False,True)
            else:
                action_separate_non_observable = grd_converter.generate_separate_action(self,action,agent_num,planning_domain,True, False,False)
        # suboptimal
        else:
            # the flags indicate is_split(for action peformed after split and ) and is_discounted (for discounted actions)
            action_separate_observable = grd_converter_timedLatestSplit.generate_separate_action(self,action, agent_num,planning_domain,True, True,False)
            # we discount only non observable actions performed by agent 0
            if agent_num == 0:
                action_separate_non_observable = grd_converter_timedLatestSplit.generate_separate_action(self,action,agent_num,planning_domain,True,False,True)
            else:
                action_separate_non_observable = grd_converter_timedLatestSplit.generate_separate_action(self,action,agent_num,planning_domain,True,False,False)



        # if : the observable actions are specified (we need the action precondition to be (not (observable_unstack ?x - block ?y - block)))
        if self.are_observables_specified:

           # observability
            action_separate_non_observable.precondition.append(self.action_predicates[not_observable_predicate_string %action.name])
            action_separate_non_observable.name += '_'+non_observable_string

        # if the non-observable actions are specified (we need the action precondition to be (non-observable_unstack ?x - block ?y - block))
        else:
            # observability
            action_separate_non_observable.precondition.append(self.action_predicates[non_observability_predicate_string %action.name])
            action_separate_non_observable.name += '_'+non_observable_string



        return [action_separate_observable, action_separate_non_observable]

    #generate the hyps of the problem file
    def generate_hyps(self,hyp_file_name):
        hyps = grd_converter.generate_hyps(self,hyp_file_name)
        return hyps

    def generate_goal_stmt(self, hyps, add_metric_and_goal_closing_bracket = True):

        # optimal agents
        if self.budget_pair is None:
            goal_statement = grd_converter.generate_goal_stmt(self,hyps,False)

        # non-optimal agents
        else:
            goal_statement = grd_converter_timedLatestSplit.generate_goal_stmt(self,hyps,False)

        if add_metric_and_goal_closing_bracket :
            goal_statement += '))\n%s\n'%metric_min_statement

        return goal_statement


    def generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate, gen_closing_bracket = False  ):

        # optimal agents (False indicates not generating the closing bracket)
        if not self.budget_pair:
            init_stmt = grd_converter.generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate, False)

        else : #non optimal agents
            init_stmt = grd_converter_timedLatestSplit.generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate,False)

        #add observability info
        for action in self.obs_actions_set:
            stripped_action = action.replace('(','')
            stripped_action = stripped_action.replace(')','')
            if self.are_observables_specified:
                init_stmt += '(observable_%s)'%stripped_action
            else:
                init_stmt += '(non-observable_%s)'%stripped_action


        init_stmt += ')' + '\n'
        return init_stmt


#CommonDeclare (exetended version of the CommonDeclare compilation from Privacy Preserving in Partially Observable Environments (IJCAI16'))
class grd_converter_commmonDeclare(grd_converter_timedLatestSplit):

    def __init__(self, tokens_file_name, optimal_costs = None, budget_pair=None):
        '''
        ןnitializes the converter

        #@param observability_file_name : specifying the observable/non-observable actions
        #@param are_observables_specified : are the actions specified in observability_file_name observable or non-observable
        '''

        self.budget_pair = None

        if budget_pair:
            self.budget_pair = budget_pair
            grd_converter_timedLatestSplit.__init__(self,optimal_costs,budget_pair)

        if not self.budget_pair:
            self.domain_file_name = "common_declare_domain.pddl"
            self.problem_file_name = "common_declare_problem.pddl"
        else:
            self.domain_file_name = "common_declare_timed_domain.pddl"
            self.problem_file_name = "common_declare_timed_problem.pddl"

        # observability
        self.tokens_file_name = tokens_file_name
        instream = open(self.tokens_file_name)
        self.obs_tokens_assignmeset_set = []
        self.action_tokens_list = []

        # load token assignment from action token file
        for line in instream:
            line = line.replace('(','')
            line = line.replace(')','')
            line = line.strip()
            action_token_entry = line.split()
            self.obs_tokens_assignmeset_set.append(action_token_entry)
            cur_token = action_token_entry[1]
            if not cur_token in self.action_tokens_list:
                self.action_tokens_list.append(cur_token)
        return

    #generate the hyps of the problem file
    def generate_hyps(self,hyp_file_name):
        hyps = grd_converter.generate_hyps(self,hyp_file_name)
        return hyps

    def generate_goal_stmt(self, hyps, add_metric_and_goal_closing_bracket = True):
        # optimal agents
        if self.budget_pair is None:
            goal_statement = grd_converter.generate_goal_stmt(self,hyps,False)

        # non-optimal agents
        else:
            goal_statement = grd_converter_timedLatestSplit.generate_goal_stmt(self,hyps,False)

        goal_statement += '( ' + pending_token_declared_predicate_string + ' agent_0 )'
        goal_statement += '('  + pending_token_declared_predicate_string + ' agent_1 )'

        # ADDED TO SUPPORT COST DECLARATION
        if self.planning_domain.actionCosts:
            goal_statement += '(paid_agent_0)'

        if add_metric_and_goal_closing_bracket :
            goal_statement += '))\n%s\n'%metric_min_statement

        return goal_statement

    def generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate, generate_closing_bracket = False):
        # optimal agents (False indicates not generating the closing bracket)
        if not self.budget_pair:
            init_stmt = grd_converter.generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate, False)

        else : #non optimal agents
            init_stmt = grd_converter_timedLatestSplit.generate_init_state_stmt(self,init_line,instream_template,num_of_hyps,predicates_to_duplicate,False)


        #add observability info
        for token_assginment in self.obs_tokens_assignmeset_set:
            token_assignment_predicate = '('

            #include the nil token assignment for the entire set of (non-grounded) actions

            if len(token_assginment) == 2 and grd_defs.NIL_STRING.lower() in token_assginment[1].lower():
                #token_assignment_predicate += '(%s AN-%s)'%(predicate_name_tokens_nil,token_assginment[0].upper())
                token_assignment_predicate += action_token_assignment_string%0
                token_assignment_predicate += " "
                token_assignment_predicate += "AN-"+(token_assginment[0]).upper() +' '
                #action token - NIL
                token_assignment_predicate+= ' AT_NIL '


            #grounded action token
            else:

                #get param num
                num_of_params = len(token_assginment)-2
                #update the predicate name with the number of params
                token_assignment_predicate += action_token_assignment_string%num_of_params

                token_assignment_predicate += " "
                token_assignment_predicate += "AN-"+(token_assginment[0]).upper() +' '

                #action token
                token_assignment_predicate+= token_assginment[1]+" "

                param_count = 0
                while param_count<num_of_params:
                    token_assignment_predicate += '%s'%token_assginment[2+param_count]
                    token_assignment_predicate += " "
                    param_count += 1

            token_assignment_predicate += (')')



            init_stmt += token_assignment_predicate
            init_stmt += '\n'

        #agents start with token declared
        init_stmt += '( ' + pending_token_declared_predicate_string + ' agent_0 )'
        init_stmt += '('  + pending_token_declared_predicate_string + ' agent_1 )'
        init_stmt += '(not-exposed)'

        # ADDED TO SUPPORT COST DECLARATION
        if self.planning_domain.actionCosts:
            init_stmt += '(paid_agent_0)'


        init_stmt += ')' + '\n'
        return init_stmt

    def extend_domain_predicates(self, planning_domain):
        '''
        Add relevant predicates to the domain definition
        '''


        if self.budget_pair:
            grd_converter_timedLatestSplit.extend_domain_predicates(self,planning_domain)

        #add token object
        planning_domain.types['obs_tok'] = pddl.Type('obs_tok',planning_domain.types['object'])
        planning_domain.types['act_tok'] = pddl.Type('act_tok',planning_domain.types['obs_tok'])
        planning_domain.types['action_name'] = pddl.Type('action_name',planning_domain.types['object'])

        #(exposed)
        planning_domain.predicates['exposed'] = pddl.Predicate('exposed',[])
        planning_domain.predicates['not-exposed'] = pddl.Predicate('not-exposed',[])
        #(ag0_done)
        planning_domain.predicates['ag0_done'] = pddl.Predicate('ag0_done',[])

        #(pending_token_declared)
        pending_token_predicate = pddl.Predicate(pending_token_declared_predicate_string,[])
        pending_token_predicate.signature.append(['?agent',('agent')])
        planning_domain.predicates[pending_token_declared_predicate_string] = pending_token_predicate
        self.action_predicates[pending_token_declared_predicate_string] = pending_token_predicate


        #(token_emitted_string)
        emitted_token_predicate = pddl.Predicate(token_emitted_string,[])
        emitted_token_predicate.signature.append(['?agent',('agent')])
        emitted_token_predicate.signature.append(['?tok',('act_tok')])
        planning_domain.predicates[token_emitted_string] = emitted_token_predicate
        self.action_predicates[token_emitted_string] = emitted_token_predicate

        # ADDED TO SUPPORT COST DECLARATION
        # non-uniform action costs
        if planning_domain.actionCosts:
            #token cost for agent 0
            for action_cost in self.actionsCostsList:
                predicate_name = 'cost_agent_0_%d'%action_cost
                cost_predicate_0 = pddl.Predicate(predicate_name,[])
                planning_domain.predicates[predicate_name] = cost_predicate_0
                self.action_predicates[predicate_name] = cost_predicate_0

            predicate_name = 'discounted_agent_0'
            discounted_predicate_0 = pddl.Predicate(predicate_name,[])
            planning_domain.predicates[predicate_name] = discounted_predicate_0
            self.action_predicates[predicate_name] = discounted_predicate_0

            predicate_name = 'not_discounted_agent_0'
            non_discounted_predicate_0 = pddl.Predicate(predicate_name,[])
            planning_domain.predicates[predicate_name] = non_discounted_predicate_0
            self.action_predicates[predicate_name] = non_discounted_predicate_0

            predicate_name = 'paid_agent_0'
            paid_predicate_0 = pddl.Predicate(predicate_name,[])
            planning_domain.predicates[predicate_name] = paid_predicate_0
            self.action_predicates[predicate_name] = paid_predicate_0



        # token assigned to un-grounded action
        predicate_name_tokens_ungrounded = action_token_assignment_string%'0'
        action_token_predicate_ungrounded = pddl.Predicate(predicate_name_tokens_ungrounded,[])
        action_token_predicate_ungrounded.signature.append(['?act_name',('action_name')])
        action_token_predicate_ungrounded.signature.append(['?act_tok',('act_tok')])

        # add predicate
        planning_domain.predicates[predicate_name_tokens_ungrounded] = action_token_predicate_ungrounded
        self.action_predicates[predicate_name_tokens_ungrounded] = action_token_predicate_ungrounded

        # count the number of params in each action and crate a list of different options
        params_count_list = []
        for action_name in planning_domain.actions.keys():

            # get original action
            action = planning_domain.actions[action_name]

            #number of params
            param_count = len(action.signature)

            if param_count not in params_count_list:
                params_count_list.append(param_count)

        # add params to signature
        for param_count in range(0,max(params_count_list)+1):

            predicate_name_tokens = action_token_assignment_string%param_count
            action_token_predicate = pddl.Predicate(predicate_name_tokens,[])
            action_token_predicate.signature.append(['?act_name',('action_name')])
            action_token_predicate.signature.append(['?act_tok',('act_tok')])

            # add params
            index = 1
            while index <= param_count:
                action_token_predicate.signature.append(['?obj_%d'%index,('object')])
                index += 1

            # add predicate
            planning_domain.predicates[predicate_name_tokens] = action_token_predicate
            self.action_predicates[predicate_name_tokens] = action_token_predicate
    # declare pending token
    def add_declare_actions(self, new_action_list):

        # DECLARE_ACTION_TOKEN_SEPARATE
        for agent_index in [0, 1]:

            # signature
            signature = []
            signature.append (['?tok',('act_tok')])

            #preconditions
            precondition = []
            emitted_token_predicate = pddl.Predicate(token_emitted_string,[])
            emitted_token_predicate.signature.append(['agent_%d'%agent_index])
            emitted_token_predicate.signature.append(['?tok',('act_tok')])

            precondition.append(emitted_token_predicate)


            #effect
            effect = pddl.Effect()
            effect.addlist = []
            effect.dellist = []

            # no pending token
            effect.addlist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_index),[]))
            effect.addlist.append(pddl.Predicate('exposed',[]))

            # ADDED TO SUPPORT COST DECLARATION
            if self.planning_domain.actionCosts is False:
                effect.addlist.append(pddl.Predicate(action_cost_predicate_string%(DEFAULT_EPSILON),[]))
            else:
                effect.addlist.append(pddl.Predicate(action_cost_predicate_string%(0),[]))

            effect.dellist.append(emitted_token_predicate)
            effect.dellist.append(pddl.Predicate('not-exposed',[]))

            action_name = 'declare_action_token_#%d'%(agent_index)
            agent_declare_action = pddl.Action(action_name, signature, precondition, effect)
            new_action_list[action_name] = agent_declare_action


            #DECLARE_ACTION_TOKEN_TOGETHER
            #signature
            signature = []
            signature.append (['?tok',('act_tok')])

            #preconditions
            precondition = []
            precondition.append(pddl.Predicate('not-exposed',[]))

            emitted_token_predicate_0 = pddl.Predicate(token_emitted_string,[])
            emitted_token_predicate_0.signature.append(['agent_0'])
            emitted_token_predicate_0.signature.append(['?tok',('act_tok')])

            precondition.append(emitted_token_predicate_0)

            emitted_token_predicate_1 = pddl.Predicate(token_emitted_string,[])
            emitted_token_predicate_1.signature.append(['agent_1'])
            emitted_token_predicate_1.signature.append(['?tok',('act_tok')])

            precondition.append(emitted_token_predicate_1)


            #effect
            effect = pddl.Effect()
            effect.addlist = []
            effect.dellist = []

            #addlist
            effect.addlist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, 0),[]))
            effect.addlist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, 1),[]))
            effect.addlist.append(pddl.Predicate(action_cost_predicate_string%(0),[]))

            #dellist
            effect.dellist.append(emitted_token_predicate_0)
            effect.dellist.append(emitted_token_predicate_1)

            # ADDED TO SUPPORT COST DECLARATION
            # the penalty is discounted according to the action cost of agent 0
            if self.planning_domain.actionCosts:
                effect.addlist.append(pddl.Predicate('discounted_agent_0',[]))
                effect.dellist.append(pddl.Predicate('not_discounted_agent_0',[]))

            action_name = 'declare_action_token_together'
            agent_declare_action =  pddl.Action(action_name, signature , precondition, effect)
            new_action_list[action_name] = agent_declare_action

            #(:action DECLARE_ACTION_TOKEN_NIL
            signature = []


            precondition = [pddl.Predicate('not-exposed',[])]
            emitted_token_predicate_0 = pddl.Predicate(token_emitted_string,[])
            emitted_token_predicate_0.signature.append(['agent_0'])
            emitted_token_predicate_0.signature.append(['AT_NIL'])
            precondition.append(emitted_token_predicate_0)

            effect = pddl.Effect()
            effect.addlist = []
            effect.dellist = []

            effect.addlist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, 0),[]))
            effect.addlist.append(pddl.Predicate(action_cost_predicate_string%(0),[]))


            #dellist
            effect.dellist.append(emitted_token_predicate_0)


            action_name = 'declare_action_token_nil_agent_0'
            declare_NIL_action = pddl.Action(action_name, signature, precondition, effect)
            new_action_list[action_name] = declare_NIL_action

    def add_pay_actions(self,new_action_list,epsilon=DEFAULT_EPSILON):

        #if the domain has non-uniform action costs we add a seperate declare action for each cost
        cost_list = []
        for action_name in self.planning_domain.actions:
            cost_list.append(self.planning_domain.actions[action_name].cost)

        for cost in cost_list:
            factored_cost = DEFAULT_ACTION_COST*cost
            # create non-discounted version
            cost_predicate_name = 'cost_agent_0_%d'%(cost)
            # create non-discounted version
            signature = []
            precondition = [pddl.Predicate('not_discounted_agent_0',[]),pddl.Predicate('cost_agent_0_%d'%cost,[])]
            effect = pddl.Effect()
            #cost
            effect.addlist = [pddl.Predicate('paid_agent_0',[]),pddl.Predicate(action_cost_predicate_string%(factored_cost),[])]
            effect.dellist = [pddl.Predicate('cost_agent_0_%d'%cost,[])]
            pay_non_discounted_action = pddl.Action('pay-0-non-discounted-%d'%cost, signature ,precondition, effect)
            new_action_list['pay-0-non-discounted-%d'%cost] = pay_non_discounted_action
            # create discounted version
            signature = []
            precondition = [pddl.Predicate('discounted_agent_0',[]),pddl.Predicate('cost_agent_0_%d'%cost,[])]
            effect = pddl.Effect()
            effect.addlist = [pddl.Predicate('paid_agent_0',[]),pddl.Predicate(action_cost_predicate_string%(factored_cost*(1-0.009)),[]), pddl.Predicate('not_discounted_agent_0',[])]
            #cost
            effect.dellist = [pddl.Predicate('cost_agent_0_%d'%cost,[]),pddl.Predicate('discounted_agent_0',[])]
            pay_discounted_action = pddl.Action('pay-0-discounted-%d'%cost, signature ,precondition, effect)
            new_action_list['pay-0-discounted-%d'%cost] = pay_discounted_action

    def create_actions_list(self, planning_domain, epsilon):


        #execute the method of the super class (without creating together actions)
        # optimal agents
        if not self.budget_pair:
            new_action_list = grd_converter.create_actions_list(self, planning_domain, epsilon,False, False, False)
        # non optimal agents
        else:
            new_action_list = grd_converter_timedLatestSplit.create_actions_list(self, planning_domain, epsilon,False,True)

        self.add_declare_actions(new_action_list)

        # ADDED TO SUPPORT COST DECLARATION
        # non-uniform action costs
        if self.planning_domain.actionCosts is True:
            self.add_pay_actions(new_action_list,epsilon)


        return new_action_list

    def generate_constants_statement(self,planning_domain, generate_closing_bracket = True):
        constants_string = ''
        # optimal agents
        if not self.budget_pair:
            constants_string =  grd_converter.generate_constants_statement(self, planning_domain, False)
        # suboptimal agents
        else:
            constants_string =  grd_converter_timedLatestSplit.generate_constants_statement(self, planning_domain, False)


        constants_string += 'AT_NIL - act_tok \n' #'(:constants\n agent_0 agent_1 - agent\n AT_NIL - act_tok \n'
        action_names_string = ''
        for action in planning_domain.actions:
            action_names_string += "AN-"+action.upper() +' '
        action_names_string += ' - action_name\n'

        # add constants indicating action cost
        if(planning_domain.actionCosts == True):
            for cost in self.actionsCostsList:
                constants_string += 'cost-%d '%cost
            constants_string += '- object\n'


        if generate_closing_bracket :
            constants_string += action_names_string + '\n)\n'
        return constants_string

    def add_objects(self, line, instream_template):


        # optimal agents
        if self.budget_pair is None:
            objects_statement =  grd_converter.add_objects(self, line,instream_template)
        # suboptimal agents
        else:
            objects_statement =  grd_converter_timedLatestSplit.add_objects(self, line,instream_template)

        objects_statement = objects_statement.replace('\n)','')

        objects_statement += '\n'

        print(objects_statement)

        #add token objects
        for token in self.action_tokens_list:
            if grd_defs.NIL_STRING.lower() not in token.lower():
                objects_statement += token
                objects_statement += ' \n'
        objects_statement += '\n- act_tok'


       # if not self.budget_pair is None or self.action_tokens_list != [] :
       #     objects_statement += ')'

        print(objects_statement)
        return objects_statement

    # generate a copy of an action performed seperately by agent agent_num
    # for simplicity we create a special action that emits the nil token - this allows to assign the nil token to an action rather then a grounded action
    # the isZeroParams flag indicates if params needs to be considered in token assignment - or there is a uniform assignmnet for grounded actions
    def generate_separate_action_old(self, action, agent_num, planning_domain, isZeroParams = False):

        # optimal agents
        if not self.budget_pair:
            # generate separate
            action_separate = grd_converter.generate_separate_action(self,action, agent_num, planning_domain, False, False, False, False )
            action_separate.signature.append (['?tok',('act_tok')])

            # generate a sperate action that emits not token
            action_seperate_nil_token = grd_converter.generate_separate_action(self,action, agent_num, planning_domain, False, False, False, False)
            action_seperate_nil_token.name += '_%s'%grd_defs.NIL_STRING

             # generate a sperate action that emits not token
            action_seperate_nil_token_params = grd_converter.generate_separate_action(self,action, agent_num, planning_domain, False, False, False, False)
            action_seperate_nil_token_params.name += '_params_%s'%grd_defs.NIL_STRING

        # suboptimal
        else:
            #generate separate
            action_separate = super(grd_converter_timedLatestSplit, self).generate_separate_action(action, agent_num, planning_domain, False, False, False, False)
            action_separate.signature.append (['?tok',('act_tok')])



            #generate a sperate action that emits no token for all actions from this type (ungrounded)
            action_seperate_nil_token = super(grd_converter_timedLatestSplit, self).generate_separate_action( action, agent_num, planning_domain, False, False, False, False)
            action_seperate_nil_token.name += '_%s'%grd_defs.NIL_STRING

            #generate a sperate action that emits no token (grounded)
            action_seperate_nil_token_params = super(grd_converter_timedLatestSplit, self).generate_separate_action( action, agent_num, planning_domain, False, False, False, False)
            action_seperate_nil_token_params.name += '_parames_%s'%grd_defs.NIL_STRING

        #number of params
        if isZeroParams:
            param_count = 0

        else:
            param_count = len(action.signature)
            action_name = "AN-"+action.name.upper()
            param_index = 0
            params_string = ''
            for param in action.signature:
                if param_index < param_count:
                    params_string =  params_string  +" " + param[0] + " "
                param_index += 1

        # OBSERVABILITY

        # regular action
        # token to emit
        action_token_string = 'action_token_ParamsNum_%s %s %s %s'%(param_count,action_name,'?tok',params_string)
        action_token_predicate = pddl.Predicate(action_token_string,[])
        action_separate.precondition.append(action_token_predicate)
        # no pending token
        action_separate.precondition.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))
        # emitted token
        emitted_token_predicate = pddl.Predicate(token_emitted_string,[])
        emitted_token_predicate.signature.append(['agent_%d'%agent_num])
        emitted_token_predicate.signature.append(['?tok',('act_tok')])
        action_separate.effect.addlist.append(emitted_token_predicate)
        # need to declare token
        action_separate.effect.dellist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))


        # ADDED TO SUPPORT COST DECLARATION
        #if the domain is non-uniforme cost and the agent is agent_0 - he needs to account for the cost of the action
        if planning_domain.actionCosts  and agent_num ==0:
            cost_predicate_name = 'cost_agent_0_%d'%(action.cost)
            emitted_token_cost_predicate = pddl.Predicate(cost_predicate_name,[])
            action_separate.effect.addlist.append(emitted_token_cost_predicate)

        # nil token action ( the nil token does not require any declaration)
        action_token_string_nil = 'action_token_ParamsNum_%s %s %s'%(0,action_name,'AT_NIL')
        action_token_predicate_nil = pddl.Predicate(action_token_string_nil,[])
        action_seperate_nil_token.precondition.append(action_token_predicate_nil)

        # no pending token
        action_seperate_nil_token.precondition.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))


        # nil token action ( the nil token does not require any declaration)
        action_token_string_nil_params = 'action_token_ParamsNum_%s %s %s %s'%(param_count,action_name,'AT_NIL',params_string)
        action_token_predicate_nil_params = pddl.Predicate(action_token_string_nil_params,[])
        action_seperate_nil_token_params.precondition.append(action_token_predicate_nil_params)

        # no pending token
        action_seperate_nil_token_params.precondition.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))

        return [action_separate, action_seperate_nil_token,action_seperate_nil_token_params]

    # generate a copy of an action performed seperately by agent agent_num
    # for simplicity we create a special action that emits the nil token - this allows to assign the nil token to an action rather then a grounded action
    # the isZeroParams flag indicates if params needs to be considered in token assignment - or there is a uniform assignmnet for grounded actions
    def generate_separate_action(self, action, agent_num, planning_domain, isZeroParams = False):

        # optimal agents
        if not self.budget_pair:

            # generate separate
            if agent_num == 0: # don;t assign regular cost (zero cost)
                action_separate = grd_converter.generate_separate_action(self,action, agent_num, planning_domain, False, False, False, False, False, True )
                action_separate.signature.append (['?tok',('act_tok')])
            else: # assign regular cost
                action_separate = grd_converter.generate_separate_action(self,action, agent_num, planning_domain, False, False, False, False , True)
                action_separate.signature.append (['?tok',('act_tok')])

        # suboptimal
        else:
            #generate separate
            action_separate = super(grd_converter_timedLatestSplit, self).generate_separate_action(action, agent_num, planning_domain, False, False, False, False)
            action_separate.signature.append (['?tok',('act_tok')])

            # add timer mechanism
            action_separate.signature.append (['?t',('time')])
            action_separate.signature.append (['?tnext',('time')])
            action_separate.precondition.append(self.action_predicates['time_of_%d_t'%agent_num])
            #(next_ ?t ?tnext )
            action_separate.precondition.append(pddl.Predicate(timer_action_predicate_string%'1',[]))

             #(time-of agent_0 ?tnext)
            action_separate.effect.addlist.append(self.action_predicates['time_of_%d_tnext'%agent_num])
            #dellist
            action_separate.effect.dellist.append(self.action_predicates['time_of_%d_t'%agent_num])





        #number of params
        if isZeroParams:
            param_count = 0

        else:
            param_count = 0
            for param in action.signature:
                if '-d' not in param[0]: # indicating the param is only because of constraints
                    param_count+=1

            action_name = "AN-"+action.name.upper()
            param_index = 0
            params_string = ''
            for param in action.signature:
                if param_index < param_count:
                    params_string =  params_string  +" " + param[0] + " "
                param_index += 1

        # OBSERVABILITY

        # regular action
        # token to emit
        action_token_string = 'action_token_ParamsNum_%s %s %s %s'%(param_count,action_name,'?tok',params_string)
        action_token_predicate = pddl.Predicate(action_token_string,[])
        action_separate.precondition.append(action_token_predicate)
        # no pending token
        action_separate.precondition.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))
        # emitted token
        emitted_token_predicate = pddl.Predicate(token_emitted_string,[])
        emitted_token_predicate.signature.append(['agent_%d'%agent_num])
        emitted_token_predicate.signature.append(['?tok',('act_tok')])
        action_separate.effect.addlist.append(emitted_token_predicate)
        # need to declare token
        action_separate.effect.dellist.append(pddl.Predicate('%s agent_%s'%(pending_token_declared_predicate_string, agent_num),[]))


        # ADDED TO SUPPORT COST DECLARATION
        #if the domain is non-uniforme cost and the agent is agent_0 - he needs to account for the cost of the action
        if planning_domain.actionCosts  and agent_num ==0:
            cost_predicate_name = 'cost_agent_0_%d'%(action.cost)
            emitted_token_cost_predicate = pddl.Predicate(cost_predicate_name,[])
            action_separate.effect.addlist.append(emitted_token_cost_predicate)


        return [action_separate]


# Extracts the static predicates of the domain using the pyperplan domain
# A static predicate is a predicate which doesn't occur in an effect of an action.
def get_static_predicates(domain):

    actions = domain.actions.values()
    predicates = domain.predicates.values()


    def get_effects(action):
        return action.effect.addlist | action.effect.dellist

    effects = [get_effects(action) for action in actions]
    effects = set(itertools.chain(*effects))

    def static(predicate):
        return not any(predicate.name == eff.name for eff in effects)

    statics = [pred.name for pred in predicates if static(pred)]
    return statics


def convert_grd_to_planning():

    import sys
    calc_method = sys.argv[1]
    domain_file_name = sys.argv[2]
    template_file_name = sys.argv[3]
    hyps_file_name = sys.argv[4]
    destination_folder_name = grd_defs.gen_files_dir

    if grd_defs.LatestSplit == calc_method:

        grdConverter = grd_converter_latestSplit()
        grdConverter.grd_to_split(domain_file_name,template_file_name,hyps_file_name,destination_folder_name)
        return

    elif grd_defs.LatestTimed == calc_method:

        import grd_evaluator
        import grd_task

        #initialize the grd task
        grd_test_task = grd_task.GrdTask()
        grd_test_task.initialize_with_files(grd_defs.gen_files_dir,domain_file_name,template_file_name,hyps_file_name)
        budget_array_string = sys.argv[5]
        if grd_test_task.actionCosts and budget_array_string != grd_defs.NA :
            print("Non optimal agents supported only for uniform action costs. Exiting"%calc_method)
            return

        #parse the budget array
        grd_test_task.set_sub_optimal_bound_array(sys.argv[5])

        #get optimal costs
        optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]


        grdConverter = grd_converter_timedLatestSplit(optimal_costs, grd_test_task.get_sub_optimal_bound_array())
        grdConverter.grd_to_split(domain_file_name, template_file_name, hyps_file_name, destination_folder_name)
        return

    elif grd_defs.LatestExpose == calc_method:

        import grd_evaluator
        import grd_task

        budget_array_string = sys.argv[5]
        observability_file_name = sys.argv[6]

        # if the destination folder has been specified - create the files there - otherwise use grd_defs.gen_files_dir
        if len(sys.argv) > 7:
            destination_folder_name = sys.argv[7]

        grd_test_task = grd_task.GrdTask()
        grd_test_task.initialize_with_files(destination_folder_name,domain_file_name,template_file_name,hyps_file_name,observability_file_name)

        optimal_costs = None
        if grd_defs.NA not in budget_array_string:
            #parse the budget array
            grd_test_task.set_budget_array(sys.argv[5])

            #get optimal costs
            optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]


        if grd_test_task.actionCosts and budget_array_string != grd_defs.NA :
            print("Non optimal agents supported only for uniform action costs. Exiting")
            return

        #activate the conversion with grd_task.are_observables_specified indicating if non observable or observable actions were specified
        grdConverter = grd_converter_latestExpose(observability_file_name, grd_test_task.are_observables_specified,optimal_costs, grd_test_task.get_sub_optimal_bound_array())
        grdConverter.grd_to_split(domain_file_name, template_file_name, hyps_file_name, destination_folder_name )
        return

    elif grd_defs.CommonDeclare == calc_method:

        import grd_evaluator
        import grd_task

        budget_array_string = sys.argv[5]
        observability_file_name = sys.argv[6]

        # if the destination folder has been specified - create the files there - otherwise use grd_defs.gen_files_dir
        if len(sys.argv) > 7:
            destination_folder_name = sys.argv[7]


        print("desitnation folder name")
        print(destination_folder_name)


        grd_test_task = grd_task.GrdTask()
        grd_test_task.initialize_with_files(destination_folder_name,domain_file_name,template_file_name,hyps_file_name,observability_file_name)

        if grd_test_task.actionCosts and budget_array_string != grd_defs.NA :
            print("Non optimal agents supported only for uniform action costs. Exiting")
            return

        optimal_costs = None
        if grd_defs.NA not in budget_array_string:
            #parse the budget array
            grd_test_task.set_sub_optimal_bound_array(sys.argv[5])

            #get optimal costs
            optimal_costs = grd_utils.check_optimal_costs(grd_test_task)[0]

        #activate the conversion
        grdConverter = grd_converter_commmonDeclare(observability_file_name,optimal_costs, grd_test_task.get_sub_optimal_bound_array())
        grdConverter.grd_to_split(domain_file_name, template_file_name, hyps_file_name, destination_folder_name )
        return

    else:
        print("Calc method %s not supported. Exiting"%calc_method)


if __name__ == '__main__' :


    import grd_utils
    grd_utils.empty_or_create_log_and_gen_dir()

    convert_grd_to_planning()
