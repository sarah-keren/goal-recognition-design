'''
Created on May 18, 2014

@author: sarahn
'''

import os,sys,itertools
import grd_defs,resource,grd_planning_gen,grd_planning


class Log:
    SILENT = 0
    FILE = 0x1
    SCREEN = 0x2
    BOTH = FILE | SCREEN
    def __init__(self, filename=None):
        self.name = filename
        self.has_file = filename is not None
        if self.has_file:
            self.file = open(filename, "w")
    def write(self, string):
        sys.stdout.write(string)
        if self.has_file:
            self.file.write(string)
    def suspend(self):
        if self.has_file:
            self.file.close()
            del self.file
        sys.stdout.flush()
    def resume(self):
        if self.has_file:
            self.file = open(self.name, "a")
    def __call__(self, mode):
        if mode == Log.SILENT:
            return SilentWriter()
        elif mode == Log.SCREEN or not self.has_file:
            return sys.stdout
        elif mode == Log.FILE:
            return self.file
        else:
            return self

class SilentWriter:
    def write(self, string):
        pass

def run(cmd, timeout, memory, log=None, verbose=True):
    """Runs a command using os.system(), restricting time and space
    resources, preventing core dumps and redirecting the output
    (both stdout and stderr) into a log file (if log is not None).

    Parameters:
      cmd     - shell command to be executed
      timeout - timeout in CPU seconds
      memory  - maximum heap size allowed in Megabytes
      log     - the log file (of class benchmark.Log)
      verbose - If true, also print the heap and time restrictions,
                the return code of the program and elapsed time.
                If false, this info is logged if there is a log,
                but not printed.

    Return Value: (signal, time)
      signal  - 0 if the program terminated properly, non-zero otherwise.
      time    - time spent for executing the program in seconds.
                Note that this is *not* CPU time but usertime and might thus
                exceed the timeout threshold.
    """

    time_slack = 5

    log_mode = Log.SILENT
    if verbose:
        log_mode |= Log.SCREEN
    if log:
        cmd = "(%s) >> %s 2>&1" % (cmd, log.name)
        log_mode |= Log.FILE
    if not log:
        log = Log()

    if verbose :
        print (log(log_mode), "Timeout: %d seconds" % timeout)
        print (log(log_mode), "Heap restriction: %d MB" % memory)
        print (log(log_mode), "Command: %s" % cmd)
        print (log(log_mode))

    memory *= 1024 * 1024
    log.suspend()

    time_passed_before = os.times()[2] + os.times()[3]
    pid = os.fork()
    if not pid:
        resource.setrlimit(resource.RLIMIT_CPU, (timeout - time_slack, timeout))
        # resource.setrlimit(resource.RLIMIT_DATA, (memory, memory))
        # resource.setrlimit(resource.RLIMIT_RSS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_AS, (memory, memory))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        signal = os.system(cmd)
        if signal % 256 == 0:
            os._exit(signal // 256)
        os._exit(signal % 256)

    signal = os.waitpid(pid, 0)[1]

    log.resume()
    time_passed = (os.times()[2] + os.times()[3]) - time_passed_before

    if signal == 0:
        if verbose :
            print (log(log_mode), "\nTime spent: %.3f seconds" % time_passed)
    else:
        if verbose :
            print (log(log_mode), "\nFailed! [Signal %d, Time %.3f seconds]" \
                  % (signal, time_passed))

    return signal, time_passed


def empty_or_create_log_and_gen_dir():
    
    import shutil
    
    if os.path.exists(grd_defs.gen_files_dir):
        shutil.rmtree(grd_defs.gen_files_dir)
    os.makedirs(grd_defs.gen_files_dir)
    
    if os.path.exists(grd_defs.log_files_dir):
        shutil.rmtree(grd_defs.log_files_dir)
    os.makedirs(grd_defs.log_files_dir)
    

#helper functions
def powerset(iterable):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(len(s)+1))

def powerset_limit(iterable,limit):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        return itertools.chain.from_iterable(itertools.combinations(s, r) for r in range(limit+1))

def powerset_n(iterable,n):
        "powerset([1,2,3]) --> () (1,) (2,) (3,) (1,2) (1,3) (2,3) (1,2,3)"
        s = list(iterable)
        comb = itertools.combinations(s, n)
        return comb
    


#Deal with timeout
class TimeoutException(Exception):
    pass

