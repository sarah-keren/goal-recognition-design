__author__ = 'sarah'

import grd_utils, os
import datetime
import time

# compares the GRD code with the one presented by Son, Tran Cao, et al. "Solving Goal Recognition Design Using ASP." AAAI. 2016.

code_folder = '/home/sarah/Documents/GoalRecognitionDesign/GRD-JournalPaper/GRD-ASP-package'
behcnhmark_folder = 'final-benchmarks-icaps-2014-asp'
saturation_behcnhmark_folder = 'final-benchmarks-icaps-2014-saturation'

solution_file_name = 'output_asp_wcd'
reduce_output_file = 'output_reduce'
timeout = 1800
memory = 2048

def run_test(prob):

    current_dir = os.getcwd()
    os.chdir(code_folder)
    max_val = 888
    wcd_total_seconds = 999
    reduce_time = 5555


    #FIND
    #cmd =   './clingo wcd/wcd.py final-benchmarks-icaps-2014-asp/easy-grid/p01/template.lp > %s'%solution_file_name
    cmd = './clingo wcd/wcd.py %s/%s/template.lp > %s'%(behcnhmark_folder,prob,solution_file_name)
    signal, time_passed = grd_utils.run(cmd, timeout, memory)

    if signal < 0:
        return [wcd_total_seconds,reduce_time]

    else:

        sol_file = open(os.path.join(code_folder,solution_file_name))
        sol_lines = sol_file.readlines()
        sol_file.close()

        for line in sol_lines:
            if 'Minimal length for all goals  SAT' in line:
                solution_array = line.split('[')[1]
                solution_array = solution_array.replace(']','')
                solution_array = solution_array.replace('\n','')
                solution_array = solution_array.split(',')
                max_val = int(max(solution_array))
            if '+++ Elapsed time: ' in line:
                wcd_exec_time = line.split('+++ Elapsed time:')[1]
                wcd_exec_time = wcd_exec_time.replace('\n','')
                wcd_exec_time = wcd_exec_time.replace(' ','')
                pt = datetime.datetime.strptime(wcd_exec_time,'%H:%M:%S.%f')
                wcd_total_seconds = pt.microsecond/1000000+pt.second+pt.minute*60+pt.hour*3600


        # ANALYZE
        #./clingo meta/brave-py.lp  meta/grdplanner.lp final-benchmarks-icaps-2014-saturation/easy-grid/p01/template.lp -c _t=12 -c tofile=outputfile
        analyze_cmd = './clingo meta/brave-py.lp  meta/grdplanner.lp %s/%s/template.lp -c _t=%d -c tofile=outputfile'%(saturation_behcnhmark_folder,prob, max_val)
        grd_utils.run( analyze_cmd, timeout, memory)

        # REDUCE
        reduce_times = []
        for budget in [3]:
            #./clingo meta/metagrdsatu.lp final-benchmarks-icaps-2014-saturation/easy-grid/p01/template.lp -c _k=2 outputfile
            reduce_cmd = './clingo meta/metagrdsatu.lp %s/%s/template.lp -c _k=%d outputfile'%(saturation_behcnhmark_folder,prob,budget)
            grd_utils.run(reduce_cmd, timeout, memory)
            sol_file = open(os.path.join(code_folder,reduce_output_file))
            sol_lines = sol_file.readlines()
            sol_file.close()
            for line in sol_lines:
                if 'CPU Time: ' in line:
                    reduce_time = line.split('CPU Time     : ')[1]
                    reduce_time = reduce_time.replace('s','')
                    reduce_time = reduce_time.replace('\n','')
                    reduce_time = float(reduce_time)
                    break
            reduce_times.append(reduce_time)


    os.chdir(current_dir)

    return [wcd_total_seconds,reduce_times]


if __name__ == '__main__' :

    results_file_name = os.path.join(code_folder,'asp_results')
    results_file = open(results_file_name,'a+')

    print('easy-grid----------------------')
    for prob in ['p01','p02','p03','p04','p05']:
        print('%s----------------------'%prob)

        time_results = run_test('easy-grid/%s'%(prob))
        results_file.write('%s/easy-grid/%s\n'%(behcnhmark_folder,prob))
        results_file.write('wcd_time---%f\n'%(time_results[0]))
        budget = 1
        for reduce_time in time_results[1]:
            results_file.write('reduce_time_%d-%f\n'%(budget,time_results[0]+reduce_time))
            budget+=1

    print('logistics----------------------')
    for prob in ['p01','p02','p03','p04','p05']:
        print('%s----------------------'%prob)


        time_results = run_test('logistics/%s'%(prob))
        results_file.write('%s/logisitcs/%s\n'%(behcnhmark_folder,prob))
        results_file.write('wcd_time---%f\n'%(time_results[0]))
        budget = 1
        for reduce_time in time_results[1]:
            results_file.write('reduce_time_%d-%f\n'%(budget,time_results[0]+reduce_time))
            budget+=1

    print('block-words----------------------')
    for prob in ['p02','p03']:
        print('%s----------------------'%prob)

        time_results = run_test('block-words/%s'%(prob))
        results_file.write('%s/block-words/%s\n'%(behcnhmark_folder,prob))
        results_file.write('wcd_time---%f\n'%(time_results[0]))
        budget = 1
        for reduce_time in time_results[1]:
            results_file.write('reduce_time_%d-%f\n'%(budget,time_results[0]+reduce_time))
            budget+=1

    print('ipc-grid----------------------')
    for prob in ['p5-5-5','p5-10-10','p10-5-5','p10-10-10']:
        print('%s----------------------'%prob)

        time_results = run_test('ipc-grid-pr-09/%s'%(prob))
        results_file.write('%s/ipc-grid-pr-09/%s\n'%(behcnhmark_folder,prob))
        results_file.write('wcd---time%f\n'%(time_results[0]))
        budget = 1
        for reduce_time in time_results[1]:
            results_file.write('reduce_time_%d-%f\n'%(budget,time_results[0]+reduce_time))
            budget+=1

    results_file.close()


