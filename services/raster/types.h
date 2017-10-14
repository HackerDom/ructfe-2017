#pragma once
#include <cstdint>
#include <xmmintrin.h>
#include <smmintrin.h>

using u8    = uint8_t;
using i8    = int8_t;
using u16   = uint16_t;
using i16   = int16_t;
using u32   = uint32_t;
using i32   = int32_t;
using u64   = uint64_t;
using i64   = int64_t;
using f32   = float;
using f64   = double;

//
union __m128_union
{
    __m128 	f;
    __m128d d;
    __m128i i;
    __m64 	m64[ 2 ];
    u64 m128_u64[ 2 ];
    i64 m128_i64[ 2 ];
    f64 m128_f64[ 2 ];
    u32 m128_u32[ 4 ];
    i32 m128_i32[ 4 ];
    f32 m128_f32[ 4 ];
    u16 m128_u16[ 8 ];
    i16 m128_i16[ 8 ];
    u8 	m128_u8[ 16 ];
    i8 	m128_i8[ 16 ];

    operator __m128() { return f; }
};
