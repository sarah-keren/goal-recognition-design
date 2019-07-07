__author__ = 'sarah'


RESULT_FILE_NAME = 'sas_plan'
#FAILURE_CODE = -999
#NO_SOL_CODE = -1
#importl sys,os,csv

verbose = False

import grd_defs,grd_utils
import sys,os,csv



"""
Activating the fast downward planner with domain_file_name and problem_file_name and output the result to destination_folder
"""
def perform_planning(destination_folder,domain_file_name,problem_file_name, time_limit = grd_defs.DEFAULT_TIME_LIMIT, heuristic = 'lmcut()') :#heuristic = 'ipdb()'):

        print('\nIn perform_planning with domain %s and problem %s time_limit = %d'%(domain_file_name,problem_file_name,time_limit))
        print('-----------------------------------------------------------')

        planning_failed = False
        plan_cmd = downward_command(destination_folder, domain_file_name, problem_file_name,time_limit,'', heuristic)
        signal = plan_cmd.execute()

        if(plan_cmd.plan_cost < -1):
            print('plan_for %s and %s == failed'%(domain_file_name,problem_file_name))
            planning_failed = True
        else:
            if((plan_cmd.plan_cost == -1 )):
                print('plan_for %s and %s == no_solution'%(domain_file_name,problem_file_name))
                planning_failed= True

        return [plan_cmd,planning_failed,signal]

