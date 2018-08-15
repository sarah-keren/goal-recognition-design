(define (problem Simple_Room_1)

(:domain navigator)
(:objects
place_3_14
place_5_9
place_2_5
place_5_10
place_3_10
place_3_3
place_4_13
place_3_8
place_2_8
place_4_9
place_2_13
place_3_7
place_2_4
place_5_11
place_4_5
place_3_11
place_4_12
place_5_6
place_2_7
place_3_4
place_2_12
place_4_7
place_5_3
place_2_3
place_3_9
place_4_4
place_4_8
place_5_12
place_5_7
place_2_6
place_3_12
place_4_11
place_3_5
place_5_4
place_5_13
place_5_8
place_2_14
place_4_6
place_4_3
place_3_13
place_3_6
place_4_10
place_2_10
place_5_14
place_5_5
place_2_9
place_4_14
place_2_11
- place
)
(:init
(connected place_3_14 place_3_13) (connected place_3_14 place_2_14) (connected place_3_14 place_4_14)
(connected place_5_9 place_5_8) (connected place_5_9 place_5_10) (connected place_5_9 place_4_9)
(connected place_2_5 place_2_4) (connected place_2_5 place_2_6) (connected place_2_5 place_3_5)
(connected place_5_10 place_5_9) (connected place_5_10 place_5_11) (connected place_5_10 place_4_10)
(connected place_3_10 place_3_9) (connected place_3_10 place_3_11) (connected place_3_10 place_2_10) (connected place_3_10 place_4_10)
(connected place_3_3 place_3_4) (connected place_3_3 place_2_3) (connected place_3_3 place_4_3)
(connected place_4_13 place_4_12) (connected place_4_13 place_4_14) (connected place_4_13 place_3_13) (connected place_4_13 place_5_13)
(connected place_3_8 place_3_7) (connected place_3_8 place_3_9) (connected place_3_8 place_2_8) (connected place_3_8 place_4_8)
(connected place_2_8 place_2_7) (connected place_2_8 place_2_9) (connected place_2_8 place_3_8)
(connected place_4_9 place_4_8) (connected place_4_9 place_4_10) (connected place_4_9 place_3_9) (connected place_4_9 place_5_9)
(connected place_2_13 place_2_12) (connected place_2_13 place_2_14) (connected place_2_13 place_3_13)
(connected place_3_7 place_3_6) (connected place_3_7 place_3_8) (connected place_3_7 place_2_7) (connected place_3_7 place_4_7)
(connected place_2_4 place_2_3) (connected place_2_4 place_2_5) (connected place_2_4 place_3_4)
(connected place_5_11 place_5_10) (connected place_5_11 place_5_12) (connected place_5_11 place_4_11)
(connected place_4_5 place_4_4) (connected place_4_5 place_4_6) (connected place_4_5 place_3_5) (connected place_4_5 place_5_5)
(connected place_3_11 place_3_10) (connected place_3_11 place_3_12) (connected place_3_11 place_2_11) (connected place_3_11 place_4_11)
(connected place_4_12 place_4_11) (connected place_4_12 place_4_13) (connected place_4_12 place_3_12) (connected place_4_12 place_5_12)
(connected place_5_6 place_5_5) (connected place_5_6 place_5_7) (connected place_5_6 place_4_6)
(connected place_2_7 place_2_6) (connected place_2_7 place_2_8) (connected place_2_7 place_3_7)
(connected place_3_4 place_3_3) (connected place_3_4 place_3_5) (connected place_3_4 place_2_4) (connected place_3_4 place_4_4)
(connected place_2_12 place_2_11) (connected place_2_12 place_2_13) (connected place_2_12 place_3_12)
(connected place_4_7 place_4_6) (connected place_4_7 place_4_8) (connected place_4_7 place_3_7) (connected place_4_7 place_5_7)
(connected place_5_3 place_5_4) (connected place_5_3 place_4_3)
(connected place_2_3 place_2_4) (connected place_2_3 place_3_3)
(connected place_3_9 place_3_8) (connected place_3_9 place_3_10) (connected place_3_9 place_2_9) (connected place_3_9 place_4_9)
(connected place_4_4 place_4_3) (connected place_4_4 place_4_5) (connected place_4_4 place_3_4) (connected place_4_4 place_5_4)
(connected place_4_8 place_4_7) (connected place_4_8 place_4_9) (connected place_4_8 place_3_8) (connected place_4_8 place_5_8)
(connected place_5_12 place_5_11) (connected place_5_12 place_5_13) (connected place_5_12 place_4_12)
(connected place_5_7 place_5_6) (connected place_5_7 place_5_8) (connected place_5_7 place_4_7)
(connected place_2_6 place_2_5) (connected place_2_6 place_2_7) (connected place_2_6 place_3_6)
(connected place_3_12 place_3_11) (connected place_3_12 place_3_13) (connected place_3_12 place_2_12) (connected place_3_12 place_4_12)
(connected place_4_11 place_4_10) (connected place_4_11 place_4_12) (connected place_4_11 place_3_11) (connected place_4_11 place_5_11)
(connected place_3_5 place_3_4) (connected place_3_5 place_3_6) (connected place_3_5 place_2_5) (connected place_3_5 place_4_5)
(connected place_5_4 place_5_3) (connected place_5_4 place_5_5) (connected place_5_4 place_4_4)
(connected place_5_13 place_5_12) (connected place_5_13 place_5_14) (connected place_5_13 place_4_13)
(connected place_5_8 place_5_7) (connected place_5_8 place_5_9) (connected place_5_8 place_4_8)
(connected place_2_14 place_2_13) (connected place_2_14 place_3_14) (at place_2_14)
(connected place_4_6 place_4_5) (connected place_4_6 place_4_7) (connected place_4_6 place_3_6) (connected place_4_6 place_5_6)
(connected place_4_3 place_4_4) (connected place_4_3 place_3_3) (connected place_4_3 place_5_3)
(connected place_3_13 place_3_12) (connected place_3_13 place_3_14) (connected place_3_13 place_2_13) (connected place_3_13 place_4_13)
(connected place_3_6 place_3_5) (connected place_3_6 place_3_7) (connected place_3_6 place_2_6) (connected place_3_6 place_4_6)
(connected place_4_10 place_4_9) (connected place_4_10 place_4_11) (connected place_4_10 place_3_10) (connected place_4_10 place_5_10)
(connected place_2_10 place_2_9) (connected place_2_10 place_2_11) (connected place_2_10 place_3_10)
(connected place_5_14 place_5_13) (connected place_5_14 place_4_14)
(connected place_5_5 place_5_4) (connected place_5_5 place_5_6) (connected place_5_5 place_4_5)
(connected place_2_9 place_2_8) (connected place_2_9 place_2_10) (connected place_2_9 place_3_9)
(connected place_4_14 place_4_13) (connected place_4_14 place_3_14) (connected place_4_14 place_5_14)
(connected place_2_11 place_2_10) (connected place_2_11 place_2_12) (connected place_2_11 place_3_11)
)
(:goal
(and
<HYPOTHESIS>
)
)
)
