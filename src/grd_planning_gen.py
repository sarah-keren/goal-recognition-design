__author__ = 'sarah'


import os
import grd_defs

#imports from pypaerplan_s
from pddl import parser
from pddl import pddl

'''
Generates classical planning files
'''
def generate_domain_file(planning_domain,output_domain_file_name,requirements_string='',functions_string='',constants_string=''):

    '''
    generates a pddl domain file

    @param All textual inputs including a planning_domain defined by pyperplan_s in the 3rdparty includes
    @return: The path to the generated file
    '''

    outstream = open(output_domain_file_name, 'w')

    #add define
    define_line = '(define (domain %s)'%planning_domain.name
    print(define_line,file = outstream)
    print('\n',file = outstream)


    #add requirements
    req_line = ''
    if '' != requirements_string:
        req_line = '(:requirements '+ requirements_string +')'

    else:
        req_line = '(:requirements '
        for req in planning_domain.requirements:
            req_line += " :"+ req
        req_line += ')'

    print(req_line,file = outstream)
    print('\n',file = outstream)

    # add types
    types_string = '(:types '

    for type_name in planning_domain.types:
            if type_name != 'object':
                cur_type = planning_domain.types[type_name]
                types_string += cur_type.name
                types_string += ' - '
                types_string += cur_type.parent.name
                types_string += '\n'
    types_string += ')'
    print(types_string,file = outstream)
    print('\n',file = outstream)

    #constants
    if constants_string == '':
        constants_string += '(:constants \n'
        for constant in planning_domain.constants.keys():
            constants_string += '%s - %s\n'%(constant, planning_domain.constants[constant])
        constants_string += '\n ) \n'

    print(constants_string,file = outstream)

    #add predicates
    predicates_string = '(:predicates \n'
    for predicate_name in planning_domain.predicates.keys():



        predicate = planning_domain.predicates[predicate_name]
        predicate_string = '(%s'%predicate_name
        parameters_string  = ''
        for parameter in predicate.signature:
            parmater_name = '%s'%(parameter[0])
            parameters_type = '%s'%(parameter[1])
            parameter_string_to_add = ' %s - %s'%(parmater_name,parameters_type)
            parameters_string +=  parameter_string_to_add
        predicate_string +=  '%s)\n' %parameters_string
        predicates_string += predicate_string

    #add closing parenthesis
    predicates_string += ')\n'
    predicates_string += ''
    print(predicates_string,file = outstream)
    print('\n',file = outstream)

    #add functions
    func_line = ''
    if '' != functions_string:
        func_line = functions_string
    else:
        if planning_domain.actionCosts :
            func_line = '(:functions (total-cost))'
    print(func_line,file = outstream)
    print('\n',file = outstream)



    #add actions
    for action_name in planning_domain.actions.keys():

        action_string =  '(:action %s \n' %action_name
        action = planning_domain.actions[action_name]

        #:parameters
        parameters_string = ' :parameters ('
        for parameter in action.signature:
            parmater_name = '%s'%(parameter[0])
            parameters_type = '%s'%(parameter[1])
            parameter_string_to_add = ' %s - %s'%(parmater_name,parameters_type)
            parameters_string +=  parameter_string_to_add

        action_string += parameters_string
        action_string += ') \n'


        #:precondition
        precond_string = ' :precondition (and '


        for predicate in action.precondition:

            predicate_string = get_predicate_string(predicate,False)
            precond_string +=  predicate_string


        action_string += precond_string
        action_string += ') \n'


        #:effect
        effect_string = ' :effect (and '

        for predicate in action.effect.addlist:

            predicate_string = get_predicate_string(predicate,False)
            effect_string +=  predicate_string

        for predicate in action.effect.dellist:

            predicate_string = get_predicate_string(predicate,True)
            effect_string +=  predicate_string


        action_string += effect_string
        action_string += ') \n'


        #close action
        action_string += ') \n'


        print(action_string,file = outstream)

    #close file
    print(')',file = outstream)

    return output_domain_file_name

def get_predicate_string(predicate,bNot):

    predicate_string = ''
    predicate_string += '('

    if bNot or predicate.IsNot == True:
        predicate_string += 'not ('

    predicate_name = predicate.name
    predicate_signature = predicate.signature

    predicate_parameters = ''
    for param in predicate_signature:
        predicate_parameters += ' '
        if 'total-cost' in param:
            totalcostString = '('+param[0]+')'
            predicate_parameters += totalcostString
        else:
            predicate_parameters += param[0]

    predicate_string += '%s %s'%(predicate_name,predicate_parameters)

    predicate_string += ')'

    if bNot or predicate.IsNot == True:
        predicate_string += ')'


    return predicate_string

