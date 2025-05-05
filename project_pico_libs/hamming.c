#include "hamming.h"

static uint8_t correct_and_decode(uint8_t byte) {
    // p1 p2 d0 p3 d1 d2 d3
    uint8_t p1 = (byte >> 6) & 1;
    uint8_t p2 = (byte >> 5) & 1;
    uint8_t d0 = (byte >> 4) & 1;
    uint8_t p3 = (byte >> 3) & 1;
    uint8_t d1 = (byte >> 2) & 1;
    uint8_t d2 = (byte >> 1) & 1;
    uint8_t d3 = (byte >> 0) & 1;

    uint8_t s0 = p1 ^ d0 ^ d1 ^ d3;
    uint8_t s1 = p2 ^ d0 ^ d2 ^ d3;
    uint8_t s2 = p3 ^ d1 ^ d2 ^ d3;

    uint8_t syndrome = (s2 << 2) | (s1 << 1) | s0;

    if (syndrome != 0) {
        if (syndrome <= 7) {
            byte ^= (1 << (7 - syndrome));
        }
        // re-extract after correction
        p1 = (byte >> 6) & 1;
        p2 = (byte >> 5) & 1;
        d0 = (byte >> 4) & 1;
        p3 = (byte >> 3) & 1;
        d1 = (byte >> 2) & 1;
        d2 = (byte >> 1) & 1;
        d3 = (byte >> 0) & 1;
    }

    // WARNING: d0 is most significant bit
    return (d0 << 3) | (d1 << 2) | (d2 << 1) | d3;
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
