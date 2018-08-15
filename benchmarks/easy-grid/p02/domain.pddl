;; simple Grid-navigation

(define (domain navigator)

	(:requirements :strips :typing)
	(:types place)
	(:predicates
		(at ?p - place)
		(connected ?p1 ?p2 - place)
	)
	(:action MOVE
		:parameters (?src - place ?dst - place)
		:precondition (and (at ?src) (connected ?src ?dst) )
		:effect (and (at ?dst) (not (at ?src)))
	)
)		