def signal_handler(signum, frame):
    raise TimeoutException("Timed out exception!")

if __name__ == '__main__':
    pass


#parse budget array

def create_budget_array(num_of_hyps, array_string = None ):
    budget_array = []
    #if agents are optimal array string is none
    if array_string is None:
        hyp_index = 0
        while hyp_index < num_of_hyps :
            budget_array.append(0)
            hyp_index +=1
    else:

        budget_string_array = array_string.split(':')
        hyp_index = 0
        cur_budget = 0
        # a single budget was specified
        isUniform = False
        if len(budget_string_array) == 1:
            isUniform = True

        while hyp_index < num_of_hyps:
            if isUniform:
                budget_array.append(int(budget_string_array[0]))
            else:
                if hyp_index < len(budget_string_array):
                    cur_budget = int(budget_string_array[hyp_index])
                    budget_array.append(cur_budget)
                else:
                    #the current budget is 0
                    budget_array.append(0)
            hyp_index +=1

    if budget_array == []:
        print('error in create_budget_array')
        sys.exit()
    print('budget array is')
    print(budget_array)

    return budget_array


def get_paths(optimal_plans, wcd_value=-1, validity_method=grd_defs.LatestSplit):


    if not optimal_plans:
        return []

    op_path = []
    if validity_method == grd_defs.LatestExpose :
        #for the first agent add all the actions
        for op in optimal_plans[0]:
            op_path.append(op)
        #for the second agent add the agents that were not added previously
        for op in optimal_plans[1]:
            if 'together' not in op :
                op_path.append(op)

    else:
        if validity_method == grd_defs.CommonDeclare :
            #for the first agent add all the actions
            for agent_plan in optimal_plans:
                for op in agent_plan:
                    if 'declare' not in op.lower():
                        op_path.append(op)


        else:

            split_value =  wcd_value if wcd_value >=0 else 0
            op_path=optimal_plans[0][:split_value]
            for op_plan in optimal_plans:
                op_path += op_plan[split_value:]


    return op_path

def parse_action_name(op,calc_method):

    act_tok = None

    # clean the operator name
    op_name = op.replace('_#0','')
    op_name = op_name.replace('_#1','')
    op_name = op_name.replace('_seperate','')
    op_name = op_name.replace('_together','')
    op_name = op_name.replace('(','')
    op_name = op_name.replace(')','')
    op_name = op_name.split(' time')[0]
    op_name = op_name.split(grd_defs.token_prefix.lower())[0]
    op_name = '(%s)'%op_name

    is_nonobservable = False
    if grd_defs.NON_OBSERVABLE_STRING in op_name:
        op_name =  op_name.replace('_%s'%grd_defs.NON_OBSERVABLE_STRING,'')
        is_nonobservable = True

     # if the name of the method contains the emitted token - replace it
    if calc_method == grd_defs.CommonDeclare:
        if grd_defs.token_prefix.lower() in op.lower():
            act_tok = op.split(grd_defs.token_prefix.lower())[1]
            act_tok = act_tok.replace(')','')
            act_tok = '%s%s'%(grd_defs.token_prefix,act_tok)
        if '_params_nil' in op_name:
            act_tok = grd_defs.token_prefix+grd_defs.NIL_STRING
            op_name = op_name.replace('_params_nil','')
        print('act_tok: %s'%act_tok)


    return [op_name, is_nonobservable, act_tok]


def check_optimal_costs(task, grd_node=None, index=0):

    optimal_costs = []
    count_expanded_states = 0
    solution_array = []


    hyp_index= 0
    for hyp in task.hyps_set:

        #problem file
        current_problem_file = grd_planning_gen.generate_current_problem_file(task.hyps_set[hyp_index],grd_node,task.full_template_file_name,task.destination_folder_name,hyp_index,index,task)
        [current_solution,test_failed,signal] = grd_planning.perform_planning(task.destination_folder_name,task.full_domain_file_name,os.path.abspath(current_problem_file))
        count_expanded_states += current_solution.num_expanded_states
        solution_array.append(current_solution)
        #if this fails for one of the hyps - update value to -1 since one of the hyps is unreachable
        if test_failed == True :

            #update original optimal cost
            optimal_costs.append(grd_defs.INFINITE_COST)
            print('In check_optimal_costs test_failed for task %s and hyp:'%task.task_name)
            print('hyp.atoms : %s'%hyp.atoms)

        else:
            #update optimal costs
            optimal_costs.append(int(current_solution.plan_cost))

        hyp_index +=1


    print('before leaving optimal costs they are ')
    print(optimal_costs)
    return [optimal_costs,count_expanded_states,solution_array]


