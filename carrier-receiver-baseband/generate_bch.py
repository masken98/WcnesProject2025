# generate_bch.py
# python3 generate_bch.py


import bchlib
import struct

# BCH Parameters
BCH_POLYNOMIAL = 137  # Primitive polynomial
BCH_BITS = 5          # Correct up to t errors (example: t=5)

# Create BCH instance
bch = bchlib.BCH(BCH_POLYNOMIAL, BCH_BITS)

# Original payload
PAYLOAD = [
    0x10, 0x20, 0x30, 0x40,
    0x50, 0x60, 0x70, 0x80,
    0x90, 0xA0, 0xB0, 0xC0,
    0xD0, 0xE0
]
HEADER = [
    0xAA, 0xAA, 0xAA, 0xAA,
    0xD3, 0x91, 0xD3, 0x91
]
SEQUENCE = 0x00

def apply_bch_ecc(data):
    data_bytes = bytes(data)
    ecc = bch.encode(data_bytes)
    protected = list(data_bytes + ecc)
    return protected

def main():
    payload_with_ecc = apply_bch_ecc(PAYLOAD)
    length_byte = len(payload_with_ecc) + 1

    packet = HEADER + [length_byte, SEQUENCE] + payload_with_ecc

    with open("predefined_packet.h", "w") as f:
        f.write("#ifndef PREDEFINED_PACKET_H\n")
        f.write("#define PREDEFINED_PACKET_H\n\n")
        f.write(f"#define PREDEF_PAYLOAD_LEN {len(payload_with_ecc)}\n")
        f.write(f"#define PREDEF_PACKET_LEN {len(packet)}\n\n")
        f.write("static const uint8_t predefined_packet[PREDEF_PACKET_LEN] = {\n    ")

        for idx, byte in enumerate(packet):
            f.write(f"0x{byte:02x}")
            if idx != len(packet) - 1:
                f.write(", ")
            if (idx + 1) % 8 == 0:
                f.write("\n    ")

        f.write("\n};\n\n#endif // PREDEFINED_PACKET_H\n")
    print("Generated predefined_packet.h successfully (BCH ECC).")

if __name__ == "__main__":
    main()
