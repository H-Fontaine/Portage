INCSDIR =build/include build/library
LIBSDIR =build/library
LDLIBS =-lmbedtls -lmbedx509 -lmbedcrypto -nostdlib -lgcc

PREFIX =arm-none-eabi-
GDB =$(PREFIX)gdb
CC =$(PREFIX)gcc
AS =$(PREFIX)as
OBJDUMP =$(PREFIX)objdump

TARGET_ARCH =-mcpu=cortex-m4 -mthumb

CFLAGS =-g -O1 -Wall -Werror -Wextra -Wno-unused-parameter $(foreach d, $(INCSDIR), -I$d) -ffreestanding -MD -MP -mfpu=fpv4-sp-d16 -mfloat-abi=softfp 
LDFLAGS =$(foreach d, $(LIBSDIR), -L$d) $(LDLIBS) -T ld_ram.lds

EXE =exec
SOURCES =main.c init.c memfuncs.c
OBJS =$(SOURCES:.c=.o) crt0.o
TO_CLEAN =$(SOURCES:.c=.o) $(SOURCES:.c=.d) $(EXE)




all: $(EXE)

$(EXE) : $(OBJS)
	$(CC) $^ $(LDFLAGS) -o $@

%.o : %.asm
	$(AS) $(TARGET_ARCH) -o $@ $<

connect::
	stlink-gdbserver

debug: $(EXE)
	$(GDB) -x config.gdb $^

dump: $(EXE)
	$(OBJDUMP) -d $^


BUILD_DIR =build
BUILD_TYPE =Debug
TOOLCHAIN =toolchain.cmake

lib::
	rm -r -f $(BUILD_DIR); \
	mkdir $(BUILD_DIR); \
	cd $(BUILD_DIR); \
	cmake -DCMAKE_BUILD_TYPE=$(BUILD_TYPE) -DUSE_SHARED_MBEDTLS_LIBRARY=OFF -DUSE_STATIC_MBEDTLS_LIBRARY=ON -DENABLE_PROGRAMS=OFF -DENABLE_TESTING=OFF -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -DCMAKE_TOOLCHAIN_FILE=../$(TOOLCHAIN) ../mbedtls-3.5.2; \
	cmake --build .; \
	cd include; \
	ln -s ../../mbedtls-3.5.2/include/mbedtls/; \
	cd ../..;


clean::
	rm -f $(TO_CLEAN)

-include $(SOURCES:.c=.d)