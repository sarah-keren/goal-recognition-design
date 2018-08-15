__author__ = 'Sarah Keren'

"""
Generator of GRD problems. See main at the bottom for a running example
"""

import random
import os, random, grd_defs, grd_utils, grd_task, numpy
import hashlib



destination_folder = '/home/GoalRecognitionDesign/benchmarks_generated'
benchmarks_folder = '/home/GoalRecognitionDesign/benchmarks'
arr_non_obs_ratio = [0,5,10,15,20,25]
num_instances_of_each_ratio = 5

# how many observability files to create for each instance
OBSERVABILITY_FILES_COUNT = 3
OBSERVABILITY_FILES_FOLDER = 'observability_files'
NON_OBS_FILE_NAME = 'non-obs.dat'
POD_FILE_NAME = 'act-toks.dat'
POND_FILE_NAME = POD_FILE_NAME

# the seed used to generated the tokens
RANDOM_SEED = random.randint(1, 30)

# location of the files
BASE_FOLDER_NAME = 'BASE'
RUNNING_INDEX = 0
DEFAULT_PROBABILITY = 0.7
MAX_NUM_OF_HYPS = 3



def generate_task_instances_different_observabilities(domain_name, benchmarks_folder_name, destination_folder):

    grd_tasks_files_list = []

    # delete old folders
    for obs_type in [grd_defs.OBSERVABILITY_FO, grd_defs.OBSERVABILITY_NO, grd_defs.OBSERVABILITY_POD, grd_defs.OBSERVABILITY_POND]:
        cur_destination_folder = os.path.join(destination_folder,domain_name, obs_type)
        cmd = 'rm -r %s; mkdir %s' %(cur_destination_folder, cur_destination_folder)
        os.system(cmd)


    for filename in os.listdir(benchmarks_folder_name):
        grd_tasks_files_list.append(os.path.join(benchmarks_folder_name, filename))



    for grd_task_compressed_files in grd_tasks_files_list:

        # generate basic grd_task
        grd_test_task = grd_task.GrdTask()
        folder_task_name = grd_test_task .initialize_with_tarred_folder(destination_folder, grd_task_compressed_files, False, MAX_NUM_OF_HYPS)
        operators = grd_test_task.planningTaskForExploration.operators

        new_token_file_name_1 = os.path.join(destination_folder,grd_defs.action_token_file_name)
        new_token_file_name_2 = os.path.join(destination_folder,'2-%s'%grd_defs.action_token_file_name)

        new_non_obs_file_name = os.path.join(destination_folder,grd_defs.non_obs_file_name)
        new_obs_file_name = os.path.join(destination_folder,grd_defs.obs_file_name)
        non_obs_file_complementry_name = 'comp-%s'%grd_defs.non_obs_file_name
        non_obs_file_complementry = os.path.join(destination_folder,non_obs_file_complementry_name)

        for obs_type in [grd_defs.OBSERVABILITY_FO, grd_defs.OBSERVABILITY_NO, grd_defs.OBSERVABILITY_POD, grd_defs.OBSERVABILITY_POND]:

            folder_name = obs_type.split('-',1)[0]
            current_destination_folder = os.path.join(destination_folder,domain_name, folder_name)

            seeds = get_observability_seeds(obs_type)
            for idx,seed in enumerate(seeds):
                generate_observability_files(new_non_obs_file_name,new_obs_file_name,new_token_file_name_1,new_token_file_name_2, grd_test_task, operators, obs_type, seed, non_obs_file_complementry)
                task_name = '%s-%s-%s'%(grd_test_task.task_name,obs_type,idx)
                if obs_type in [grd_defs.OBSERVABILITY_POD, grd_defs.OBSERVABILITY_POND]:
                    grd_utils.create_tarred_task(task_name, current_destination_folder, grd_test_task.full_domain_file_name
                                                 , grd_test_task.full_template_file_name, grd_test_task.full_hyps_file_name, None, new_token_file_name_1,None)
                else:
                    grd_utils.create_tarred_task(task_name, current_destination_folder, grd_test_task.full_domain_file_name, grd_test_task.full_template_file_name, grd_test_task.full_hyps_file_name, new_non_obs_file_name, new_token_file_name_1,new_obs_file_name)
                if non_obs_file_complementry is not None and obs_type in [grd_defs.OBSERVABILITY_NO]:
                    task_name = '%s-%s-%s-compl'%(grd_test_task.task_name,obs_type,idx)
                    grd_utils.create_tarred_task(task_name, current_destination_folder, grd_test_task.full_domain_file_name, grd_test_task.full_template_file_name, grd_test_task.full_hyps_file_name, non_obs_file_complementry, new_token_file_name_1)
                if new_token_file_name_2 is not None and obs_type in [grd_defs.OBSERVABILITY_POD,grd_defs.OBSERVABILITY_POND]:
                    task_name = '%s-%s-%s-tok2'%(grd_test_task.task_name,obs_type,idx)
                    grd_utils.create_tarred_task(task_name, current_destination_folder, grd_test_task.full_domain_file_name, grd_test_task.full_template_file_name, grd_test_task.full_hyps_file_name, non_obs_file_complementry, new_token_file_name_2,new_obs_file_name)



        cmd = 'rm -r %s ' % (folder_task_name)
        os.system(cmd)


