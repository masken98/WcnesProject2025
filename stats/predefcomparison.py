#!/usr/bin/env python3
import re
import sys
from functions import *
import matplotlib.pyplot as plt


def flip_counter(expected: list[int], received: list[int]) -> tuple[int, int]:
    """
    Compare two lists of integers (e.g. bytes).  
    Returns a tuple (flips_to_one, flips_to_zero), where:
      - flips_to_one is the total count of bits that went from 0→1
      - flips_to_zero is the total count of bits that went from 1→0
    """
    if len(expected) != len(received):
        raise ValueError(f"List lengths differ: {len(expected)} vs {len(received)}")
    flips_to_one = 0
    flips_to_zero = 0

    for e, r in zip(expected, received):
        diff = e ^ r
        # bits that flipped to 1 are those that differ AND are 1 in r
        flips_to_one  += hamming_weight(diff & r)
        # bits that flipped to 0 are those that differ AND are 1 in e
        flips_to_zero += hamming_weight(diff & e)

    return flips_to_one, flips_to_zero

def hamming_weight(x: int) -> int:
    """Count number of set bits in x."""
    return bin(x).count('1')

def main():
    logfile = './ecc130.txt'  # file in the same directory

    # --- define your expected packet here ---
    # Byte sequence: 0f 00 10 20 30 40 50 60 70 80 90 a0 b0 c0 d0 e0
    expected_hex = "0f 17 1b 1d 1e 27"
    expected = [int(b, 16) for b in expected_hex.split()]
    packet_len = len(expected)

    bit_errors_per_packet = []

    total_bits = 0
    total_bit_errors = 0
    packets_seen = 0
    skipped = 0
    flipped_to_one = 0
    flipped_to_zero = 0

    # Regex to capture a run of hex-bytes between pipes
    line_re = re.compile(r"\|\s*([0-9A-Fa-f]{2}(?:\s+[0-9A-Fa-f]{2})+)\s*\|")

    try:
        with open(logfile, 'r') as f:
            for lineno, line in enumerate(f, start=1):
                m = line_re.search(line)
                if not m:
                    # No hex data found (e.g. overflow line)
                    skipped += 1
                    continue

                rec_bytes = [int(b,16) for b in m.group(1).split()]
                if len(rec_bytes) != packet_len:
                    # Wrong byte count—probably corrupted line
                    print(f"Line {lineno}: expected {packet_len} bytes but got {len(rec_bytes)}; skipping",
                          file=sys.stderr)
                    skipped += 1
                    continue

                # Count bit-errors
                bit_errors = sum(
                    hamming_weight(e ^ r) for e, r in zip(expected, rec_bytes)
                )

                bit_errors_per_packet.append(bit_errors)

                one, zero = flip_counter(expected, rec_bytes)
                flipped_to_one  += one
                flipped_to_zero += zero

                total_bit_errors += bit_errors
                total_bits += packet_len * 8
                packets_seen += 1

                # Count flips

    except FileNotFoundError:
        print(f"Error: cannot open '{logfile}'", file=sys.stderr)
        sys.exit(1)

    if packets_seen == 0:
        print("No valid packets found; nothing to compute.", file=sys.stderr)
        sys.exit(1)

    ber = total_bit_errors / total_bits
    print(f"Packets analyzed    : {packets_seen}")
    print(f"Lines skipped       : {skipped}")
    print(f"Total bits checked  : {total_bits}")
    print(f"Total bit errors    : {total_bit_errors}")
    print(f"Bit-Error Rate (BER): {ber:.6e}")
    print(f"Flips from 0 to 1   : {flipped_to_one}")
    print(f"Flips from 1 to 0   : {flipped_to_zero}")

    # plot results
    plt.scatter(range(len(bit_errors_per_packet)), bit_errors_per_packet, color='black', alpha=0.7, marker='o', s=6)
    plt.title("Bit Errors per Packet")
    plt.xlabel("Packet Index")
    plt.ylabel("Number of Bit Errors")
    plt.grid(True)
    plt.xlim(-0.5, len(bit_errors_per_packet) - 0.5)
    plt.ylim(-0.5, max(bit_errors_per_packet) + 1)
    plt.savefig("ecc130.png", dpi=300, bbox_inches='tight') 
    plt.show()

if __name__ == "__main__":
    main()
