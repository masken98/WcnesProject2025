#include "hamming.h"

static uint8_t correct_and_decode(uint8_t byte) {
    // Positions: p0, p1, d3, p2, d2, d1, d0
    uint8_t p0 = (byte >> 6) & 1;
    uint8_t p1 = (byte >> 5) & 1;
    uint8_t d3 = (byte >> 4) & 1;
    uint8_t p2 = (byte >> 3) & 1;
    uint8_t d2 = (byte >> 2) & 1;
    uint8_t d1 = (byte >> 1) & 1;
    uint8_t d0 = (byte >> 0) & 1;

    uint8_t s0 = p0 ^ d3 ^ d1 ^ d0;
    uint8_t s1 = p1 ^ d3 ^ d2 ^ d0;
    uint8_t s2 = p2 ^ d2 ^ d1 ^ d0;

    uint8_t syndrome = (s2 << 2) | (s1 << 1) | s0;

    if (syndrome != 0) {
        // Correct single-bit error
        if (syndrome <= 7) {
            byte ^= (1 << (7 - syndrome)); 
        }
    }

    // Extract corrected data bits
    d3 = (byte >> 4) & 1;
    d2 = (byte >> 2) & 1;
    d1 = (byte >> 1) & 1;
    d0 = (byte >> 0) & 1;

    return (d3 << 3) | (d2 << 2) | (d1 << 1) | d0;
}

void hamming_decode(const uint8_t *encoded, size_t encoded_len, uint8_t *decoded, size_t *decoded_len) {
    if (encoded_len % 2 != 0) {
        // Invalid length
        *decoded_len = 0;
        return;
    }

    *decoded_len = encoded_len / 2;
    for (size_t i = 0; i < *decoded_len; i++) {
        uint8_t high = correct_and_decode(encoded[2*i]);
        uint8_t low = correct_and_decode(encoded[2*i+1]);
        decoded[i] = (high << 4) | low;
    }
}
