set r0.xyzw 0.0 0.0 0.0 0.0
set r1.xyzw 4.0 3.0 2.0 1.0
set r2.xyzw 40.0 30.0 20.0 10.0
set r3.xyzw 0.0 0.0 0.0 0.0
set r4.xyzw 0.0 0.0 0.0 0.0
add r0.xyzw r1.xyzw r2.xyzw
add r0.x r1.x r2.y
add r0.yx r1.xw r2.zy
add r0.wy r1.xw r2.zy
dot r0.x r1.xy r2.zw
dot r0.xy r1.xyz r2.zwz
ret