"""
The fast downward command :
"""
class downward_command :
    """fast downward command
    website: http://www.fast-downward.org/

    requirements:
    -python 2.7
    -fast downward installed in grd_defs.downward_path

    """

    def __init__( self,destination_folder_name, domainfilename, problemfilename,max_time = grd_defs.DEFAULT_TIME_LIMIT,upper_bound= '' ,heuristic = 'lmcut()' , max_mem = 2048 ) :
        self.domain_file_name  = os.path.abspath(domainfilename)
        self.problem_file_name = os.path.abspath(problemfilename)
        self.noext_problem = os.path.basename(self.problem_file_name).replace( '.pddl', '' )
        self.max_time = max_time
        self.max_mem = max_mem
        self.heuristic = heuristic
        self.upper_bound = upper_bound
        self.plan_cost = 0
        self.signal = 0
        self.destination_folder_name = destination_folder_name
        self.num_expanded_states = -1


    def execute(self) :
        """executing fast downward search command via 3 steps:
            --Translate
            --Preporocess
            --Search
           result is processed in gather_data
        """
	#command
        cmd_string_planner = '%s/fast-downward.py %s %s --search "astar(lmcut())"'%(os.path.abspath(grd_defs.downward_path), self.domain_file_name,self.problem_file_name)
        search_log_file_name = os.path.abspath(os.path.join(grd_defs.log_files_dir,'Search_downward.log'))#%(self.noext_problem,int(time.time()))))


        # Change working directory to the one in which all files are generated
        cur_dir = os.getcwd()
        os.chdir(self.destination_folder_name)
	
	
        
        #Search
        self.log_file_name = search_log_file_name
        self.log = grd_utils.Log(self.log_file_name)
        self.signal, self.time = grd_utils.run( cmd_string_planner, self.max_time, self.max_mem, self.log ,verbose)
        print("----------------------------------------------> Search performed with signal %s ,log file name is %s"%(self.signal,search_log_file_name))

        if(self.signal != 0):
            print("! ! ! signal is not 0 - it is %d"%self.signal)


        os.chdir(cur_dir)

        #process results
        self.gather_data()
        return self.signal


    def execute_deprecated(self) :
        """executing fast downward search command via 3 steps:
            --Translate
            --Preporocess
            --Search
           result is processed in gather_data
        """
	

        #commands
        cmd_string_translate = 'python2.7 %s/translate/translate.py %s %s' %(os.path.abspath(grd_defs.downward_path),self.domain_file_name,self.problem_file_name)
        print('cmd string is %s'%cmd_string_translate)
        cmd_string_preprocess = '%s/preprocess/preprocess < output.sas' %(os.path.abspath(grd_defs.downward_path))
        print('cmd string is %s'%cmd_string_preprocess)
        cmd_string_search = '%s/search/downward --search "astar(%s)" < output'%(os.path.abspath(grd_defs.downward_path),self.heuristic)
        print('cmd string is %s'%cmd_string_search)


        #log_files
        translate_log_file_name = os.path.abspath(os.path.join(grd_defs.log_files_dir,'Translate_downward.log'))#%self.noext_problem))
        preprocess_log_file_name = os.path.abspath(os.path.join(grd_defs.log_files_dir,'Preprocess_downward.log'))#%self.noext_problem))
        search_log_file_name = os.path.abspath(os.path.join(grd_defs.log_files_dir,'Search_downward.log'))#%(self.noext_problem,int(time.time()))))


        # Change working directory to the one in which all files are generated
        cur_dir = os.getcwd()
        os.chdir(self.destination_folder_name)


        # Translate
        self.log_file_name = translate_log_file_name
        self.log = grd_utils.Log(self.log_file_name)
        #run Translate command
        self.signal, self.time = grd_utils.run( cmd_string_translate, self.max_time, self.max_mem, self.log ,verbose)
        print("----------------------------------------------> Translate performed with signal %s, log file name is %s"%(self.signal,translate_log_file_name))


        if(self.signal != 0):
            #import sys
            #sys.exit(1)
            print('failed translate with signal %d'%self.signal)
            os.chdir(cur_dir)
            return self.signal


        # Preprocess
        self.log_file_name = preprocess_log_file_name
        self.log = grd_utils.Log(self.log_file_name)
        #run Preprocess command
        self.signal, self.time = grd_utils.run( cmd_string_preprocess, self.max_time, self.max_mem, self.log ,verbose)
        print("----------------------------------------------> Preprocess performed with signal %s ,log file name is %s"%(self.signal,preprocess_log_file_name))

        if(self.signal != 0):
            #import sys
            #sys.exit(1)
            print('failed pre-process with signal %d'%self.signal)
            os.chdir(cur_dir)
            return self.signal

        #Search
        self.log_file_name = search_log_file_name
        self.log = grd_utils.Log(self.log_file_name)
        self.signal, self.time = grd_utils.run( cmd_string_search, self.max_time, self.max_mem, self.log ,verbose)
        print("----------------------------------------------> Search performed with signal %s ,log file name is %s"%(self.signal,search_log_file_name))

        if(self.signal != 0):
            print("! ! ! signal is not 0 - it is %d"%self.signal)


        os.chdir(cur_dir)

        #process results
        self.gather_data()
        return self.signal




    def gather_data( self ) :
       '''
       analyzing the log file generated by the fast dowanrd command:  Search_downward.log
       :return:NIL
       '''
       if os.path.exists( self.log_file_name ) :
            instream = open(self.log_file_name,'r')

            self.plan_cost = -999
            for line in instream :

                line = line.strip()
                if 'Completely explored state space -- no solution!' in line :
                    self.plan_cost = -1


                if 'Plan cost:' in line :
                    toks = line.split()
                    self.plan_cost = (int)(toks[-1])

                if 'Total time:' in line :
                    toks = line.split()
                    time = (int)(toks[-1])
                    self.time = time.replace("s", "")


                if 'Expanded' in line and 'state(s).' in line :
                    toks = line.split()
                    self.num_expanded_states = int(toks[1])
                    break

            #if the solution is failed return the signal
            if self.plan_cost <  -1:
                self.plan_cost = -1 * self.signal

            instream.close()

       #Process solution files (sas_plan)
       sol_file_name = os.path.join(self.destination_folder_name,'sas_plan')
       self.solution_seq = []
       action_counter = 0
       if os.path.exists( self.log_file_name ) :

           #no solution found
           if not os.path.exists(sol_file_name):
               print('no solution found!!!!!!!!')

           else:
               sol_file  = open(sol_file_name)
               for line in sol_file:

                   action_counter += 1
                   line = line.strip()
                   action = line.replace('','')
                   self.solution_seq.append(action)

               sol_file.close()

    def write_result( self, filename ) :

        res = csv.writer(  open( '%s'%filename, 'w' ) )

        res.writerow( [ os.path.basename(self.domain_file_name), os.path.basename(self.problem_file_name), self.signal, self.time, self.plan_cost ] )


def test_perform_planning():

    grd_utils.empty_or_create_log_and_gen_dir()
    
    if len(sys.argv) >3:
        heuristic = sys.argv[2]
    else:
        heuristic = grd_defs.HEURISTIC

    print('heuristic: %s'%heuristic)	
    perform_planning(grd_defs.log_files_dir,sys.argv[1],sys.argv[2],grd_defs.DEFAULT_TIME_LIMIT,heuristic )
    
    

	



if __name__ == '__main__' :

    test_perform_planning();