def generate_hyp_sets_with_index(folder_name,hyp_file_name,generation_type = grd_defs.comb_all_pairs):

        print('generate_hyp_sets_with_index with folder_name : %s, hyp_file_name: %s, generation_type = %s '%(folder_name,hyp_file_name,generation_type))

        generated_hyp_files = []

        f = open(hyp_file_name)
        hyp_lines = f.readlines()
        f.close()


        combs = []

        if generation_type == grd_defs.comb_all_pairs or generation_type == grd_defs.comb_all_ordered_pairs or generation_type == grd_defs.comb_all_pairs_10  or generation_type == grd_defs.comb_all_pairs_5 or generation_type == grd_defs.comb_rand_30:

        	#generate all pairs
            import itertools
            s = list(hyp_lines)

            if generation_type == grd_defs.comb_rand_30:
                indices = [5,6,85,45,46,25,26,87]
                new_list = []
                for index in indices:
                    new_list.append(s[index])
                s = new_list


            combs = itertools.combinations(range(len(s)), 2)

            #add to the combination list the pair in reversed order
            if generation_type == grd_defs.comb_all_ordered_pairs:
                ordered_combs = []
                for pair in combs:
                    ordered_combs.append((pair[0],pair[1]))
                    ordered_combs.append((pair[1],pair[0]))
                combs = ordered_combs

            if generation_type == grd_defs.comb_all_pairs_10 :
                combs = itertools.islice(combs, 10) # grab the first ten elements

            if generation_type == grd_defs.comb_all_pairs_5 :
                combs = itertools.islice(combs, 5) # grab the first five elements

            if generation_type == grd_defs.comb_rand_30 :
                combs = itertools.islice(combs, 30) # grab the first 30 elements


        print('combs are: ')

        index = 0
        for pair in combs:

            print('-------------------------------------------------> pair is ')



            first_hyp = (pair[0])
            second_hyp = (pair[1])

            print(pair)
            print('%s-%s\n'%(hyp_lines[first_hyp],hyp_lines[second_hyp]))

            new_file_name = 'hyp_@_%s_@_%s.dat'%( chr(first_hyp + ord('A')), chr(second_hyp + ord('A')))
            full_new_file_name = os.path.join(folder_name,new_file_name)
            new_file = open(full_new_file_name,'w')

            new_file.write(hyp_lines[first_hyp])
            new_file.write(hyp_lines[second_hyp])

            new_file.close()

            generated_hyp_files.append(new_file_name)
            index += 1
        return [generated_hyp_files,len(s)]


def create_tarred_task(task_name, destination_folder_name, domain_file, template_file, hyps_file_name, observability_file_name = None, action_token_file_name = None, reciprocal_observability_file_name=None):

    tarred_dir = '%s.tar.bz2' % task_name

    #change current directory
    current_dir = os.getcwd()
    os.chdir(destination_folder_name)

    #create the task folder
    cur_directory_name = os.path.join(os.getcwd(), task_name)
    cmd = 'mkdir %s' % task_name
    os.system(cmd)

    #copy files into the task directory
    cmd = 'cp %s %s' % (domain_file, cur_directory_name)
    os.system(cmd)
    cmd = 'cp %s %s' % (template_file, cur_directory_name)
    os.system(cmd)
    cmd = 'cp %s %s' % (hyps_file_name, cur_directory_name)
    os.system(cmd)
    if observability_file_name != None:
        cmd = 'cp %s %s' % (observability_file_name, cur_directory_name)
    os.system(cmd)
    if action_token_file_name != None:
        cmd = 'cp %s %s' % (action_token_file_name, cur_directory_name)
    os.system(cmd)

    if reciprocal_observability_file_name != None:
        cmd = 'cp %s %s' % (reciprocal_observability_file_name, cur_directory_name)
    os.system(cmd)

    #create compressed folder
    cmd = 'tar jcvf %s %s/' % (tarred_dir, task_name)
    os.system(cmd)

    #delete the generated folder
    cmd = 'rm -r %s ' % (cur_directory_name)
    os.system(cmd)
    #change back
    os.chdir(current_dir)