def parse_domain_file(domain_file_name):

    #create a PRD domain
    pddl_parser = parser.Parser(domain_file_name)
    planning_domain = pddl_parser.parse_domain()
    return planning_domain

def generate_current_problem_file(current_hyp,grd_node,template_file_name,destination_folder_name,hyp_index,iteration_num,grd_task):

    #generate init state
    current_initial_state = None
    if grd_node != None:
        current_initial_state = grd_node.state


    #open template file
    instream_template  = open(template_file_name)

    #open destination file
    current_problem_file_name = os.path.join(destination_folder_name,'current_problem_%d_%d.pddl'%(hyp_index,iteration_num))


    with open(current_problem_file_name, 'w') as outstream:

        goal_line_reached = False

        line = instream_template.readline()

        while goal_line_reached == False:


            if( goal_line_reached == True):
                break
            else:

                if '<HYPOTHESIS>' in line :
                    print('generating goal')
                    line_to_print = generate_goal(current_hyp)
                    goal_line_reached = True
                    while line:
                        line = instream_template.readline()
                        if 'metric minimize' in line:
                            line_to_print += '(:metric minimize (total-cost))\n'

                    line_to_print += ')'
                #lines that are not hyp
                else:
                    if '(:init' in line and current_initial_state != None:

                        line_to_print = generate_init_state(line,instream_template,current_initial_state,grd_task)

                    else:
                        line_to_print = line


            print(line_to_print,file = outstream)

            line = instream_template.readline()

    outstream.close()
    instream_template.close()
    return current_problem_file_name

def generate_init_state(init_line,instream_template,current_init_state,grd_model):

    #get the entire init statement from the file whose end is indicated by a ')\n'
    init_statement = ''
    next_line = instream_template.readline()
    while ')\n' != next_line :
        init_statement = init_statement + next_line
        next_line = instream_template.readline()

    #remove all newlines - giving us a statement with predicates
    init_statement = init_statement.replace('\n',"")


    #initialize the init to be printed
    init_to_print = ''
    init_to_print += init_line + '\n'
    #for pred in init_statement.split('\n') :
    for line in init_statement.split('(') :
        #if the line is empty - continue to the next line
        if line == '':
            continue
        #stripped_var =  line.replace(')','')
        #stripped_var =  stripped_var.replace('(','')


        #check if the predicate needs to be duplicated
        isStatic = False
        for pred in grd_model.static_predicates:
            if pred.lower() in line.lower() :
                isStatic = True

        #only if the predicate belongs to the list of the ones to be duplicated
        #if isStatic == True:
        line = line.replace('(','')
        init_to_print += '('+line

    current_init_state_to_print = ''
    for predicate in current_init_state:
        current_init_state_to_print += predicate


    init_to_print = '\n'+ init_to_print + current_init_state_to_print +'\n'+')' +'\n'




    return init_to_print

def generate_goal(hyp):

    new_goal_statement=''
    for atom in hyp.atoms:

        #after the goal we need to add the metric minimization and end the file with the approriate ')'
        new_goal_statement += atom


    new_goal_statement+= '\n )\n'+')\n'

    return new_goal_statement

def parse_problem_file(problem_file_name,domain_file_name):
    '''
    Create a problem object
    :param problem_file_name:
    :param domain_file_name:
    :return:
    '''

    #generate_domain
    pddl_domain = parse_domain_file(domain_file_name)

    #Create the grounded problem
    pddl_parser = parser.Parser(domain_file_name,problem_file_name)
    print("domain file name:", domain_file_name, " problem file name", problem_file_name)
    planning_problem = pddl_parser.parse_problem(pddl_domain)

    return planning_problem


def test_generate_planning_files():
    import sys

    #parse domain and problem files
    #sys.argv[1] = domain file sys.argv[2] = problem file
    pddl_parser = parser.Parser(sys.argv[1],sys.argv[2])

    planning_domain = pddl_parser.parse_domain()
    requirements_string = ''
    functions_string = ''
    constants_string = ''

    domain_file_name = os.path.join(grd_defs.gen_files_dir,"new_domain.pddl")
    generate_domain_file(planning_domain,domain_file_name,requirements_string,functions_string,constants_string)





if __name__ == '__main__' :

    import grd_utils
    grd_utils.empty_or_create_log_and_gen_dir()

    test_generate_planning_files();
