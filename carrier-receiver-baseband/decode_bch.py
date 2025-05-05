import bchlib
import sys

# BCH parameters (MUST MATCH what you used in your encoder!)
BCH_POLYNOMIAL = 137
BCH_BITS = 5

bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 decode_bch.py <comma-separated-hex-bytes>")
        sys.exit(1)

    hex_input = sys.argv[1]
    hex_bytes = bytes(int(x, 16) for x in hex_input.split(','))

    # Separate data and ECC
    data_length = len(hex_bytes) - bch.ecc_bytes
    data = hex_bytes[:data_length]
    ecc = hex_bytes[data_length:]

    # Decode
    corrected_data = bytearray(data)
    errors = bch.decode_inplace(corrected_data, ecc)

    if errors >= 0:
        print(f"Successfully decoded with {errors} errors corrected.")
        print("Decoded payload:")
        print(' '.join(f'{byte:02X}' for byte in corrected_data))
    else:
        print("Failed to decode. Too many errors.")

if __name__ == "__main__":
    main()
