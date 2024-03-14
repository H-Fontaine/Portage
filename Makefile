INCSDIR =build/include build/library
LIBSDIR =build/library
LDLIBS =-lmbedcrypto -nostdlib

PREFIX =arm-none-eabi-
GDB =$(PREFIX)gdb
CC =$(PREFIX)gcc
AS =$(PREFIX)as
OBJDUMP =$(PREFIX)objdump

TARGET_ARM =-mcpu=cortex-m4 -mthumb
TARGET_ARCH =$(TARGET_ARM) -ffreestanding -mfpu=fpv4-sp-d16 -mfloat-abi=softfp

CFLAGS =-g -O1 -Wall -Werror -Wextra -Wno-unused-parameter $(foreach d, $(INCSDIR), -I$d) -MD -MP $(TARGET_ARCH)
LDFLAGS =$(foreach d, $(LIBSDIR), -L$d) $(LDLIBS) -T linker_script.lds

EXE =exec
SOURCES =main.c init.c mbedtls_dependencies.c
OBJS =$(SOURCES:.c=.o) crt0.o
OBJS_TO_CLEAN =$(OBJS) $(OBJS:.o=.d) $(EXE)

BUILD_DIR =build
BUILD_TYPE =Debug
TOOLCHAIN =toolchain.cmake

all: $(EXE)

%.o : %.asm
	$(AS) $(TARGET_ARM) -o $@ $<

$(EXE) : LIB $(OBJS)
	$(CC) $(OBJS) $(LDFLAGS) -o $@

LIB : $(TOOLCHAIN) | $(BUILD_DIR)

$(TOOLCHAIN) :
	@echo "\
set(CMAKE_SYSTEM_PROCESSOR armv7-m)\n\
set(CMAKE_C_COMPILER $(CC))\n\
set(CMAKE_MAKE_PROGRAM=make)\n\
set(CMAKE_C_FLAGS \"\$${CMAKE_C_FLAGS} $(TARGET_ARCH)\")\n\
set(CMAKE_EXE_LINKER_FLAGS \" --specs=nosys.specs\")" > $(TOOLCHAIN)

$(BUILD_DIR):
	rm -r -f $(BUILD_DIR); \
	mkdir $(BUILD_DIR); \
	cd $(BUILD_DIR); \
	cmake -DCMAKE_BUILD_TYPE=$(BUILD_TYPE) -DUSE_SHARED_MBEDTLS_LIBRARY=OFF -DUSE_STATIC_MBEDTLS_LIBRARY=ON -DENABLE_PROGRAMS=OFF -DENABLE_TESTING=OFF -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_TOOLCHAIN_FILE=../$(TOOLCHAIN) ../mbedtls-3.5.2; \
	cmake --build .; \
	cd include; \
	ln -s ../../mbedtls-3.5.2/include/mbedtls/; \
	cd ../..;

connect::
	stlink-gdbserver

debug: $(EXE)
	$(GDB) -x config.gdb $^

dump: $(EXE)
	$(OBJDUMP) -D $^ > dump.txt


clean::
	rm -f $(OBJS_TO_CLEAN) $(TOOLCHAIN)

fclean: clean
	rm -r -f $(BUILD_DIR)

-include $(SOURCES:.c=.d)