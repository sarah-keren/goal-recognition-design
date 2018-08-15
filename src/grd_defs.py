__author__ = 'sarah'

#imports
import os,sys


#log folders
script_dirname=os.path.dirname(os.path.abspath(__file__))
log_files_dir = os.path.join(script_dirname,"../log_files")
gen_files_dir = os.path.join(script_dirname,"../gen_files")


# a detour - meant to ge the iss domain to work
duplicate_all_predicates = True


#defaults
DEFAULT_TIME_LIMIT = 1800
DEFAULT_MAX_VAL  = 5555555#float("inf")
DEFAULT_MIN_WCD  = -5555555#float("-inf")
TIME_OUT = -888
ERROR = -99999
INFINITE_COST = 88888
INFINITE      = 88888
DELIMINATOR = ','

#fast_downward
if 'src' in os.getcwd():
    downward_path = "./3rdparty/downward/src"
else:
    downward_path = "./src/3rdparty/downward/src"
if "FD_HOME" in os.environ:
    downward_path = os.environ["FD_HOME"] + "/src"

#pyperplan_s
pyper_plan_loaction = os.path.join(script_dirname,'./3rdparty/pyperplan_s')
path = os.path.abspath(os.path.join(pyper_plan_loaction))
if not path in sys.path:
    sys.path.insert(0,path)
del path




#calc methods
WcdBfs = 'WcdBfs'
LatestSplit = 'LatestSplit'
LatestTimed = 'LatestTimed'
LatestExpose = 'LatestExpose'
CommonDeclare = 'CommonDeclare'
WcdReduce = 'WcdReduce'
WcdReduceExhaustive = 'WcdReduceExhaustive'


calc_method_options = [WcdBfs, LatestSplit, LatestTimed, LatestExpose, CommonDeclare, WcdReduce, WcdReduceExhaustive]

#observability

OBSERVABILITY_FO   = 'FO'
OBSERVABILITY_NO   = 'NO'
OBSERVABILITY_POD  = 'POD'
OBSERVABILITY_POND = 'POND'


NON_OBSERVABLE_STRING = 'non-observable'

action_token_file_name = 'act-toks.dat'
non_obs_file_name = 'non-obs.dat'
obs_file_name = 'obs.dat'


#reduction
WcdRedEx = 'WcdRedEx'
WcdRedPruned = 'WcdRedPruned'


# the heuristic used by the fast downward planner
HEURISTIC = 'ipdb()'
#HEURISTIC =  'lmcut()'

CONSTRAINT_DESIGN = True
USE_CLOSED_LIST = True

domain_name = ''
#if DEFAULT_DOMAIN != '':
#    domain_name = '_%s'%DEFAULT_DOMAIN

results_file_name = os.path.join(log_files_dir, 'grd_results%s.txt'%domain_name)

log_file_name_reduction = os.path.join(log_files_dir, 'grd_log_reduction%s.txt'%domain_name)



#specifies the combinations of hyps that can be examined for a given grd problem

# examining each pair seperatly (unordered i,j = j,i)
comb_all_pairs = 'all_pairs'
# examining each pair seperatly (ordered i,j != j,i)
comb_all_ordered_pairs = 'all_ordered_pairs'
# examinning all the hyps togheter
comb_max = 'max'
# examinning all the hyps with a limit of 10 pairs per problem
comb_all_pairs_10 = 'all_pairs_10'
# examinning all the hyps with a limit of 5 pairs per problem
comb_all_pairs_5 = 'all_pairs_5'
# examinning all the hyps with a limit of 30 pairs per problem
comb_rand_30 = 'rand_pairs_30'


comb_examined_options = [comb_all_pairs,comb_all_ordered_pairs,comb_max,comb_all_pairs_10,comb_all_pairs_5,comb_rand_30]

token_prefix = 'AT_'
# indication of non-observability
NON_OBSERVABILITY_STRING = 'non'
NA = 'NA'
NIL_STRING = 'nil'
REFINEMENT_INDEX = 999999
