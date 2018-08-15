(define (domain campus)
	
	(:requirements :strips :typing :action-costs)
	(:types place)

	(:constants
		bank watson_theater hayman_theater davis_theater jones_theater
		bookmark_cafe library cbs psychology_bldg angazi_cafe tav - place
	)
	(:predicates 
		(at ?p - place )
		(banking)
		(lecture-1-taken)
		(lecture-2-taken)
		(lecture-3-taken)
		(lecture-4-taken)
		(group-meeting-1)
		(group-meeting-2)
		(group-meeting-3)
		(coffee)
		(breakfast)
		(lunch)
	)

	(:functions
		(total-cost) - number
	)
	(:action MOVE
		:parameters( ?src - place ?dst - place )
		:precondition (and (at ?src ) )
		:effect ( and
				(at ?dst)
				(increase (total-cost) 1)
				(not (at ?src))
			)
	)
	(:action ACTIVITY-BANKING
		:parameters()
		:precondition (and (at bank))
		:effect (and
				(banking)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-TAKE-LECTURE-1
		:parameters()
		:precondition (and (at watson_theater))
		:effect (and
				(lecture-1-taken)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-TAKE-LECTURE-2
		:parameters()
		:precondition (and (at hayman_theater) (breakfast) (lecture-1-taken))
		:effect (and
				(lecture-2-taken)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-TAKE-LECTURE-3
		:parameters()
		:precondition (and (at davis_theater) (group-meeting-2) (banking))
		:effect	(and
				(lecture-3-taken)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-TAKE-LECTURE-4
		:parameters()
		:precondition (and (at jones_theater) (lecture-3-taken))
		:effect (and
				(lecture-4-taken)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-GROUP-MEETING-1
		:parameters()
		:precondition (and (at bookmark_cafe) (lecture-1-taken) (breakfast))
		:effect (and
				(group-meeting-1)
				(increase (total-cost) 1)
			) 
	)
	(:action ACTIVITY-GROUP-MEETING-11
		:parameters()
		:precondition (and (at library) (lecture-1-taken) (breakfast))
		:effect (and
				(group-meeting-1)
				(increase (total-cost) 1)
			) 
	)
	(:action ACTIVITY-GROUP-MEETING-111
		:parameters()
		:precondition (and (at cbs) (lecture-1-taken) (breakfast))
		:effect (and
				(group-meeting-1)
				(increase (total-cost) 1)
			) 
	)
	(:action ACTIVITY-GROUP-MEETING-2
		:parameters()
		:precondition (and (at library))
		:effect (and
				(group-meeting-2)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-GROUP-MEETING-22
		:parameters()
		:precondition (and (at cbs))
		:effect (and
				(group-meeting-2)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-GROUP-MEETING-222
		:parameters()
		:precondition (and (at psychology_bldg))
		:effect (and
				(group-meeting-2)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-GROUP-MEETING-3
		:parameters()
		:precondition (and (at angazi_cafe) (lecture-4-taken))
		:effect (and
				(group-meeting-3)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-GROUP-MEETING-33
		:parameters()
		:precondition (and (at psychology_bldg) (lecture-4-taken))
		:effect (and
				(group-meeting-3)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-COFFEE
		:parameters()
		:precondition (and (at tav) (lecture-2-taken) (group-meeting-1))
		:effect (and
				(coffee)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-COFFEE1
		:parameters ()
		:precondition (and (at angazi_cafe) (lecture-2-taken) (group-meeting-1))
		:effect (and
				(coffee)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-COFFEE2
		:parameters ()
		:precondition (and (at bookmark_cafe) (lecture-2-taken) (group-meeting-1))
		:effect (and
				(coffee)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-BREAKFAST
		:parameters()
		:precondition (and (at tav))
		:effect (and
				(breakfast)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-BREAKFAST1
		:parameters ()
		:precondition (and (at angazi_cafe))
		:effect (and
				(breakfast)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-BREAKFAST2
		:parameters ()
		:precondition (and (at bookmark_cafe))
		:effect (and
				(breakfast)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-LUNCH
		:parameters ()
		:precondition (and (at tav))
		:effect (and
				(lunch)
				(increase (total-cost) 1)
			)
	)
	(:action ACTIVITY-LUNCH2
		:parameters ()
		:precondition (and (at bookmark_cafe))
		:effect (and
				(lunch)
				(increase (total-cost) 1)
			)
	)
)
