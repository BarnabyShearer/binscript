#!/usr/bin/env python3
import sys
import os
from elf import elf


def int64(i):
    return int(i).to_bytes(8, byteorder="little")


MOV_REG = [
    b"\x48\xb8",  # mov rax
    b"\x48\xbf",  # mov rdi
    b"\x48\xbe",  # mov rsi
    b"\x48\xba",  # mov rdx
    b"\x49\xba",  # mov r10
    b"\x49\xb8",  # mov r8
    b"\x49\xb9",  # mov r9
]
DEREF = [
    b"\x48\x8b\x00",  # mov rax,[rax]
    b"\x48\x8b\x3f",  # mov rdi,[rdi]
    b"\x48\x8b\x36",  # mov rsi,[rsi]
    b"\x48\x8b\x12",  # mov rdx,[rdx]
    b"\x4d\x8b\x12",  # mov r10,[r10]
    b"\x4d\x8b\x00",  # mov r8,[r8]
    b"\x4d\x8b\x09",  # mov r9,[r9]
]


def main(src_name: str, dest_name: str) -> None:
    refs = {
        # constants
        b"NULL": int64(0),
        b"OK": int64(0),
        b"STDIN": int64(0),
        b"TRUE": int64(1),
        b"STDOUT": int64(1),
        b"INET": int64(2),
        b"END": int64(2),
        b"STREAM": int64(1),
        b"CREAT": int64(0o1000 + 0o100 + 0o2), # O_TRUNC |O_CREAT | O_RDWR
        # syscalls
        b"read": int64(0),
        b"write": int64(1),
        b"open": int64(2),
        b"lseek": int64(8),
        b"socket": int64(41),
        b"connect": int64(42),
        b"accept": int64(43),
        b"sendto": int64(44),
        b"recvfrom": int64(45),
        b"bind": int64(49),
        b"listen": int64(50),
        b"exit": int64(60),
    }
    lens = {}
    token = b""
    i = 0
    with open(src_name, "rb") as src, open(dest_name, "wb") as dest:
        dest.write(elf(0))
        dest.write(b"\x48\xb8")
        dest.write(int64(0))
        dest.write(b"\xff\xd0")
        while True:
            c = src.read(1)
            #print(c.decode(), end="")
            if not c:
                break
            if c == b"\n":
                pass
            elif c == b" ":
                if token != b"":
                    dest.write(MOV_REG[i])
                    dest.write(refs[token])
                    i += 1
                    token = b""
            elif c == b"*":
                dest.write(MOV_REG[i])
                dest.write(lens[token])
                i += 1
                token = b""
            elif c == b">":
                dest.write(DEREF[i - 1])
            elif c == b"+":
                dest.write(b"\x48\x01\xf8")  # add rax, rdi
                i = 1
            elif c == b"-":
                dest.write(b"\x48\x29\xf8")  # sub rax, rdi
                i = 1
            elif c == b"<":
                dest.write(b"\x48\xA3")  # mov [qword ], rax
                dest.write(refs[token])
                token = b""
                i = 0
            elif c == b"[":
                dest.write(MOV_REG[6])  # mov r9
                dest.write(refs[token])
                dest.write(DEREF[6])  # mov r9,[r9]
                dest.write(b"\x49\x89\x01")  # mov [r9], rax
                token = b""
                i = 0
            elif c == b"|":
                dest.write(b"\x58")  # pop rax
            elif c == b"!":
                dest.write(b"\xff\xd0")  # call
                i = 0
            elif c == b"$":
                dest.write(b"\x0f\x05")  # syscall
                i = 0
            elif c == b"=":
                dest.write(b"\x48\x39\xf8")  # cmp rax, rdi
                dest.write(b"\x75\x02")  # jne 2
                dest.write(b"\xff\xd6")  # call rsi
                i = 0
            elif c == b"~":
                dest.write(b"\x48\x39\xf8")  # cmp rax, rdi
                dest.write(b"\x74\x02")  # je 2
                dest.write(b"\xff\xd6")  # call rsi
                i = 0
            elif c == b":":
                dest.write(b"\xc3")  # ret
                print(token.decode(), "offset", dest.tell())
                refs[token] = int64(0x08048000 + dest.tell())
                lens[token] = 0
                c = src.read(1)
                in_str = False
                in_byte = False
                tmp = 0
                while c != b"\n":
                    if in_str:
                        if c == b'"':
                            in_str = False
                        else:
                            dest.write(c)
                            lens[token] += 1
                    else:
                        if c == b'"':
                            in_str = True
                        elif c == b" ":
                            if in_byte:
                                dest.write(int(tmp).to_bytes(1, byteorder="little"))
                                lens[token] += 1
                                tmp = 0
                                in_byte = False
                        elif c == b"*":
                            mul = b""
                            c = src.read(1)
                            while c not in b" \n":
                                mul += c
                                c = src.read(1)
                            for _ in range(int(mul) - 1):
                                dest.write(int(tmp).to_bytes(1, byteorder="little"))
                                lens[token] += 1
                            tmp = 0
                            continue
                        else:
                            tmp <<= 4
                            tmp += int(c, 16)
                            in_byte = True
                    c = src.read(1)
                if in_byte:
                    dest.write(int(tmp).to_bytes(1, byteorder="little"))
                    lens[token] += 1
                lens[token] = int64(lens[token])
                token = b""
            else:
                token += c
        size = dest.tell()
        dest.seek(0x60)
        dest.write(int64(size))  # p_filesz
        dest.write(int64(size))  # p_memsz
        dest.seek(0x7A)
        dest.write(refs[b"main"])  # call main
    os.chmod(dest_name, 0o777)

if __name__ == "__main__":
    main(*sys.argv[1:])
