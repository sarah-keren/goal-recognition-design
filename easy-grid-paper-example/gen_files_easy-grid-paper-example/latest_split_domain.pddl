(define (domain navigator)


(:requirements :strips :typing :action-costs  :equality)


(:types place - object
agent - object
)


(:constants
 agent_0 agent_1 - agent
)

(:predicates 
(at ?p - place ?a - agent)
(connected ?p1 - place ?p2 - place ?a - agent)
(split)
(ag0_done)
)



(:functions (total-cost) - number)


(:action move_together 
 :parameters ( ?src - place ?dst - place) 
 :precondition (and (at  ?src agent_0)(at  ?src agent_1)(connected  ?src ?dst agent_0)(connected  ?src ?dst agent_1)(not(split) )) 
 :effect (and (at  ?dst agent_0)(at  ?dst agent_1)(increase (total-cost) 19980 )(not (at  ?src agent_0))(not (at  ?src agent_1))) 
) 

(:action move_seperate_#0 
 :parameters ( ?src - place ?dst - place) 
 :precondition (and (at  ?src agent_0)(connected  ?src ?dst agent_0)(split )(not(ag0_done) )) 
 :effect (and (at  ?dst agent_0)(increase (total-cost) 10000 )(not (at  ?src agent_0))) 
) 

(:action move_seperate_#1 
 :parameters ( ?src - place ?dst - place) 
 :precondition (and (at  ?src agent_1)(connected  ?src ?dst agent_1)(split )(ag0_done )) 
 :effect (and (at  ?dst agent_1)(increase (total-cost) 10000 )(not (at  ?src agent_1))) 
) 

(:action split-agents 
 :parameters () 
 :precondition (and (not(split) )) 
 :effect (and (split )(increase (total-cost) 0 )) 
) 

(:action agent-0-done 
 :parameters () 
 :precondition (and (not(ag0_done) )(split )) 
 :effect (and (ag0_done )(increase (total-cost) 0 )) 
) 

)