def generate_task_instances_refinement_relation(domain_name, benchmarks_folder_name, destination_folder):

    destination_folder = os.path.join(destination_folder,domain_name)
    cmd = 'mkdir %s' %destination_folder
    os.system(cmd)


    grd_tasks_files_list = []


    for filename in os.listdir(benchmarks_folder_name):
        grd_tasks_files_list.append(os.path.join(benchmarks_folder_name, filename))


    for grd_task_compressed_files in grd_tasks_files_list:

        # generate basic grd_task
        grd_test_task = grd_task.GrdTask()
        folder_task_name = grd_test_task .initialize_with_tarred_folder(destination_folder, grd_task_compressed_files, False, MAX_NUM_OF_HYPS)
        operators = grd_test_task.planningTaskForExploration.operators

        # generate all files which are created in grd_test_task.destination_folder_name
        generate_observability_files_refinement(grd_test_task, operators)

        # copy the generated folder to the benchmark folder
        #cmd = 'mv %s %s' % (grd_test_task.destination_folder_name,destination_folder)
        #os.system(cmd)
        #cmd = 'rm -r %s ' % (folder_task_name)
        #os.system(cmd)


def get_observability_seeds(obs_type):

    if obs_type == grd_defs.OBSERVABILITY_FO :
        return [1]
    if obs_type == grd_defs.OBSERVABILITY_NO :
        return [0.2,0.3,0.5]
    if obs_type == grd_defs.OBSERVABILITY_POD :
        return [1,2,3,4,5,6]
    if obs_type == grd_defs.OBSERVABILITY_POND :
        return [[1,0.2],[1,0.3],[1,0.5],[2,0.2],[2,0.3],[2,0.5],[3,0.2],[3,0.3],[3,0.5],[4,0.2],[4,0.3],[4,0.5],[5,0.2],[5,0.3],[5,0.5],[6,0.2],[6,0.3],[6,0.5]]



def choose_tokens(possible_tokens, observability, seed = RANDOM_SEED):

    tokens = []
    if observability == grd_defs.OBSERVABILITY_FO:
        tokens.append(possible_tokens[0])

    if observability == grd_defs.OBSERVABILITY_NO:
        tokens.append(possible_tokens[1])

    if observability == grd_defs.OBSERVABILITY_POD:
        tokens.append(possible_tokens[2])

    if observability == grd_defs.OBSERVABILITY_POND:
        tokens.append(possible_tokens[2])
        tokens.append(possible_tokens[3])

    return tokens


def get_split_op(op):

    split_op = op.name.split()
    params_string =''
    for param in split_op[1:]:
        params_string += ' %s'%param
    if params_string == '':
        split_op[0] = split_op[0].replace(')','')
        #split_op[0] = split_op[0].replace('(','')

    return [split_op[0],params_string]


