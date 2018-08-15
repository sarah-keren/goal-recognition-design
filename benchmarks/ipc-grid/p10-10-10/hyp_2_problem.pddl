(define (problem ipc-grid-10-10-10)

(:domain grid)
(:objects
place_0_0
place_0_1
place_0_2
place_0_3
place_0_4
place_0_5
place_0_6
place_0_7
place_0_8
place_0_9
place_1_0
place_1_1
place_1_2
place_1_3
place_1_4
place_1_5
place_1_6
place_1_7
place_1_8
place_1_9
place_2_0
place_2_1
place_2_2
place_2_3
place_2_4
place_2_5
place_2_6
place_2_7
place_2_8
place_2_9
place_3_0
place_3_1
place_3_2
place_3_3
place_3_4
place_3_5
place_3_6
place_3_7
place_3_8
place_3_9
place_4_0
place_4_1
place_4_2
place_4_3
place_4_4
place_4_5
place_4_6
place_4_7
place_4_8
place_4_9
place_5_0
place_5_1
place_5_2
place_5_3
place_5_4
place_5_5
place_5_6
place_5_7
place_5_8
place_5_9
place_6_0
place_6_1
place_6_2
place_6_3
place_6_4
place_6_5
place_6_6
place_6_7
place_6_8
place_6_9
place_7_0
place_7_1
place_7_2
place_7_3
place_7_4
place_7_5
place_7_6
place_7_7
place_7_8
place_7_9
place_8_0
place_8_1
place_8_2
place_8_3
place_8_4
place_8_5
place_8_6
place_8_7
place_8_8
place_8_9
place_9_0
place_9_1
place_9_2
place_9_3
place_9_4
place_9_5
place_9_6
place_9_7
place_9_8
place_9_9
- place
key_0
key_1
key_2
key_3
key_4
key_5
key_6
key_7
key_8
key_9
- key
shape_0
shape_1
shape_2
shape_3
shape_4
shape_5
shape_6
shape_7
shape_8
shape_9
- shape
)
(:init
(at-robot place_0_0)
(conn place_0_0 place_0_1) (conn place_0_0 place_1_0)
(conn place_0_1 place_0_0) (conn place_0_1 place_0_2) (conn place_0_1 place_1_1)
(conn place_0_2 place_0_1) (conn place_0_2 place_0_3) (conn place_0_2 place_1_2)
(conn place_0_3 place_0_2) (conn place_0_3 place_0_4) (conn place_0_3 place_1_3)
(conn place_0_4 place_0_3) (conn place_0_4 place_0_5)
(conn place_0_5 place_0_4) (conn place_0_5 place_0_6) (conn place_0_5 place_1_5)
(conn place_0_6 place_0_5) (conn place_0_6 place_0_7) (conn place_0_6 place_1_6)
(conn place_0_7 place_0_6) (conn place_0_7 place_0_8)
(conn place_0_8 place_0_7) (conn place_0_8 place_0_9) (conn place_0_8 place_1_8)
(conn place_0_9 place_0_8)
(conn place_1_0 place_1_1) (conn place_1_0 place_0_0) (conn place_1_0 place_2_0)
(conn place_1_1 place_1_0) (conn place_1_1 place_1_2) (conn place_1_1 place_0_1)
(conn place_1_2 place_1_1) (conn place_1_2 place_1_3) (conn place_1_2 place_0_2)
(conn place_1_3 place_1_2) (conn place_1_3 place_1_4) (conn place_1_3 place_0_3)
(conn place_1_4 place_1_3) (conn place_1_4 place_1_5)
(conn place_1_5 place_1_4) (conn place_1_5 place_1_6) (conn place_1_5 place_0_5)
(conn place_1_6 place_1_5) (conn place_1_6 place_1_7) (conn place_1_6 place_0_6)
(conn place_1_7 place_1_6) (conn place_1_7 place_1_8)
(conn place_1_8 place_1_7) (conn place_1_8 place_1_9) (conn place_1_8 place_0_8)
(conn place_1_9 place_1_8)
(conn place_2_0 place_2_1) (conn place_2_0 place_1_0) (conn place_2_0 place_3_0)
(conn place_2_1 place_2_0) (conn place_2_1 place_2_2) (conn place_2_1 place_3_1)
(conn place_2_2 place_2_1) (conn place_2_2 place_2_3)
(conn place_2_3 place_2_2) (conn place_2_3 place_2_4) (conn place_2_3 place_3_3)
(conn place_2_4 place_2_3) (conn place_2_4 place_2_5)
(conn place_2_5 place_2_4) (conn place_2_5 place_2_6)
(conn place_2_6 place_2_5) (conn place_2_6 place_2_7) (conn place_2_6 place_3_6)
(conn place_2_7 place_2_6) (conn place_2_7 place_2_8)
(conn place_2_8 place_2_7) (conn place_2_8 place_2_9) (conn place_2_8 place_3_8)
(conn place_2_9 place_2_8)
(conn place_3_0 place_3_1) (conn place_3_0 place_2_0) (conn place_3_0 place_4_0)
(conn place_3_1 place_3_0) (conn place_3_1 place_3_2) (conn place_3_1 place_2_1)
(conn place_3_2 place_3_1) (conn place_3_2 place_3_3)
(conn place_3_3 place_3_2) (conn place_3_3 place_3_4) (conn place_3_3 place_2_3)
(conn place_3_4 place_3_3) (conn place_3_4 place_3_5)
(conn place_3_5 place_3_4) (conn place_3_5 place_3_6)
(conn place_3_6 place_3_5) (conn place_3_6 place_3_7) (conn place_3_6 place_2_6)
(conn place_3_7 place_3_6) (conn place_3_7 place_3_8)
(conn place_3_8 place_3_7) (conn place_3_8 place_3_9) (conn place_3_8 place_2_8)
(conn place_3_9 place_3_8)
(conn place_4_0 place_4_1) (conn place_4_0 place_3_0) (conn place_4_0 place_5_0)
(conn place_4_1 place_4_0) (conn place_4_1 place_4_2)
(conn place_4_2 place_4_1) (conn place_4_2 place_4_3) (conn place_4_2 place_5_2)
(conn place_4_3 place_4_2) (conn place_4_3 place_4_4)
(conn place_4_4 place_4_3) (conn place_4_4 place_4_5) (conn place_4_4 place_5_4)
(conn place_4_5 place_4_4) (conn place_4_5 place_4_6)
(conn place_4_6 place_4_5) (conn place_4_6 place_4_7) (conn place_4_6 place_5_6)
(conn place_4_7 place_4_6) (conn place_4_7 place_4_8)
(conn place_4_8 place_4_7) (conn place_4_8 place_4_9)
(conn place_4_9 place_4_8)
(conn place_5_0 place_5_1) (conn place_5_0 place_4_0) (conn place_5_0 place_6_0)
(conn place_5_1 place_5_0) (conn place_5_1 place_5_2)
(conn place_5_2 place_5_1) (conn place_5_2 place_5_3) (conn place_5_2 place_4_2)
(conn place_5_3 place_5_2) (conn place_5_3 place_5_4)
(conn place_5_4 place_5_3) (conn place_5_4 place_5_5) (conn place_5_4 place_4_4)
(conn place_5_5 place_5_4) (conn place_5_5 place_5_6)
(conn place_5_6 place_5_5) (conn place_5_6 place_5_7) (conn place_5_6 place_4_6)
(conn place_5_7 place_5_6) (conn place_5_7 place_5_8)
(conn place_5_8 place_5_7) (conn place_5_8 place_5_9)
(conn place_5_9 place_5_8)
(conn place_6_0 place_6_1) (conn place_6_0 place_5_0) (conn place_6_0 place_7_0)
(conn place_6_1 place_6_0) (conn place_6_1 place_6_2)
(conn place_6_2 place_6_1) (conn place_6_2 place_6_3) (conn place_6_2 place_7_2)
(conn place_6_3 place_6_2) (conn place_6_3 place_6_4) (conn place_6_3 place_7_3)
(conn place_6_4 place_6_3) (conn place_6_4 place_6_5)
(conn place_6_5 place_6_4) (conn place_6_5 place_6_6) (conn place_6_5 place_7_5)
(conn place_6_6 place_6_5) (conn place_6_6 place_6_7) (conn place_6_6 place_7_6)
(conn place_6_7 place_6_6) (conn place_6_7 place_6_8) (conn place_6_7 place_7_7)
(conn place_6_8 place_6_7) (conn place_6_8 place_6_9)
(conn place_6_9 place_6_8)
(conn place_7_0 place_7_1) (conn place_7_0 place_6_0) (conn place_7_0 place_8_0)
(conn place_7_1 place_7_0) (conn place_7_1 place_7_2)
(conn place_7_2 place_7_1) (conn place_7_2 place_7_3) (conn place_7_2 place_6_2)
(conn place_7_3 place_7_2) (conn place_7_3 place_7_4) (conn place_7_3 place_6_3)
(conn place_7_4 place_7_3) (conn place_7_4 place_7_5)
(conn place_7_5 place_7_4) (conn place_7_5 place_7_6) (conn place_7_5 place_6_5)
(conn place_7_6 place_7_5) (conn place_7_6 place_7_7) (conn place_7_6 place_6_6)
(conn place_7_7 place_7_6) (conn place_7_7 place_7_8) (conn place_7_7 place_6_7)
(conn place_7_8 place_7_7) (conn place_7_8 place_7_9)
(conn place_7_9 place_7_8)
(conn place_8_0 place_8_1) (conn place_8_0 place_7_0) (conn place_8_0 place_9_0)
(conn place_8_1 place_8_0) (conn place_8_1 place_8_2)
(conn place_8_2 place_8_1) (conn place_8_2 place_8_3) (conn place_8_2 place_9_2)
(conn place_8_3 place_8_2) (conn place_8_3 place_8_4)
(conn place_8_4 place_8_3) (conn place_8_4 place_8_5) (conn place_8_4 place_9_4)
(conn place_8_5 place_8_4) (conn place_8_5 place_8_6)
(conn place_8_6 place_8_5) (conn place_8_6 place_8_7)
(conn place_8_7 place_8_6) (conn place_8_7 place_8_8) (conn place_8_7 place_9_7)
(conn place_8_8 place_8_7) (conn place_8_8 place_8_9) (conn place_8_8 place_9_8)
(conn place_8_9 place_8_8)
(conn place_9_0 place_9_1) (conn place_9_0 place_8_0)
(conn place_9_1 place_9_0) (conn place_9_1 place_9_2)
(conn place_9_2 place_9_1) (conn place_9_2 place_9_3) (conn place_9_2 place_8_2)
(conn place_9_3 place_9_2) (conn place_9_3 place_9_4)
(conn place_9_4 place_9_3) (conn place_9_4 place_9_5) (conn place_9_4 place_8_4)
(conn place_9_5 place_9_4) (conn place_9_5 place_9_6)
(conn place_9_6 place_9_5) (conn place_9_6 place_9_7)
(conn place_9_7 place_9_6) (conn place_9_7 place_9_8) (conn place_9_7 place_8_7)
(conn place_9_8 place_9_7) (conn place_9_8 place_9_9) (conn place_9_8 place_8_8)
(conn place_9_9 place_9_8)
(open place_0_0)
(open place_0_1)
(open place_0_2)
(open place_0_3)
(open place_0_4)
(locked place_0_5) (lock-shape place_0_5 shape_7)
(locked place_0_6) (lock-shape place_0_6 shape_0)
(open place_0_7)
(open place_0_8)
(open place_0_9)
(open place_1_0)
(open place_1_1)
(open place_1_2)
(open place_1_3)
(open place_1_4)
(open place_1_5)
(open place_1_6)
(open place_1_7)
(open place_1_8)
(open place_1_9)
(open place_2_0)
(open place_2_1)
(locked place_2_2) (lock-shape place_2_2 shape_9)
(open place_2_3)
(open place_2_4)
(open place_2_5)
(locked place_2_6) (lock-shape place_2_6 shape_3)
(locked place_2_7) (lock-shape place_2_7 shape_5)
(open place_2_8)
(open place_2_9)
(open place_3_0)
(open place_3_1)
(open place_3_2)
(open place_3_3)
(open place_3_4)
(open place_3_5)
(open place_3_6)
(locked place_3_7) (lock-shape place_3_7 shape_4)
(open place_3_8)
(open place_3_9)
(open place_4_0)
(open place_4_1)
(open place_4_2)
(open place_4_3)
(open place_4_4)
(open place_4_5)
(open place_4_6)
(open place_4_7)
(open place_4_8)
(open place_4_9)
(open place_5_0)
(open place_5_1)
(locked place_5_2) (lock-shape place_5_2 shape_8)
(open place_5_3)
(open place_5_4)
(open place_5_5)
(open place_5_6)
(open place_5_7)
(open place_5_8)
(open place_5_9)
(open place_6_0)
(open place_6_1)
(open place_6_2)
(open place_6_3)
(open place_6_4)
(open place_6_5)
(open place_6_6)
(open place_6_7)
(open place_6_8)
(open place_6_9)
(open place_7_0)
(open place_7_1)
(open place_7_2)
(open place_7_3)
(open place_7_4)
(open place_7_5)
(open place_7_6)
(open place_7_7)
(open place_7_8)
(open place_7_9)
(open place_8_0)
(locked place_8_1) (lock-shape place_8_1 shape_2)
(open place_8_2)
(locked place_8_3) (lock-shape place_8_3 shape_6)
(open place_8_4)
(open place_8_5)
(open place_8_6)
(open place_8_7)
(open place_8_8)
(open place_8_9)
(open place_9_0)
(open place_9_1)
(open place_9_2)
(locked place_9_3) (lock-shape place_9_3 shape_1)
(open place_9_4)
(open place_9_5)
(open place_9_6)
(open place_9_7)
(open place_9_8)
(open place_9_9)
(at key_0 place_0_0)
(key-shape key_0 shape_0)
(at key_1 place_9_0)
(key-shape key_1 shape_1)
(at key_2 place_7_0)
(key-shape key_2 shape_2)
(at key_3 place_9_0)
(key-shape key_3 shape_3)
(at key_4 place_6_0)
(key-shape key_4 shape_4)
(at key_5 place_9_0)
(key-shape key_5 shape_5)
(at key_6 place_2_0)
(key-shape key_6 shape_6)
(at key_7 place_5_0)
(key-shape key_7 shape_7)
(at key_8 place_7_0)
(key-shape key_8 shape_8)
(at key_9 place_7_0)
(key-shape key_9 shape_9)
)
(:goal
(and
(at-robot place_2_9)
)
)
)
