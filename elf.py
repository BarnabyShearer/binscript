import ctypes


class Elf(ctypes.Structure):
    _fields_ = [
        ("e_ident_magic", ctypes.c_int32),
        ("e_ident_class", ctypes.c_byte),
        ("e_ident_data", ctypes.c_byte),
        ("e_ident_version", ctypes.c_byte),
        ("e_ident_osabi", ctypes.c_byte),
        ("e_ident_abiversion", ctypes.c_int64),
        ("e_type", ctypes.c_int16),
        ("e_machine", ctypes.c_int16),
        ("e_version", ctypes.c_int32),
        ("e_entry", ctypes.c_int64),
        ("e_phoff", ctypes.c_int64),
        ("e_shoff", ctypes.c_int64),
        ("e_flags", ctypes.c_int32),
        ("e_ehsize", ctypes.c_int16),
        ("e_phentsize", ctypes.c_int16),
        ("e_phnum", ctypes.c_int16),
        ("e_shentsize", ctypes.c_int16),
        ("e_shnum", ctypes.c_int16),
        ("e_shstrndx", ctypes.c_int16),
    ]


class Program(ctypes.Structure):
    _fields_ = [
        ("p_type", ctypes.c_int32),
        ("p_flags", ctypes.c_int32),
        ("p_offset", ctypes.c_int64),
        ("p_vaddr", ctypes.c_int64),
        ("p_paddr", ctypes.c_int64),
        ("p_filesz", ctypes.c_int64),
        ("p_memsz", ctypes.c_int64),
        ("p_align", ctypes.c_int64),
    ]


def elf(progsize: int = 0) -> bytes:
    return bytes(
        Elf(
            int.from_bytes(b"\x7FELF", byteorder="little"),
            2,  # 64bit Elf
            1,  # little endian
            1,  # v1 Elf
            3,  # Linux
            0,  # v0 ABI + pad
            2,  # ET_EXEC
            0x3E,  # amd64
            1,  # v1 Elf
            0x08048000 + 0x40 + 0x38,  # program start
            0x40,  # program header start
            0,  # section header start
            0,  # flags
            0x40,  # elf header size
            0x38,  # program header size
            1,  # program headers
            0,  # section header size
            0,  # section headers
            0,  # section names index
        )
    ) + bytes(
        Program(
            1,  # PT_LOAD
            7,  # Read-Write-Execute
            0,  # section header start
            0x08048000,  # virtual address
            0x08048000,  # physical address
            progsize + 0x40 + 0x38,  # file size
            progsize + 0x40 + 0x38,  # memory size
            0x1000,  # align
        )
    )
