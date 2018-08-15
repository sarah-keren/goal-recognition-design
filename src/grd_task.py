__author__ = 'sarah'



import grd_utils,grd_planning_gen,grd_defs
import os
from pddl import parser
import grounding

class GrdTask :
    """
    Representing a grd problem.
    Supports all types of grd models : optimal, sub-optimal, partially observable and action tokens
    """

    def __init__(self):

        #folder to create corresponding files
        self.destination_folder_name = None

        #name
        self.task_name = None

        #costs
        self.optimal_costs = None

        #domain file name
        self.domain_file_name = None
        self.full_domain_file_name = None

        #template file name
        self.template_file_name = None
        self.full_template_file_name = None

        #hyps file name
        self.hyps_file_name = None
        self.full_hyps_file_name = None
        self.hyps_set = []

        #corresponding planning task (used in BFS search)
        self.planningTaskForExploration = None

        #static predicates
        self.static_predicates = []

        #parsed via 3rd party - pyperplan
        self.parsed_pddl_domain = None

        #observability file and list
        self.observability_file_name = None
        self.observability_actions_list = None
        self.observability_actions_list_string = None
        self.non_observability_actions_list = None
        self.non_observability_actions_list_string = None
        self.observability_file_name = None
        self.are_observables_specified = False

        #action token file andlist
        self.action_tokens_file_name = None
        self.action_tokens_list = None
        self.action_tokens_list_string = None
        self.full_action_tokens_file_name = None


        #poi_hyps file and list
        self.poi_hyps_file_name = None
        self.poi_hyps_list = None
        self.poi_hyps_list_string = None
        self.full_poi_hyps_file_name = None

        #diversion budget array
        self.bound_array = None

        #design budget array
        self.design_budget_array = None

        #benchnmark domain name
        self.domain_name = grd_defs.NA


	
    def initialize_with_tarred_folder(self,destination_folder_name,tarred_folder, delete_ex_folder = True, max_hyps_num = grd_defs.INFINITE, domain_name= grd_defs.NA):
        '''
        :param destination_folder_name: place to extract files
        :param tarred_folder: tar.bz2 tarred folder containing all files
        :return: NA
        '''

        #extract files
        cmd = 'tar jxf %s -C %s'%(tarred_folder,destination_folder_name)
        os.system(cmd)

        #according to the folder created (if the tar creates a folder or not)
        from os.path import basename
        # now you can call it directly with basename
        task_name =  (basename(tarred_folder).split('.'))[0]
        self.task_name = task_name
        folder_task_name = os.path.join(destination_folder_name,task_name)
        if os.path.exists(folder_task_name):
            destination_folder_name = folder_task_name

        # if the number of hyps is limited - select the fitst max_hyps_num hyps from the hyps file
        if max_hyps_num != grd_defs.INFINITE:
            temp_file_name = 'temp_hyps.dat'
            intstream = open(os.path.join(folder_task_name,'hyps.dat'))
            with open(os.path.join(folder_task_name,temp_file_name), 'w') as outstream:
                index = 0
                for line in intstream.readlines():
                    if index < max_hyps_num:
                        outstream.write(line)
                        index += 1
            # delete original file and replace with new one
            os.remove(os.path.join(folder_task_name,'hyps.dat'))
            os.rename(os.path.join(folder_task_name,temp_file_name),os.path.join(folder_task_name,'hyps.dat'))



        # only if the non-obs file exists include it in the parameters
        observability_file_name = None
        if os.path.isfile(os.path.join(folder_task_name,'non-obs.dat')):
            observability_file_name = 'non-obs.dat'

        if os.path.isfile(os.path.join(folder_task_name,'comp-non-obs.dat')):
            observability_file_name = 'comp-non-obs.dat'

        if os.path.isfile(os.path.join(folder_task_name,'obs.dat')):
            observability_file_name = 'obs.dat'

        # only if the action_token file exists include it in the parameters
        action_token_file_name = None
        if os.path.isfile(os.path.join(folder_task_name,grd_defs.action_token_file_name)):
            action_token_file_name = 'act-toks.dat'


        # only if the poi_hyps file exists include it in the parameters
        poi_hyps_file_name = None
        if os.path.isfile(os.path.join(folder_task_name,'poi_hyps.dat')):
            action_token_file_name = 'poi_hyps.dat'


        self.initialize_with_files(destination_folder_name,'domain.pddl','template.pddl','hyps.dat',observability_file_name, action_token_file_name,poi_hyps_file_name, task_name, None, domain_name )


        # delete folder
        if delete_ex_folder:
            cmd = 'rm -r %s ' % (folder_task_name)
            os.system(cmd)

        return folder_task_name


    def initialize_with_files(self, destination_folder_name, domain_file, template_file, hyps_file_name, observability_file_name = None, action_token_file_name = None, poi_hyps_file = None, task_name=None, reciprocal_observability_file_name = None, domain_name = grd_defs.NA):
        '''
        Same as above with files specified instead of tarred folder - initialization includes processing the files and collecting grd relevant information
        :param destination_folder_name:
        :param domain_file:
        :param template_file:
        :param hyps_file_name:
        :param task_name:
        :param observability_file_name: if relevant
        :param action_token_file_name: if relevant
        :return: NA
        '''


        #only if the name has not ben initialized previously
        if task_name == None:
            self.task_name = destination_folder_name.split('/')[-1]
        else:
            self.task_name = task_name

        #assign the relevant file names
        self.destination_folder_name = destination_folder_name
        self.domain_file_name = domain_file
        self.full_domain_file_name = os.path.abspath(os.path.join(destination_folder_name,self.domain_file_name))
        self.template_file_name = template_file
        self.full_template_file_name = os.path.abspath(os.path.join(destination_folder_name,self.template_file_name))
        self.hyps_file_name = hyps_file_name
        self.full_hyps_file_name = os.path.abspath(os.path.join(destination_folder_name,self.hyps_file_name))

        # the benchmark domain (easy-gird etc)
        self.domain_name = grd_utils.get_domain_name(self)


        #load hyps(possible goals) set from hyps.dat file
        self.load_hypotheses(self.full_hyps_file_name)

        #parse the domain file
        pddl_parser = parser.Parser(self.full_domain_file_name)
        self.parsed_pddl_domain = pddl_parser.parse_domain()

        #add a flag indicating if actions costs are specified in the original domain
        if self.parsed_pddl_domain.actionCosts == True:
            self.actionCosts = True
        else:
            self.actionCosts = False



        #if the observability_file_name is included - parse it
        if observability_file_name != None:

            self.are_observables_specified = True
            print('observability_file_name %s'%observability_file_name)
            if grd_defs.NON_OBSERVABILITY_STRING in observability_file_name:
                self.are_observables_specified = False
                print('non observables are specified')


            self.observability_file_name = observability_file_name
            self.full_path_observability_file_name = os.path.abspath(os.path.join(destination_folder_name,observability_file_name))

            if self.are_observables_specified:
                self.non_observability_actions_list = self.load_actions(self.full_path_observability_file_name)
            else:
                self.observability_actions_list = self.load_actions(self.full_path_observability_file_name)
                action_list_string = ''
                for op in self.observability_actions_list:
                    action_list_string += ' (%s) '%op
                self.observability_actions_list_string = action_list_string

        #if the reciprocal_observability_file_name is included - parse it
        if reciprocal_observability_file_name != None and reciprocal_observability_file_name != grd_defs.NA:

            print('reciprocal observability_file_name %s'%reciprocal_observability_file_name)


            self.reciprocal_observability_file_name = reciprocal_observability_file_name
            self.full_path_reciprocal_observability_file_name = os.path.abspath(os.path.join(destination_folder_name,reciprocal_observability_file_name))


            self.reciprocal_observability_actions_list = self.load_actions(self.full_path_reciprocal_observability_file_name)
            action_list_string = ''
            for op in self.reciprocal_observability_actions_list:
                action_list_string += ' (%s) '%op
            self.reciprocal_observability_actions_list_string = action_list_string


        #if the action token file name is included - parse it
        if action_token_file_name != None:

            print("action token name is :")
            print(action_token_file_name)

            self.action_tokens_file_name = action_token_file_name
            self.full_action_tokens_file_name = os.path.abspath(os.path.join(destination_folder_name,action_token_file_name))


            self.action_tokens_list = self.load_actionsTokens(self.full_action_tokens_file_name)
            action_tokens_list_string = ''
            for op in self.action_tokens_list:
                action_tokens_list_string += ' (%s) '%op
            self.action_tokens_list_string = action_tokens_list_string

        #if the poi_hyps is included - parse it
        if poi_hyps_file != None:
            self.poi_hyps_file_name = poi_hyps_file
            self.full_poi_hyps_file_name = os.path.abspath(os.path.join(destination_folder_name,self.poi_hyps_file_name))


            self.poi_hyps_list = self.load_poiHyps(self.full_poi_hyps_file_name)
            poi_hyps_list_string = ''
            for hyp in self.poi_hyps_list:
                poi_hyps_list_string += ' (%s) '%hyp.atoms
            self.poi_hyps_list_string = poi_hyps_list_string


    #open and parse non-observable actions file
    def load_actions(self,file_name):


        instream = open( file_name )
        action_list =[]
        for line in instream :
            new_line = line.strip()
            new_line = new_line.replace(')','')
            new_line = new_line.replace('(','')
            action_list.append(new_line)
        instream.close()
        return action_list

    #open and parse poi_hyps file
    def load_poiHyps(self,file_name):

        #open and parse poi_hyp file
        instream = open( file_name )
        poi_hyps_list =[]
        #each line in the file is the index of the relevant hyp
        for line in instream :
            line = line.replace('\n','')
            hyp_index = (int)(line)
            current_hyp = self.hyps_set[hyp_index]
            current_hyp.name = line
            poi_hyps_list.append(current_hyp)
        instream.close()
        return poi_hyps_list


    def load_actionsTokens(self,file_name):

        #open and parse hyp file
        instream = open( file_name )
        action_tokens_list =[]
        for line in instream :
            new_line = line.strip()
            new_line = new_line.replace(')','')
            new_line = new_line.replace('(','')
            new_line = new_line.split()
            action_tokens_list.append(new_line)
        instream.close()

        return action_tokens_list

    def load_groundedActions(self,file_name):

        #open and parse hyp file
        instream = open( file_name )
        grounded_action_list =[]
        for line in instream :
            new_line = line.strip()
            new_line = new_line.replace(')','')
            new_line = new_line.replace('(','')
            #create a list with action name followed by parameters
            new_line = new_line.split()
            grounded_action_list.append(new_line)
        instream.close()

        return grounded_action_list


    def load_hypotheses(self,file_name) :
        '''
        Creates a seperate problem instance for each hypothesis (the problem is as defined in the third party pyperplan_s)
        :param file_name: hyps file name
        :return:
        '''

        #open and parse hyp file
        instream = open( file_name )
        index = 0
        for line in instream :
            line = line.strip()
            H = GrdHypothesis()
            H.atoms = [  tok.strip() for tok in line.split(',') ]
            H.name = index
            self.hyps_set.append( H )
            index +=1
        instream.close()


        #create for each GrdHypothesis the corresponding planning task
        index = 0
        while(index < len(self.hyps_set)):

            # generate the problem with Goal = hyp
            hyp_problem_name = os.path.join(self.destination_folder_name,'hyp_%d_problem.pddl'%index)

            #because the pyper plan does not support action costs we remove the '(= (total-cost) 0)' statement from the file if it exists
            self.hyps_set[index].generate_pddl_for_hyp_plan( hyp_problem_name,self.full_template_file_name,True)



            #parse the current planning problem
            hyp_planning_problem = grd_planning_gen.parse_problem_file(hyp_problem_name,self.full_domain_file_name)
            hyp_planning_task = grounding.ground(hyp_planning_problem)

            #TODO: decide if the re is a more elegant way - and see how helpful the relevance check may be
            #We create a grounded problem for which relevance check is not performed
            if(index == 0):
                self.planningTaskForExploration = grounding.ground(hyp_planning_problem,False)
                self.static_predicates = grounding.get_statis_predicates(hyp_planning_problem)



            self.hyps_set[index].set_task(hyp_planning_task)
            self.hyps_set[index].set_name(index)
            index+=1


    #create the successor states which are extracted from the task for which the relevance analysis was not perfroemd
    def get_successor_states(self,grd_node):


        successor_states = self.planningTaskForExploration.get_successor_states(grd_node.state)
        return successor_states

    #set the array of optimal costs
    def set_optimal_costs(self,optimal_costs):
        self.optimal_costs = optimal_costs

    #create a string of the optimal costs
    def get_optimal_costs_string(self):
        optimal_costs_string =''

        if self.optimal_costs == None:
            optimal_costs_string  = 'optimal_costs not set yet'
        else:
            optimal_costs_string ='['
            for cost in self.optimal_costs:
                optimal_costs_string += '%d '%cost
            optimal_costs_string +=']'
        return optimal_costs_string

    def set_sub_optimal_bound_array(self,budget):
        if isinstance(budget, str):
            self.bound_array = grd_utils.create_budget_array(len(self.hyps_set), budget )
        else:
            self.bound_array = budget

    def get_sub_optimal_bound_array(self):

        return self.bound_array

    def get_sub_optimal_bound_array_string(self):

        if self.bound_array is None:
            return 'NA'

        bound_array_string = '<'

        for bound in self.bound_array:
            bound_array_string += '%d,'%bound
        bound_array_string+= '>'

        return bound_array_string


    def set_design_budget_array(self,design_budget_array):

        self.design_budget_array = design_budget_array

    def get_design_budget_array(self):

        return self.design_budget_array

    def get_action_sequence_cost (self, obs_seq):

        seq_cost = 0
        for action in obs_seq:
            action_name = action.split()[0]
            action_name = action_name.replace('(','')
            action_name = action_name.replace(')','')
            if self.actionCosts:  #non-uniform cost
                #get action cost
                action_cost = self.parsed_pddl_domain.actions[action_name].cost
                seq_cost += action_cost
            else: #uniform cost
                seq_cost += 1
        return seq_cost

    def is_path_legal (self, path, solution_sequence, hyp_index) :

        obs_seq_names = []
        for obs in path :
            obs_seq_names.append(obs.name)
        # get the cost of the obs_seq
        path_cost = self.get_action_sequence_cost(obs_seq_names )

        solution_cost = self.get_action_sequence_cost(solution_sequence )


        # if the path is on an optimal path
        if path_cost + solution_cost == self.optimal_costs[hyp_index]:
            return True

        else:
            return False


