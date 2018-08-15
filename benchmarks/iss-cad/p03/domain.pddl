;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;      ISS/DSH CREW ACTIVITIES      ;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

(define (domain crew-activities)
  (:requirements :strips :typing :action-costs)
  (:types module crew component system tool part equipment sample)
  (:constants  
	      ;;cdr fe1 fe2 fe3 - crew ;
	      cdr - crew
	      ;; fe - flight engineer
	      ;; cdr - commander

	      Harmony Columbus Destiny Kibo Unity Leonardo Tranquility - module ;; Cupola Kibo-Cargobay Quest
		
	      wrs ars stw galley she fdss epm mares hrf pfs ared cevis colbert altea padles - system ;;shf etc melfi edr biolab saibo
	      ;; wrs - water recycing system
	      ;; ars - atmosphere revitalization system
	      ;; stw - stowage
	      ;; she - sanitation & hygiene equipment
	      ;; fdss - fire detection & supression equipment
	      ;; epm - european physiology module
	      ;; mares - muscle atrophy research exercise system
	      ;; hrf - human research facility
	      ;; pfs - pulmonary function system
	      ;; ared - advance resistive exercise device
	      ;; cevis - cyvle ergometer with vibration isolation system
	      ;; colbert - combined operational load bearing external resistive exercise treadmill
	      ;; altea - anomalous long term effects in astronaut's central nervous system
	      ;; padles - passive dosimeter for lifescience experiments in space

	      food-warmer toilet filter distiller sensor extinguisher ac breathing-equipment cdl meemm sck laptop slammd ultrasound treadmill helmet torso crew-laptop - component ; centrifuge incubator microscope glovebox     
	      ;; cdl - cardiolab
	      ;; meemm - multi electrodes encephalogram measurement module
	      ;; sck - sample collection kit
	      ;; slammd - space linear acceleration mass measurement device
	
	      battery anemometer hygrometer tool-box headligth vacuum-cleaner utensils food cleaning-products holter dosimeter spectrometer catheter sphygmomanometer pulse-oximeter stethoscope electroencephalograph - tool    
	      ;; sphygmomanometer - blood pressure meter
			  
	      water blood unrine salive microbe - sample 
  )
  (:predicates (connected ?m1 ?m2 - module)
	       (at ?c - crew ?m - module)
	       	        
               ;; tools
	       (taken ?t - tool ?c - crew) ;(taken ?t - tool ?c - crew ?m - module)
	       (available ?t - tool ?m - module)
	
	       ;; parts
	       (taken-replacement ?t - component  ?c - crew)
	       (replacement-in ?t - component ?m - module)
	    
	       ;; components
	       (on ?c - component ?s - system ?m - module)
	       (enable ?c - component ?s - system ?m - module)
	       (in ?c - component ?s - system ?m - module)       
	       (inspected ?c - component ?s - system ?m - module ?cr - crew)
	       (replaced ?c - component ?s - system ?m - module ?cr - crew)
	       ;(static ?c - component)
	       ;(attached ?t - component ?c - crew)
	       ;(has-adhesive-pads ?t - component)
	    
	       (airflow-cleaned ?c - crew)
	       (airflow-measured ?c - crew)
	       (humidity-measured ?c - crew)
	       (wrs-repared ?c - crew) ;(wrs-repared ?m - module ?c - crew)
	       (wrs-inspected ?c - crew) ;(wrs-inspected ?m - module ?c - crew)
	       (fdss-inspected ?m - module ?c - crew)
	       (fdss-repared ?m - module ?c - crew)

	       (vacuumed ?m - module ?c - crew)
	       (food-heated ?c - crew)
	       (toilet-cleaned ?c - crew)
	       (food-eaten ?c - crew)
    
	       (sample-taken ?s - sample ?c - crew)
	       (water-sample-analyzed ?c - crew)
	       (blood-sample-analyzed ?c - crew)
	       (microbe-sample-analyzed ?c - crew)
    
	       (heart-rate-measured ?c - crew)
	       (blood-pressure-measured ?c - crew)
	       (brain-activity-measured ?c - crew)
	       (muscle-measured ?c - crew)
	       (skeletal-measure ?c - crew)
	       (tD-image ?c - crew)
	       (mass-measured ?c - crew)
	       (breath-stream-analyzed ?c - crew)

	       (radiation-measured ?cr - crew)
	       (high-pressure-calibrated ?cr - crew)

	       (resistive-exercise-done ?c - crew)
	       (aerobic-exercise-done ?c - crew)
	       (brain-radiation-measured ?c - crew)
	       (body-radiation-measured ?c - crew)

	       (health-ckecked ?c - crew)
	       (oxygen-measured ?c - crew) 
	       (brain-wavees-measured ?c - crew)
	       (health-data-sent ?c - crew)
	       

)

  (:functions (total-cost))

  ;; move
  (:action move
   :parameters (?c - crew ?m1 ?m2 - module)
   :precondition (and (at ?c ?m1) (connected ?m1 ?m2))
   :effect (and (not (at ?c ?m1)) (at ?c ?m2) (increase (total-cost) 1)))

  ;; take a tool from stowage
  (:action take
   :parameters (?t - tool ?m - module ?c - crew)
   :precondition (and (available ?t ?m) (at ?c ?m)) 
   :effect (and (taken ?t ?c) (not (available ?t ?m)) (increase (total-cost) 20))) 

  ;; put-away a tool in stowage
  (:action put-away
   :parameters (?t - tool ?m - module ?c - crew)
   :precondition (and (not (available ?t ?m)) (taken ?t ?c) (at ?c ?m)) 
   :effect (and (not (taken ?t ?c)) (available ?t ?m) (increase (total-cost) 20)))

  ;; take a replacement from stowage
  (:action take-replacement
   :parameters (?t - component ?c - crew)
   :precondition (and (replacement-in ?t Leonardo) (at ?c Leonardo)) 
   :effect (and (taken-replacement ?t ?c) (increase (total-cost) 20))) 
  
  ;; power a component up
  (:action power-up
   :parameters (?o - component ?s - system ?m - module ?c - crew)
   :precondition (and (not (on ?o ?s ?m)) (in ?o ?s ?m) (at ?c ?m)) 
   :effect (and (on ?o ?s ?m) (increase (total-cost) 10)))

  ;; power a component off
  (:action power-off
   :parameters (?o - component ?s - system ?m - module ?c - crew)
   :precondition (and  (on ?o ?s ?m) (in ?o ?s ?m) (at ?c ?m))
   :effect (and (not (on ?o ?s ?m)) (increase (total-cost) 10)))  
  
  ;(:action attach-to-body
  ; :parameters (?o - component ?s - system ?m - module ?c - crew)
  ; :precondition (and  (off ?o ?s ?m) (in ?o ?s ?m) (at ?c ?m) (has-adhesive-pads ?o))
  ; :effect (and (attached ?o ?c) (increase (total-cost) 10)))

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;;;;; SPACECRAFT MAINTENANCE
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;; repare a component
  (:action repare-component 
   :parameters (?o - component ?s - system ?m - module ?c - crew)
   :precondition (and (taken headligth ?c) (taken tool-box ?c) (not (enable ?o ?s ?m)) (not (on ?o ?s ?m)) (in ?o ?s ?m) (at ?c ?m)) 
   :effect (and (enable ?o ?s ?m) (increase (total-cost) 25)))  

  ;; replace a component
  (:action replace-component
   :parameters (?o - component ?s - system ?m - module ?c - crew)
   :precondition (and (taken headligth ?c) (taken tool-box ?c) (taken-replacement ?o ?c) (not (on ?o ?s ?m)) (in ?o ?s ?m) (at ?c ?m)) 
   :effect (and (replaced ?o ?s ?m ?c) (not(taken-replacement ?o ?c)) (increase (total-cost) 20)))
  
  ;; inspect a component
  (:action inspect-component
   :parameters (?o - component ?s - system ?m - module ?c - crew)
   :precondition (and (taken headligth ?c) (taken tool-box ?c) (in ?o ?s ?m) (not (on ?o ?s ?m)) (at ?c ?m)) 
   :effect (and (inspected ?o ?s ?m ?c) (increase (total-cost) 10)))

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;;;;; LAB EXPERIMENTS
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;; analyze sample incubator and centrifuge

  ;(:action take-sample
  ; :parameters (?s - sample ?c - crew )
  ; :precondition (and (on sck epm Columbus) (at ?c Columbus))
  ; :effect (and (sample-taken ?s ?c) (increase (total-cost) 20)))

  ;; predicate for connecting machine to human

  (:action body-oxygen-monitoring
   :parameters (?c - crew)
   :precondition (and (taken pulse-oximeter ?c)) ;(attached pulse-oximeter ?c)
   :effect (and (oxygen-measured ?c) (increase (total-cost) 10)))  

  (:action brain-monitoring
   :parameters (?c - crew)
   :precondition (and (taken electroencephalograph ?c)) ;(attached electroencephalograph ?c)
   :effect (and (brain-wavees-measured ?c) (increase (total-cost) 10)))  

  (:action health-monitoring
   :parameters (?c - crew)
   :precondition (and (heart-rate-measured ?c) (blood-pressure-measured ?c) (oxygen-measured ?c) (brain-wavees-measured ?c))
   :effect (and (health-ckecked ?c)))  ;(increase (total-cost) 10)

  (:action send-health-data
   :parameters (?c - crew)
   :precondition (and (health-ckecked ?c) (on laptop padles Kibo) (at ?c Kibo))
   :effect (and (health-data-sent ?c)  (increase (total-cost) 30)))  

;; EPM - European Physiology Module

  ;; predicate for connecting machine to human

  ;; measure heart rate and blood pressure
  (:action blood-heart--monitoring
   :parameters (?c - crew )
   :precondition (and (at ?c Columbus) (on cdl epm Columbus)) ;(attached cdl ?c)
   :effect (and (blood-pressure-measured ?c) (heart-rate-measured ?c) (increase (total-cost) 50)))
  
  (:action blood-heart-monitoring-holter
   :parameters (?c - crew )
   :precondition (and (taken holter ?c) (at ?c Kibo)) ;(attached holter ?c)
   :effect (and (heart-rate-measured ?c) (blood-pressure-measured ?c) (increase (total-cost) 50)))

  (:action blood-heart-manual-monitoring
   :parameters (?c - crew )
   :precondition (and (taken stethoscope ?c) (taken sphygmomanometer ?c)) ;(attached sphygmomanometer ?c)
   :effect (and (blood-pressure-measured ?c) (increase (total-cost) 40)))
    
  ;; measure electrical activity in the brain
  (:action brain-activity-measuring
   :parameters (?c - crew )
   :precondition (and (on meemm epm Columbus) (at ?c Columbus)) ;(attached meemm ?c)
   :effect (and (brain-activity-measured ?c) (increase (total-cost) 10)))

;; MARES - Muscle Atrophy Research Exercise System

  ;; measure muscle-atrophy
  (:action microgravity-study
   :parameters (?c - crew)
   :precondition (and (on laptop mares Columbus) (at ?c Columbus)) ;(attached mares ?c)
   :effect (and (muscle-measured ?c) (skeletal-measure ?c) (increase (total-cost) 15)))

;; HRF - Human Resource Facilicty

  ;; get ultrasound image
  (:action sonography
   :parameters (?c - crew)
   :precondition (and (on laptop hrf Destiny) (on ultrasound hrf Destiny) (at ?c Destiny))
   :effect (and (tD-image ?c) (increase (total-cost) 15)))

  ;; measure radiation
  (:action dosimetric-mapping-HRF
   :parameters (?c - crew)
   :precondition (and (on laptop hrf Destiny) (taken dosimeter ?c) (at ?c Destiny))
   :effect (and (radiation-measured ?c) (increase (total-cost) 15)))

  ;; supply high-pressure calibration gases
  (:action high-pressure-calibration-D
   :parameters (?c - crew)
   :precondition (and (taken spectrometer ?c) (on laptop hrf Destiny) (not (on sensor hrf Destiny)) (at ?c Destiny)) 
   :effect (and (high-pressure-calibrated ?c) (increase (total-cost) 20))) 

  (:action high-pressure-calibration-C
   :parameters (?c - crew)
   :precondition (and (taken spectrometer ?c) (on laptop pfs Columbus) (not (on sensor pfs Columbus)) (at ?c Columbus)) 
   :effect (and (high-pressure-calibrated ?c) (increase (total-cost) 20)))

  ;; measure and analyze the inhaled and exhaled breath stream
  (:action breath-stream-analysis-D
   :parameters (?c - crew)
   :precondition (and (on laptop hrf Destiny) (on sensor hrf Destiny) (taken catheter ?c) (at ?c Destiny) (high-pressure-calibrated ?c))
   :effect (and (breath-stream-analyzed ?c) (increase (total-cost) 15)))

  (:action breath-stream-analysis-C
   :parameters (?c - crew)
   :precondition (and (on laptop pfs Columbus) (on sensor pfs Columbus) (taken catheter ?c) (at ?c Columbus) (high-pressure-calibrated ?c))
   :effect (and (breath-stream-analyzed ?c) (increase (total-cost) 15)))

  ;; measure on-orbit mass
  (:action measure-mass
   :parameters (?c - crew)
   :precondition (and (on laptop hrf Destiny) (on slammd hrf Destiny) (at ?c Destiny))
   :effect (and (mass-measured ?c) (increase (total-cost) 15)))

;; ARED - Advance Resistive Exercise Device

  ;; resistive exercise
  ;(:action resistive-exercise
  ; :parameters (?c - crew)
  ; :precondition (and (on laptop ared Destiny) (at ?c Destiny))
  ; :effect (and (resistive-exercise-done ?c) (increase (total-cost) 10)))

;; CEVIS - Cycle Ergometer with Vibration Isolation System

  ; aerobic exercise
  (:action aerobic-exercise
   :parameters (?c - crew)
   :precondition (and (on laptop cevis Destiny) (at ?c Destiny))
   :effect (and (aerobic-exercise-done ?c) (increase (total-cost) 10)))

;; COLBERT - Combined Operational Load Bearing External Resistive Exercise Treadmill

  ;; resistive exercise
  (:action resistive-exercise
   :parameters (?c - crew)
   :precondition (and (on laptop colbert Destiny) (on treadmill colbert Destiny) (at ?c Destiny))
   :effect (and (resistive-exercise-done ?c) (increase (total-cost) 10)))

;; ALTEA - Anomalous Long Term Effects in Astronaut's Central Nervous System

  ;; measure radiation
  (:action dosimetric-mapping-AD
   :parameters (?c - crew)
   :precondition (and (on laptop altea Destiny) (at ?c Destiny))
   :effect (and (radiation-measured ?c) (increase (total-cost) 10)))

  (:action dosimetric-mapping-AC
   :parameters (?c - crew)
   :precondition (and (on laptop altea Columbus) (at ?c Columbus))
   :effect (and (radiation-measured ?c) (increase (total-cost) 10)))

  ;; measure radiation and its relation with brain activity
  (:action measure-brain-radiation-AD
   :parameters (?c - crew)
   :precondition (and (on helmet altea Destiny) (on laptop altea Destiny) (at ?c Destiny)) ;(attached helmet ?c)
   :effect (and (brain-radiation-measured ?c) (brain-activity-measured ?c) (increase (total-cost) 10)))

  ;; measure radiation
  (:action measure-brain-radiation-AC
   :parameters (?c - crew)
   :precondition (and (on helmet altea Columbus) (on laptop altea Columbus) (at ?c Columbus)) ;(attached helmet ?c)
   :effect (and (brain-radiation-measured ?c) (brain-activity-measured ?c) (increase (total-cost) 10)))

;; PADLES - PAssive Dosimeter for Lifescience Experiments in Space

  (:action dosimetric-mapping-P
   :parameters (?c - crew)
   :precondition (and (on laptop padles Kibo) (at ?c Kibo))
   :effect (and (radiation-measured ?c) (increase (total-cost) 15)))

  ;; measure radiation
  (:action measure-body-radiation-P
   :parameters (?c - crew)
   :precondition (and (on laptop padles Kibo) (taken dosimeter ?c) (at ?c Kibo))
   :effect (and (body-radiation-measured ?c) (increase (total-cost) 15)))

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;;;;; CQ ECLSS ACTIVITIES -- Crew Quarters Enviromental Control and Life Support System
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;;   water control
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;; water system cleaning
  (:action repair-wrs-distiller
   :parameters (?c - crew ) ;?m - module
   :precondition (and (replaced distiller wrs Tranquility ?c) (on distiller wrs Tranquility) (at ?c Tranquility)) 
   :effect (and (wrs-repared ?c))) ;(wrs-repared ?m ?c) (increase (total-cost) 10)

  (:action repair-wrs-filter
   :parameters (?c - crew ) ;?m - module
   :precondition (and (replaced filter wrs Tranquility ?c) (on filter wrs Tranquility) (at ?c Tranquility))
   :effect (and (wrs-repared ?c))) ;(wrs-repared ?m ?c) (increase (total-cost) 20)
  
  (:action wrs-inspection
   :parameters (?c - crew ) ;?m - module
   :precondition (and  (inspected distiller wrs Tranquility ?c) (inspected filter wrs Tranquility ?c) (at ?c Tranquility))
   :effect (and (wrs-inspected ?c) ))  ;(wrs-inspected ?m ?c)

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;; atmosphere revitalization system
  ;; temperature and humidity and control system
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;; airflow levels measure
  (:action airflow-measuring
   :parameters (?c - crew ?m - module)
   :precondition (and (taken battery ?c) (taken anemometer ?c) (at ?c ?m))
   :effect (and (airflow-measured ?c) (increase (total-cost) 15)))
  
  ;; airflow cleaning
  (:action airflow-cleaning
   :parameters (?c - crew ?m - module)
   :precondition (and (airflow-measured ?c) (replaced filter ars ?m ?c) (on filter ars ?m) (at ?c ?m))
   :effect (and (airflow-cleaned ?c) ))

  ;(:action humidity-measure
  ; :parameters (?c - crew ?m - module)
  ; :precondition (and (taken battery ?c) (taken hygrometer ?c) (at ?c ?m))
  ; :effect (and (humidity-measured ?c) (increase (total-cost) 15)))

  ;; airflow cleaning
  ;(:action airflow-cooling
  ; :parameters (?c - crew ?m - module)
  ; :precondition (and (airflow-measured ?c) (humidity-measured ?c) (inspected filter ars ?m ?c) (on filter ars ?m) (inspected ac ars ?m ?c) 
  ; :effect (and (airflow-cleaned ?c) ))  

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;; fire detection and suppresion system
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  ;; fire detector system
  (:action fdss-repair-sensor
   :parameters (?c - crew ?m - module)
   :precondition (and (replaced sensor fdss ?m ?c) (on sensor fdss ?m) (at ?c ?m))
   :effect (and (fdss-repared ?m ?c) )) ;(increase (total-cost) 15)

  (:action fdss-repair-extinguisher
   :parameters (?c - crew ?m - module)
   :precondition (and (replaced extinguisher fdss ?m ?c) (at ?c ?m))
   :effect (and (fdss-repared ?m ?c) )) ;(increase (total-cost) 15)

  (:action fdss-repair-breathing-equipment
   :parameters (?c - crew ?m - module)
   :precondition (and (replaced breathing-equipment fdss ?m ?c) (at ?c ?m))
   :effect (and (fdss-repared ?m ?c) )) ;(increase (total-cost) 15)

  (:action fdss-inspection
   :parameters (?c - crew ?m - module)
   :precondition (and (inspected sensor fdss ?m ?c) (inspected extinguisher fdss ?m ?c) (inspected breathing-equipment fdss ?m ?c) (at ?c ?m) )
   :effect (and (fdss-inspected ?m ?c) )) 

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ;;;;; HOUSEKEEPING ACTIVITIES
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

  (:action food-warming
   :parameters (?c - crew)
   :precondition (and (taken food ?c) (enable food-warmer galley Unity) (at ?c Unity))
   :effect (and (food-heated ?c) (increase (total-cost) 20)))

  (:action eating-snack
   :parameters (?c - crew)
   :precondition (and (taken food ?c) (taken utensils ?c) (at ?c Unity))
   :effect (and (food-eaten ?c) (increase (total-cost) 20)))

  (:action eating-meal
   :parameters (?c - crew)
   :precondition (and (taken utensils ?c) (food-heated ?c) (at ?c Unity))
   :effect (and (food-eaten ?c) (increase (total-cost) 20)))

  (:action vacuum-module
   :parameters (?c - crew  ?m - module)
   :precondition (and (taken vacuum-cleaner ?c) (at ?c ?m))
   :effect (and (vacuumed ?m ?c) (increase (total-cost) 10)))

  (:action toilet-cleaning
   :parameters (?c - crew)
   :precondition (and (in toilet she Tranquility) (at ?c Tranquility) (taken cleaning-products ?c))
   :effect (and (toilet-cleaned ?c) (increase (total-cost) 15))) 
 
)