def generate_token_file_deprecated(token_file_name, cur_grd_task, operators,observability):

    cur_token_file_name = os.path.join(cur_grd_task.destination_folder_name,token_file_name)
    cur_token_file = open(cur_token_file_name,'w')

    for op in operators:
        split_op = op.name.split()
        possible_tokens = get_possible_tokens(op)
        chosen_tokens = choose_tokens(possible_tokens, observability)

        params_string =''
        for param in split_op[1:]:
            params_string += ' %s'%param
        for token in chosen_tokens:
            line = '%s %s %s'%(split_op[0],token,params_string)
            cur_token_file.write('%s\n'%line)

    cur_token_file.close()
    return cur_token_file_name


def generate_observability_files_refinement(grd_test_task, operators):


   #generate obs.dat files
   non_obs_file_array = []
   pod_obs_file_array = []
   pond_obs_file_array = []

   obs_file_dir = os.path.join(grd_test_task.destination_folder_name,OBSERVABILITY_FILES_FOLDER)
   if not os.path.exists(obs_file_dir):
    os.makedirs(obs_file_dir)

   # for FO we generate all the relevant observability files
   fo_no_file_name   = os.path.join(obs_file_dir,'%s__%s'%('FONO',NON_OBS_FILE_NAME))
   fo_no_file = open(fo_no_file_name,'w')
   fo_no_file.close()

   fo_pod_file_name   = os.path.join(obs_file_dir,'%s__%s'%('FOPOD',POD_FILE_NAME))
   fo_pod_file = open(fo_pod_file_name,'w')
   # populate the pod file
   for op in operators:
       possible_tokens = get_possible_tokens(op)
       split_op = get_split_op(op)
       token = possible_tokens[0]
       fo_pod_file.write('%s %s %s\n'%(split_op[0], token, split_op[1]))
   fo_pod_file.close()

   # create the observability files
   for i_no in range(OBSERVABILITY_FILES_COUNT):

        non_obs_file_name = os.path.join(obs_file_dir,'%d__%s_%s'%(i_no,'NO_',NON_OBS_FILE_NAME))
        cur_non_obs_file = open(non_obs_file_name,'w')
        non_obs_file_array.append(cur_non_obs_file)


        cur_pod_files = []
        cur_pond_files = []
        for i_pod in range(OBSERVABILITY_FILES_COUNT):

            pod_file_name = os.path.join(obs_file_dir,'%d__%d_%s_%s'%(i_no,i_pod,'POD_',POD_FILE_NAME))
            cur_pod_obs_file = open(pod_file_name,'w')
            cur_pod_files.append(cur_pod_obs_file)

            cur_pond_file_array = []
            for i_pond in range(OBSERVABILITY_FILES_COUNT):
                pond_file_name = os.path.join(obs_file_dir,'%d__%d_%d_%s_%s'%(i_no,i_pod,i_pond,'POND_',POND_FILE_NAME))
                cur_pond_file = open(pond_file_name,'w')
                cur_pond_file_array.append(cur_pond_file)
            cur_pond_files.append(cur_pond_file_array)

        pond_obs_file_array.append(cur_pond_files)
        pod_obs_file_array.append(cur_pod_files)


   # populate the observability files
   for no_index in range(OBSERVABILITY_FILES_COUNT):

        #generate token file
        no_pod_file_name = os.path.join(obs_file_dir,'%d__%s__%s'%(no_index,'NOPOD',POD_FILE_NAME))
        no_pod_file = open(no_pod_file_name,'w')

        op_counter = 0
        for op in operators:

            op_counter += 1

            # for token generation
            possible_tokens = get_possible_tokens(op)
            split_op = get_split_op(op)

            # making sure observability corresponds to the counter and index
            obs_ratio = int(no_index+RANDOM_SEED)
            b_observable = op_counter%(obs_ratio)
            print('random is: ')
            #print(op_counter%(obs_ratio))
            print(b_observable)
            if b_observable == 0:
                #generate the relevant token in the NO files
                non_obs_file_array[no_index].write('%s\n'%op.name)
                no_pod_file.write('%s %s %s\n'%(split_op[0], possible_tokens[1], split_op[1]))
            else:
                no_pod_file.write('%s %s %s\n'%(split_op[0], possible_tokens[0], split_op[1]))

            # update the token in pod observability files
            pod_index = -1
            for pod_file in pod_obs_file_array[no_index]:

                pod_index += 1
                if b_observable == 0:
                    token_index = 1 # nil token
                else:
                    token_index = (pod_index+2)%len(possible_tokens) # random token

                token = possible_tokens[token_index]
                if split_op[1] == '':
                    pod_file.write('%s %s %s)\n'%(split_op[0], token, split_op[1]))
                else:
                    pod_file.write('%s %s %s\n'%(split_op[0], token, split_op[1]))

                # update the token in the pond observability file
                no_files = pond_obs_file_array[no_index]
                pod_files = no_files[pod_index]
                pond_index = -1
                for pond_file in pod_files:
                    pond_index += 1
                    # write the first (POD) token
                    if split_op[1] == '':
                        pond_file.write('%s %s %s)\n'%(split_op[0], token, split_op[1]))
                    else:
                        pond_file.write('%s %s %s\n'%(split_op[0], token, split_op[1]))
                    if b_observable:
                        second_token_index = 4 + pond_index
                        if second_token_index == len(possible_tokens)-1 or second_token_index == 1 or second_token_index == 0 or second_token_index == token_index:
                            second_token_index = 6
                        second_token = possible_tokens[second_token_index]
                        if split_op[1] == '':
                            pond_file.write('%s %s %s)\n'%(split_op[0], second_token, split_op[1]))
                        else:
                            pond_file.write('%s %s %s\n'%(split_op[0], second_token, split_op[1]))

        no_pod_file.close()


   for file in non_obs_file_array:
       file.close()

   for file_list in pod_obs_file_array:
       for file in file_list:
        file.close()

   for file_list in pond_obs_file_array:
       for list in file_list:
           for file in list:
               file.close()

   print('Generated')



