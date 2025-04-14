/**
 * Tobias Mages & Wenqing Yan
 * Modified for convolutional coding (rate 1/2 with K=3)
 */

 #ifndef PACKET_GERNATION_LIB
 #define PACKET_GERNATION_LIB
 
 #include <stdio.h>
 #include <string.h>
 #include <math.h>
 #include "pico/stdlib.h"
 
 // New definitions for the raw and encoded payload sizes.
 // Here we assume a raw payload of 7 samples each 2 bytes plus a 2-byte index.
 #define RAW_PAYLOADSIZE     (14 + 2)    // 2-byte index + 7 samples * 2 bytes = 16 bytes total.
 // For a rate-1/2 encoder, every input bit is doubled in output; plus tail bits (K-1 extra input zeros).
 // For RAW_PAYLOADSIZE of 16 bytes = 128 bits, plus 2 tail bits -> (128+2)*2 = 260 bits, i.e. ceil(260/8)=33 bytes.
 #define MAX_ENC_PAYLOADSIZE 33
 
 #define HEADER_LEN  10 // 8 bytes header + 1 byte payload length + 1 byte sequence number.
 #define buffer_size(x, y) (((x + y) % 4 == 0) ? ((x + y) / 4) : ((x + y) / 4 + 1))
 
 #ifndef MINMAX
 #define MINMAX
 #define max(x, y) (((x) > (y)) ? (x) : (y))
 #define min(x, y) (((x) < (y)) ? (x) : (y))
 #endif
 
 /*
  * obtain the packet header template for the corresponding radio
  */
 uint8_t *packet_hdr_template(uint16_t receiver);
 
 /* 
  * generate a uniform random number.
  */
 uint32_t rnd();
 
 /* 
  * generate a compressible payload sample
  */
 uint16_t generate_sample();
 
 /*
  * Fill the buffer with payload data.
  * include_index: if true, include a 2-byte file index at the start.
  * length: number of bytes to fill in (should match RAW_PAYLOADSIZE).
  */
 void generate_data(uint8_t *buffer, uint8_t length, bool include_index);
 
 /*
  * Add a header to the packet.
  * The header consists of an 8-byte signature, one payload length byte, and one sequence byte.
  * payload_len: the length (in bytes) of the error-corrected payload (after convolutional coding).
  */
 void add_header(uint8_t *packet, uint8_t seq, uint8_t *header_template, uint8_t payload_len);
 
 /*
  * Convolutional encoder (rate 1/2, constraint length 3, generators 7 and 5 (octal)).
  * It takes the raw input (in bytes) and produces an encoded output.
  * output_len: returns the encoded length in bytes.
  */
 void conv_encode(uint8_t *input, int input_len, uint8_t *output, int *output_len);
 
 #endif
 