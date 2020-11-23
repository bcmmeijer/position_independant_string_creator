from argparse import ArgumentParser
from binascii import hexlify
import struct

def main():
    parser = ArgumentParser()
    parser.add_argument("-s", "--string", required=True, help="input string")
    parser.add_argument("-a", "--arch", required=False, default="x86", help="Architecture (x86, x64). will be used to choose chunksize")
    parser.add_argument("-f", "--format", required=False, default="function", help="Output type. (function, asm)")
    args = parser.parse_args()

    chunksize = 4 if args.arch == "x86" else 8

    data = bytearray(args.string.encode('utf-8'))
    res = chunksize - (len(data) % chunksize)
    for _ in range(res):
        data.append(0x00)

    chunks = [hexlify(data[i:i+chunksize]) for i in range(0, len(data), chunksize)]

    formatted_chunks = []

    for chunk in chunks:
        number = [int(i, 16) for i in chunk.split()][0]
        packed = struct.pack('<I' if chunksize == 4 else '<Q', number).hex()

        if args.format == "function":
            formatted_chunks.append(f"0x{packed}")
        elif args.format == "asm" or args.format == "raw":
            formatted_chunks.append(f"0x{packed}")

    if args.format == "function":

        func = """

void get_string(char* buffer) {
\ttypedef unsigned long """

        func += "u32;\n" if chunksize == 4 else "long u64;\n"
        i = 0

        for fmt in formatted_chunks:
            beg = "u32" if chunksize == 4 else "u64"
            func += f"\t*({beg}*)&buffer[{i}] = {fmt};\n"
            i += chunksize
            
        func += "}\n"
        print(func)
    
    elif args.format == "asm":
        func = "\n"
        inst = "DWORD PTR" if chunksize == 4 else "QWORD PTR"
        ax = "eax" if chunksize == 4 else "rax"
        cx = "ecx" if chunksize == 4 else "rcx"
        i = 0

        for fmt in formatted_chunks:
            func += f"mov {ax}, {fmt}\n"
            func += f"mov {inst} [{cx} + {i}], {ax}\n"
            i += chunksize
        
        func += "ret\n"
        print(func)

if __name__ == "__main__":
    main()