def generate_observability_files(non_obs_file_name, obs_file_name, tokens_file_name_1,tokens_file_name_2, grd_test_task, operators, obs_type, seed, non_obs_file_complementry=None):

    full_non_obs_file_name = os.path.join(grd_test_task.destination_folder_name,non_obs_file_name)
    cur_non_obs_file = open(full_non_obs_file_name,'w')

    full_obs_file_name = os.path.join(grd_test_task.destination_folder_name,obs_file_name)
    cur_obs_file = open(full_obs_file_name,'w')

    full_tokens_file_name_1 = os.path.join(grd_test_task.destination_folder_name,tokens_file_name_1)
    tokens_file_1 = open(full_tokens_file_name_1,'w')

    full_tokens_file_name_2 = os.path.join(grd_test_task.destination_folder_name,tokens_file_name_2)
    tokens_file_2 = open(full_tokens_file_name_2,'w')

    cur_non_obs_complementry_file = None
    if non_obs_file_complementry != None:
        full_non_obs_file_complementry_name = os.path.join(grd_test_task.destination_folder_name,non_obs_file_complementry)
        cur_non_obs_complementry_file = open(full_non_obs_file_complementry_name,'w')

    for op in operators:

        # for token generation
        possible_tokens = get_possible_tokens(op)
        split_op = get_split_op(op)
        token = ''

        if obs_type == grd_defs.OBSERVABILITY_FO:
            cur_obs_file.write('%s\n'%op.name)
            token = possible_tokens[0]
            if split_op[1] != '':
                tokens_file_1.write('%s %s %s\n'%(split_op[0], token, split_op[1]))
            else:
                tokens_file_1.write('%s %s %s)\n'%(split_op[0], token, split_op[1]))

        if obs_type == grd_defs.OBSERVABILITY_NO:

            # according to probability - decide if the op is observable or not
            b_observable = numpy.random.choice(numpy.arange(0,2), p=[1-seed, seed])

            if b_observable:
                cur_obs_file.write('%s\n'%op.name)
                token = possible_tokens[0]

                if cur_non_obs_complementry_file is not None:
                    cur_non_obs_complementry_file.write('%s\n'%op.name)
                    tokens_file_2.write('%s %s %s\n'%(split_op[0], token, split_op[1]))

            else: # non-observable

                cur_non_obs_file.write('%s\n'%op.name)
                token = possible_tokens[1]

            tokens_file_1.write('%s %s %s\n'%(split_op[0], token, split_op[1]))


        if obs_type == grd_defs.OBSERVABILITY_POD:
            token_index = seed%5 + 1
            token = possible_tokens[token_index]
            tokens_file_1.write('%s %s %s\n'%(split_op[0], token, split_op[1]))
            token_index = 8
            token_2 = possible_tokens[token_index]
            tokens_file_2.write('%s %s %s\n'%(split_op[0], token_2, split_op[1]))

        if obs_type == grd_defs.OBSERVABILITY_POND:
            probability = seed[1]
            token_index = seed[0]%5 + 1
            # smample the probaiblity of having more than one token
            b_noisy = numpy.random.choice(numpy.arange(0,2), p=[1-probability, probability])
            cur_tokens = []
            cur_tokens_2 = []
            if b_noisy:
                cur_tokens.append(possible_tokens[token_index])
                cur_tokens.append(possible_tokens[1])

                cur_tokens_2.append(possible_tokens[8])
                cur_tokens_2.append(possible_tokens[1])
            else:
                cur_tokens.append(possible_tokens[token_index])
                cur_tokens_2.append(possible_tokens[8])

            for tok in cur_tokens:
                tokens_file_1.write('%s %s %s\n'%(split_op[0], tok, split_op[1]))

            for tok in cur_tokens_2:
                tokens_file_2.write('%s %s %s\n'%(split_op[0], tok, split_op[1]))

    cur_obs_file.close()
    cur_non_obs_file.close()
    tokens_file_1.close()
    tokens_file_2.close()
    if cur_non_obs_complementry_file is not None:
        cur_non_obs_complementry_file.close()

