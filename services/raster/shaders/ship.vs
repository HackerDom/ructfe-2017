VS_VARYINGS_NUM 2

dot r0.x i0.xyzw c5.xyzw
dot r0.y i0.xyzw c6.xyzw
dot r0.z i0.xyzw c7.xyzw
dot r0.w i0.xyzw c8.xyzw

dot o0.x r0.xyzw c0.xyzw
dot o0.y r0.xyzw c1.xyzw
dot o0.z r0.xyzw c2.xyzw
dot o0.w r0.xyzw c3.xyzw
mov o1.xyzw i1.xyzw
ret