#!/usr/bin/env python3
import re
import sys

def hamming_weight(x: int) -> int:
    """Count number of set bits in x."""
    return bin(x).count('1')

def main():
    logfile = 'nytt_test.txt'  # file in the same directory

    # --- define your expected packet here ---
    # Byte sequence: 0f 00 10 20 30 40 50 60 70 80 90 a0 b0 c0 d0 e0
    expected_hex = "0f 00 10 20 30 40 50 60 70 80 90 a0 b0 c0 d0 e0"
    expected = [int(b, 16) for b in expected_hex.split()]
    packet_len = len(expected)

    total_bits = 0
    total_bit_errors = 0
    packets_seen = 0
    skipped = 0

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

                total_bit_errors += bit_errors
                total_bits += packet_len * 8
                packets_seen += 1

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

if __name__ == "__main__":
    main()
