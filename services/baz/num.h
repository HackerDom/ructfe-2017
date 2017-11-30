#pragma once

uint192 expand(uint64 n);

uint192 add(uint192 a, uint64 b);

uint192 multiply(uint192 a, uint64 b);

uint192 divmod(uint192 a, uint32 b, uint32 *remainder);

bool is_zero(uint192 n);