class GrdHypothesis :

    def __init__( self ) :

        self.planning_task = None
        self.name = ''
        self.atoms = []
        self.optimal_cost = -1
        self.optimal_obs_seq = []

        self.size_of_pr_search_space = -1

    def set_task(self,hyp_planning_task):

        self.planning_task = hyp_planning_task

    def set_name(self, name):

        self.name = name


    #taken from PR
    def generate_pddl_for_hyp_plan( self, out_name,template_file_name, remove_cost_statement) :
        #'template.pddl'
        instream  = open(template_file_name)
      #  outstream = open( out_name, 'w' )


        with open(out_name, 'w') as outstream:

            for line in instream :
                if remove_cost_statement :
                    if 'total-cost' in line:
                        continue

                line = line.strip()
                if '<HYPOTHESIS>' not in line :
                    #print >> outstream, line
                    print(line,file = outstream)
                else :
                    for atom in self.atoms :
                        #print >> outstream, atom
                        print(atom,file = outstream)

            outstream.close()
        instream.close()


def test_grd_task():

    import sys, grd_defs

    grd_utils.empty_or_create_log_and_gen_dir()


    grd_task = GrdTask()
    #initialize tar folder
    if len(sys.argv) == 2:
        grd_task.initialize_with_tarred_folder(grd_defs.gen_files_dir,sys.argv[1])
    #initialize with files
    else:

        grd_task.initialize_with_files(grd_defs.gen_files_dir,sys.argv[1],sys.argv[2],sys.argv[3])



if __name__ == '__main__' :

    test_grd_task();
