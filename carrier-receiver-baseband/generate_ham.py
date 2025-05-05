# python3 generate_ham.py

import struct

# Parameters
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

def hamming74_encode(nibble):
    """
    Encode 4 bits into 7 bits using Hamming(7,4).
    Input: nibble (lower 4 bits used)
    Output: 7-bit encoded int (packed in 1 byte)
    """
    d = [(nibble >> i) & 1 for i in range(4)]
    p1 = d[0] ^ d[1] ^ d[3]
    p2 = d[0] ^ d[2] ^ d[3]
    p3 = d[1] ^ d[2] ^ d[3]
    encoded = (p1 << 6) | (p2 << 5) | (d[0] << 4) | (p3 << 3) | (d[1] << 2) | (d[2] << 1) | d[3]
    return encoded

def apply_hamming_ecc(data):
    encoded = []
    for byte in data:
        upper = (byte >> 4) & 0x0F
        lower = byte & 0x0F
        encoded.append(hamming74_encode(upper))
        encoded.append(hamming74_encode(lower))
    return encoded

def main():
    payload_with_ecc = apply_hamming_ecc(PAYLOAD)
    length_byte = len(payload_with_ecc) + 1  # payload + sequence byte

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
    print("Generated predefined_packet.h successfully (Hamming ECC).")


if __name__ == "__main__":
    main()