# different tokens are created (specification below)
def get_possible_tokens(op):


    op_name = op.name
    op_name = op_name.replace(')','')
    op_name = op_name.replace('(','')

    action_name = op_name.split()[0]
    params_string = op_name.split()[1:]
    all_params_string = ''
    for param in params_string:
        all_params_string += '_%s'%param

    # all possible tokens
    possible_tokens = []

    # 0: fully observable
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,op_name.replace(' ','')))
    # 1: non-observable
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,grd_defs.NIL_STRING))
    # 2: first param
    if len(params_string)>0:
        possible_tokens.append('%s%s'%(grd_defs.token_prefix,params_string[0]))
    else:
        possible_tokens.append('%s%s'%(grd_defs.token_prefix,2))
    # 3: all params
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,all_params_string))
    # 4: action name
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,action_name))
    # 5: random a
    rand = (int(hashlib.sha256(all_params_string.encode('utf-8')).hexdigest(), 16) % 10**8)%(RANDOM_SEED)
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,rand))
    # 6: random b
    rand = (int(hashlib.sha256(all_params_string.encode('utf-8')).hexdigest(), 16) % 10**8)%(RANDOM_SEED-1)
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,rand))
    # 7: random c
    rand = (int(hashlib.sha256(all_params_string.encode('utf-8')).hexdigest(), 16) % 10**8)%(RANDOM_SEED+1)
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,rand))
    # 8: action name first letter
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,action_name[0]))
    # 9: random out of 2
    rand = ((int(hashlib.sha256(all_params_string.encode('utf-8')).hexdigest(), 16) % 10**8)%(RANDOM_SEED)%2)
    possible_tokens.append('%s%s'%(grd_defs.token_prefix,rand))

    return possible_tokens


def generate_benchmarks():


    cmd = 'rm -r %s; mkdir %s' %(destination_folder, destination_folder)
    os.system(cmd)

    for domain_name in ['iss-cad','campus','rovers-min','pucrs-depots','pucrs-depots-min','easy-grid','ipc-grid','block-words','logistics-min','iss-cad','intrusion-detection','intrusion-detection-min','sokoban','zeno-travel','zeno-travel-min','sokoban-min']:

        print('generating behnchmarks for %s'%domain_name)
        # get domain folder
        domain_folder_name = os.path.join(benchmarks_folder, domain_name, BASE_FOLDER_NAME )
	# generate grd problems with various sensors - where the NO is a refinement of the FO problems, POD are refinements of the NO problems, and the POND problems are refinement of the POD problems
        generate_task_instances_refinement_relation(domain_name, domain_folder_name, destination_folder)

if __name__ == '__main__':
    generate_benchmarks()
