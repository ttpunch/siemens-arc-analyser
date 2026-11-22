/* mc7dis — sequential MC7 disassembler CLI built on rizinorg/rz-libmc7.
 *
 * Usage: mc7dis <file.mc5> [start_offset] [max_instructions]
 *
 * Prints one AWL/STL statement per line as "<offset>: <mnemonic>".
 * Intended for read-only inspection of STEP 7 block code payloads that were
 * extracted from a project (see s7_project.py --blobs).
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "simatic.h"

int main(int argc, char **argv)
{
	if (argc < 2) {
		fprintf(stderr, "usage: %s <file> [start] [max]\n", argv[0]);
		return 2;
	}
	ut64_t start = (argc > 2) ? strtoull(argv[2], NULL, 0) : 0;
	ut64_t max = (argc > 3) ? strtoull(argv[3], NULL, 0) : 0;

	FILE *f = fopen(argv[1], "rb");
	if (!f) {
		perror("open");
		return 1;
	}
	fseek(f, 0, SEEK_END);
	long len = ftell(f);
	fseek(f, 0, SEEK_SET);
	ut8_t *buf = malloc(len > 0 ? (size_t)len : 1);
	if (!buf || fread(buf, 1, (size_t)len, f) != (size_t)len) {
		fprintf(stderr, "read error\n");
		fclose(f);
		return 1;
	}
	fclose(f);

	ut64_t off = start, count = 0;
	while (off < (ut64_t)len) {
		S7Instr instr;
		memset(&instr, 0, sizeof(instr));
		int read = simatic_s7_decode_instruction(buf + off, (ut64_t)len - off, off, &instr);
		if (read <= 0) {
			printf("%04llx: .byte 0x%02x\n", (unsigned long long)off, buf[off]);
			off += 1;
		} else {
			printf("%04llx: %s\n", (unsigned long long)off, instr.assembly);
			off += (ut64_t)read;
		}
		if (max && ++count >= max) {
			break;
		}
	}
	free(buf);
	return 0;
}
