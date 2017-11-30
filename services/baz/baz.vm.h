#pragma once
#include "types.h"

byte handler_mix[] = { 0x5, 0x0, 0xd, 0x8, 0xc, 0xa, 0x3, 0xc8, 0x0, 0x0, 0x0, 0xf, 0x6, 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x94, 0x1, 0x0, 0x0, 0xf };
byte handler_mixnew[] = { 0x5, 0x0, 0x9, 0x8, 0xc, 0xa, 0x3, 0xc8, 0x0, 0x0, 0x0, 0xf, 0x6, 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x90, 0x1, 0x0, 0x0, 0xf };
byte handler_memorize[] = { 0x5, 0x0, 0x1, 0x7, 0x7, 0x59, 0x4f, 0x55, 0x52, 0x4d, 0x4f, 0x4d, 0x0, 0x8, 0x2a, 0x6, 0x5, 0x1, 0x9, 0x1, 0xb, 0x1, 0xd, 0x8, 0x1f, 0x3, 0x99, 0x1, 0x0, 0x0, 0xf, 0x6, 0xc, 0x8, 0x40, 0xa, 0x3, 0xc9, 0x0, 0x0, 0x0, 0xf, 0x6, 0x5, 0x1, 0x9, 0x2, 0x1, 0xd, 0x8, 0x1f, 0x6, 0x6, 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x99, 0x1, 0x0, 0x0, 0xf, 0x6, 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x90, 0x1, 0x0, 0x0, 0xf };
byte handler_list[] = { 0x5, 0x1, 0x5, 0x0, 0xe, 0x8, 0xd, 0x3, 0xc8, 0x0, 0x0, 0x0, 0xf, 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x90, 0x1, 0x0, 0x0, 0xf };
byte handler_notfound[] = { 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x94, 0x1, 0x0, 0x0, 0xf };
byte handler_badrequest[] = { 0x3, 0x0, 0x0, 0x0, 0x0, 0x3, 0x90, 0x1, 0x0, 0x0, 0xf };
byte handler_index[] = { 0x4, 0x8, 0x48, 0x69, 0x20, 0x74, 0x68, 0x65, 0x72, 0x65, 0x0, 0x3, 0xc8, 0x0, 0x0, 0x0, 0xf };
