#ifndef HAMMING_H
#define HAMMING_H

#include <stdint.h>
#include <stddef.h>

void hamming_decode(const uint8_t *encoded, size_t encoded_len, uint8_t *decoded, size_t *decoded_len);

#endif