def get_constraints_inst(grd_task, op_path, calc_method, op):


    # get the operator that appears after op if it exists
    found = False
    next_op_name = None
    parsed_op = parse_action_name(op,calc_method)[0]
    parsed_op = parsed_op.replace('(','')
    parsed_op = parsed_op.replace(')','')
    parsed_op_action_name = parsed_op.split()[0]
    parsed_op_params = parsed_op.split()[1:]

    const_actions = get_constraints_actions(grd_task)
    if const_actions is None:
        return None
    if parsed_op_action_name not in const_actions:
        return None

    for cur_op in op_path:

        [cur_op_name, is_nonobservable, act_tok] = parse_action_name(cur_op,calc_method)
        cur_op_name = cur_op_name.replace('(','')
        cur_op_name = cur_op_name.replace(')','')
        action_name = cur_op_name.split()[0]
        cur_op_params = cur_op_name.split()[1:]

        if found and action_name in const_actions and parsed_op_params[0] != cur_op_params[0] :
            next_op_name = cur_op_name
            break

        if cur_op_name == parsed_op and not found:

            found = True

    const_params = []
    if next_op_name is not None:
        [next_op_name, is_nonobservable, act_tok] = parse_action_name(next_op_name,calc_method)
        next_op_name = next_op_name.replace('(','')
        next_op_name = next_op_name.replace(')','')
        const_params = next_op_name.split()[1:]
        if 'dummy' in parsed_op:
            return None
        return [parsed_op, const_params]
    else:
        return None

def get_constraints_actions(cur_grd_task):

    domain_name = cur_grd_task.domain_name

    if 'grid' in domain_name:
        return ['move']
    elif 'block' in domain_name:
        return ['stack','unstack']#['pick-up']#,'put-down']
    elif 'logistics' in domain_name:
        return ['load-truck','unload-truck']
    elif 'iss' in domain_name:
        return ['move']#,'take','put-away']
    elif 'depots' in domain_name:
        return ['lift']
    elif 'intrusion-detection' in domain_name:
        return ['modify-files','download-files']
    elif 'zeno-travel' in domain_name:
        return ['fly','board']
    elif 'sokoban' in domain_name:
        return ['move']
    elif 'rovers' in domain_name:
        return ['sample_rock','sample_soil']
    elif 'campus' in domain_name:
        return ['move']

    else:
        print('COMPLETE')
        print(cur_grd_task.template_file_name)
        return None


def get_disallowed_actions(cur_grd_task):
    return get_constraints_actions(cur_grd_task)


def get_constraint_type(cur_grd_task):

    domain_name = cur_grd_task.domain_name
    if 'grid' in domain_name:
        return 'object'
    elif 'block' in domain_name:
        return 'object'
    elif 'logistics' in domain_name:
        return 'object'
    elif 'iss' in domain_name:
        return 'object'
    elif 'depots' in domain_name:
        return 'object'
    elif 'intrusion-detection' in domain_name:
        return 'object'
    elif 'sokoban' in domain_name:
        return 'object'
    elif 'zeno-travel' in domain_name:
        return 'object'
    elif 'rovers' in domain_name:
        return 'object'
    elif 'campus' in domain_name:
        return 'object'
    else:
        print('COMPLETE')
        return None



def get_param_count(grd_task,action):
    action_name = action.replace(')','')
    action_name = action_name.replace('(','')
    action_type = action_name.split()[0]
    param_count = len(grd_task.parsed_pddl_domain.actions[action_type].signature)
    return param_count


def get_domain_name(grd_task):

    if 'grid' in grd_task.full_domain_file_name:
        return 'grid'
    elif 'block' in grd_task.full_domain_file_name:
        return 'block'
    elif 'logistics' in grd_task.full_domain_file_name:
        return 'logistics'
    elif 'iss' in grd_task.full_domain_file_name:
        return 'iss'
    elif 'depots' in grd_task.full_domain_file_name:
        return 'depots'
    elif 'zeno-travel' in grd_task.full_domain_file_name:
        return 'zeno-travel'
    elif 'intrusion-detection' in grd_task.full_domain_file_name:
        return 'intrusion-detection'
    elif 'sokoban' in grd_task.full_domain_file_name:
        return 'sokoban'
    elif 'rovers' in grd_task.full_domain_file_name:
        return 'rovers'
    elif 'campus' in grd_task.full_domain_file_name:
        return 'campus'


