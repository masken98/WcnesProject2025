/**
 * Tobias Mages & Wenqing Yan
 * Modified for convolutional coding.
 */

 #include <stdio.h>
 #include <string.h>
 #include <math.h>
 #include "pico/stdlib.h"
 #include "packet_generation.h"
 
 #define DEFAULT_SEED 0xABCD
 uint32_t seed = DEFAULT_SEED;
 
 uint8_t packet_hdr_2500[HEADER_LEN] = {0xaa, 0xaa, 0xaa, 0xaa, 0xd3, 0x91, 0xd3, 0x91, 0x00, 0x00};
 uint8_t packet_hdr_1352[HEADER_LEN] = {0xaa, 0xaa, 0xaa, 0xaa, 0x93, 0x0b, 0x51, 0xde, 0x00, 0x00};
 
 /*
  * obtain the packet header template for the corresponding radio
  */
 uint8_t *packet_hdr_template(uint16_t receiver){
     if(receiver == 2500){
         return packet_hdr_2500;
     } else{
         return packet_hdr_1352;
     }
 }
 
 /* 
  * generate a uniform random number.
  */
 uint32_t rnd() {
     const uint32_t A1 = 1664525;
     const uint32_t C1 = 1013904223;
     const uint32_t RAND_MAX1 = 0xFFFFFFFF;
     seed = ((seed * A1 + C1) & RAND_MAX1);
     return seed;
 }
 
 /* 
  * generate a compressible payload sample.
  */
 uint16_t file_position = 0;
 uint16_t generate_sample(){
     if (file_position == 0) {
         seed = DEFAULT_SEED; /* reset seed when beginning a new sequence */
     }
     file_position = file_position + 2;
     double two_pi = 2.0 * M_PI;
     double u1, u2;
     u1 = ((double) rnd())/ ((double) 0xFFFFFFFF);
     u2 = ((double) rnd())/((double) 0xFFFFFFFF);
     double tmp = ((double) 0x7FF) * sqrt(-2.0 * log(u1));
     return max(0.0, min(((double) 0x3FFFFF), tmp * cos(two_pi * u2) + ((double) 0x1FFF)));
 }
 
 /*
  * Fill the buffer with payload data.
  * Now, instead of triple repetition, we generate a single instance per sample.
  * If include_index is true, the first two bytes are the file index.
  */
 void generate_data(uint8_t *buffer, uint8_t length, bool include_index) {
     if(length % 2 != 0){
         printf("WARNING: generate_data has been used with an odd length.\n");
     }
     
     uint8_t data_start = 0;
     if(include_index){
         buffer[0] = (uint8_t) (file_position >> 8);
         buffer[1] = (uint8_t) (file_position & 0x00FF);
         data_start = 2;
     }
     // Fill remaining bytes with 2 bytes per sample.
     for (uint8_t i = data_start; i < length; i = i + 2) {
         uint16_t sample = generate_sample();
         buffer[i]   = (uint8_t) (sample >> 8);
         buffer[i+1] = (uint8_t) (sample & 0x00FF);
     }
 }
 
 /*
  * Add header to the packet:
  * Copies the first 8 bytes from header_template.
  * The 9th byte is the payload length, and the 10th is the sequence number.
  */
 void add_header(uint8_t *packet, uint8_t seq, uint8_t *header_template, uint8_t payload_len) {
     for(int loop = 0; loop < HEADER_LEN - 2; loop++) {
         packet[loop] = header_template[loop];
     }
     packet[HEADER_LEN - 2] = payload_len;  // set payload length (post-encoding)
     packet[HEADER_LEN - 1] = seq;
 }
 
 /*
  * Helper function: compute parity (XOR of all bits in a byte).
  */
 static int parity(uint8_t x) {
     int p = 0;
     while(x) {
         p ^= (x & 1);
         x >>= 1;
     }
     return p;
 }
 
 /*
  * Helper function: set the bit (0 or 1) at bit position 'bit_index' in array 'arr'.
  */
 static void set_bit_in_array(uint8_t *arr, int bit_index, int value) {
     int byte_index = bit_index / 8;
     int bit_pos = 7 - (bit_index % 8); // store most-significant bit first
     if(value)
         arr[byte_index] |= (1 << bit_pos);
     else
         arr[byte_index] &= ~(1 << bit_pos);
 }
 
 /*
  * Convolutional encoder (rate 1/2, constraint length 3, generator polynomials G1=0x7 (111) and G2=0x5 (101)).
  * It processes the input bitstream (MSB first) and produces two output bits per input bit,
  * with an additional 2*(K-1) bits as tail bits to flush the encoder.
  */
 void conv_encode(uint8_t *input, int input_len, uint8_t *output, int *output_len) {
     int K = 3; // constraint length
     uint8_t G1 = 0x7; // 111 in binary
     uint8_t G2 = 0x5; // 101 in binary
 
     int total_input_bits = input_len * 8;
     // Each input bit produces 2 output bits, plus tail bits for (K-1) zeros.
     int total_encoded_bits = 2 * (total_input_bits + (K - 1));
     // Clear the output buffer.
     memset(output, 0, (total_encoded_bits + 7) / 8);
     
     int out_bit_index = 0;
     int shift_reg = 0; // shift register initial state
     
     // Process each input bit.
     for (int i = 0; i < total_input_bits; i++) {
         int byte_index = i / 8;
         int bit_index = 7 - (i % 8);
         int bit = (input[byte_index] >> bit_index) & 1;
         // Shift in the new bit.
         shift_reg = ((shift_reg << 1) | bit) & 0x7;  // keep 3 bits
         // Compute the two output bits (using modulo-2 addition, i.e. XOR).
         int p1 = parity(shift_reg & G1);
         int p2 = parity(shift_reg & G2);
         set_bit_in_array(output, out_bit_index, p1);
         set_bit_in_array(output, out_bit_index + 1, p2);
         out_bit_index += 2;
     }
     // Flush the encoder: process K-1 zeros.
     for (int i = 0; i < (K - 1); i++) {
         shift_reg = (shift_reg << 1) & 0x7;  // shift in a zero
         int p1 = parity(shift_reg & G1);
         int p2 = parity(shift_reg & G2);
         set_bit_in_array(output, out_bit_index, p1);
         set_bit_in_array(output, out_bit_index + 1, p2);
         out_bit_index += 2;
     }
     *output_len = (out_bit_index + 7) / 8;
 }
 

