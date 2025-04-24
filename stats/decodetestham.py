#!/usr/bin/env python3
import sys
import re

def hamming_decode_nibble(code):
    """
    Decodes a single 7-bit Hamming(7,4) code word (stored in an 8-bit value)
    using the bit mapping (bit positions 6 down to 0):
      bit6: p1, bit5: p2, bit4: d1, bit3: p3, bit2: d2, bit1: d3, bit0: d4.
    It computes the syndrome, corrects any single-bit error, then extracts the 4 data bits.
    """
    # Extract individual bits
    b6 = (code >> 6) & 1  # p1
    b5 = (code >> 5) & 1  # p2
    b4 = (code >> 4) & 1  # d1
    b3 = (code >> 3) & 1  # p3
    b2 = (code >> 2) & 1  # d2
    b1 = (code >> 1) & 1  # d3
    b0 = code & 1         # d4

    # Compute syndrome bits
    s1 = b6 ^ b4 ^ b2 ^ b0  # parity for positions 1,3,5,7
    s2 = b5 ^ b4 ^ b1 ^ b0  # parity for positions 2,3,6,7
    s3 = b3 ^ b2 ^ b1 ^ b0  # parity for positions 4,5,6,7

    syndrome = s1 + (s2 << 1) + (s3 << 2)

    # If syndrome is non-zero, correct the error:
    if syndrome != 0:
        # Map syndrome (1-7) to bit index (6 down to 0)
        error_index = 7 - syndrome
        code ^= (1 << error_index)

    # Now extract the data bits (d1 at bit4, d2 at bit2, d3 at bit1, d4 at bit0)
    nibble = (((code >> 4) & 1) << 3) | (((code >> 2) & 1) << 2) | (((code >> 1) & 1) << 1) | (code & 1)
    return nibble

def decode_hamming_data(encoded):
    """
    Given a list of encoded bytes (each is a 7-bit Hamming code word in an 8-bit container),
    decode them in pairs (first codeword gives high nibble, second gives low nibble) to recover
    the original bytes.
    """
    decoded = []
    if len(encoded) % 2 != 0:
        print("Warning: Encoded data length is not even. Some data may be incomplete.")
    for i in range(0, len(encoded) - 1, 2):
        high_nibble = hamming_decode_nibble(encoded[i])
        low_nibble  = hamming_decode_nibble(encoded[i+1])
        decoded_byte = (high_nibble << 4) | low_nibble
        decoded.append(decoded_byte)
    return decoded

def process_line(line):
    """
    Processes one log line in the format:
      timestamp | hex bytes | error message
    It extracts the timestamp and error message unchanged, decodes the hex byte list (assumed to be the
    Hamming-encoded payload), and returns a new line in the same format but with the decoded payload.
    """
    parts = line.split("|")
    if len(parts) < 3:
        return None  # Line does not follow the expected format.
    timestamp = parts[0].strip()
    hex_payload = parts[1].strip()  # This is the Hamming-encoded payload.
    error_message = parts[2].strip()
    # Split the hex_payload by spaces and convert each token to an integer.
    hex_tokens = hex_payload.split()
    try:
        encoded_bytes = [int(token, 16) for token in hex_tokens]
    except ValueError:
        print(f"Warning: Could not parse hex values in line: {line}")
        return None

    decoded_bytes = decode_hamming_data(encoded_bytes)
    # Format the decoded bytes as space-separated two-digit hex values.
    decoded_hex = " ".join(f"{byte:02X}" for byte in decoded_bytes)
    # Return the re-formatted log line.
    return f"{timestamp} | {decoded_hex} | {error_message}"

def main(filename):
    try:
        with open(filename, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                new_line = process_line(line)
                if new_line:
                    print(new_line)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python decode_log_format.py <filename>")
        sys.exit(1)
    main(sys.argv[1])
