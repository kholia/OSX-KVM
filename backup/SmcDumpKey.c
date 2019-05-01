/*
 * prints out 4-character name of the SMC key at given index position;
 *
 * by Gabriel L. Somlo <somlo@cmu.edu>, Summer 2014
 *
 * Compile with: gcc -O2 -o SmcDumpKey SmcDumpKey.c -Wall
 *
 * You probably want to "modprobe -r applesmc" before running this...
 *
 * Code bits and pieces shamelessly ripped from the linux kernel driver
 * (drivers/hwmon/applesmc.c by N. Boichat and H. Rydberg)
 *
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License v2 as published by the
 * Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 *
 * You should have received a copy of the GNU General Public License along with
 * this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA
 *
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <limits.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <sys/io.h>
#include <linux/byteorder/little_endian.h>


#define APPLESMC_START 0x300
#define APPLESMC_RANGE 0x20

#define APPLESMC_DATA_PORT	(APPLESMC_START + 0x00)
#define APPLESMC_CMD_PORT	(APPLESMC_START + 0x04)

#define APPLESMC_READ_CMD		0x10
#define APPLESMC_GET_KEY_BY_INDEX_CMD	0x12
#define APPLESMC_GET_KEY_TYPE_CMD	0x13


/* wait up to 128 ms for a status change. */
#define APPLESMC_MIN_WAIT	0x0010
#define APPLESMC_RETRY_WAIT	0x0100
#define APPLESMC_MAX_WAIT	0x20000


#define APPLESMC_KEY_NAME_LEN	4
#define APPLESMC_KEY_TYPE_LEN	4

typedef struct key_type {
  uint8_t data_len;
  uint8_t data_type[APPLESMC_KEY_TYPE_LEN];
  uint8_t flags;
} __attribute__((packed)) key_type;


/* wait_read - Wait for a byte to appear on SMC port. */
static int
wait_read(void)
{
  uint8_t status;
  int us;

  for (us = APPLESMC_MIN_WAIT; us < APPLESMC_MAX_WAIT; us <<= 1) {
    usleep(us);
    status = inb(APPLESMC_CMD_PORT);
    /* read: wait for smc to settle */
    if (status & 0x01)
      return 0;
  }

  fprintf(stderr, "wait_read() fail: 0x%02x\n", status);
  return -1;
}

/*send_byte - Write to SMC port, retrying when necessary. */
static int
send_byte(uint8_t cmd, unsigned short port)
{
  uint8_t status;
  int us;

  outb(cmd, port);
  for (us = APPLESMC_MIN_WAIT; us < APPLESMC_MAX_WAIT; us <<= 1) {
    usleep(us);
    status = inb(APPLESMC_CMD_PORT);
    /* write: wait for smc to settle */
    if (status & 0x02)
      continue;
    /* ready: cmd accepted, return */
    if (status & 0x04)
      return 0;
    /* timeout: give up */
    if (us << 1 == APPLESMC_MAX_WAIT)
      break;
    /* busy: long wait and resend */
    usleep(APPLESMC_RETRY_WAIT);
    outb(cmd, port);
  }

  fprintf(stderr,
          "send_byte(0x%02x, 0x%04x) fail: 0x%02x\n", cmd, port, status);
  return -1;
}

static int
send_argument(const uint8_t *key)
{
  int i;

  for (i = 0; i < APPLESMC_KEY_NAME_LEN; i++)
    if (send_byte(key[i], APPLESMC_DATA_PORT))
      return -1;
  return 0;
}

static int
read_smc(uint8_t cmd, const uint8_t *key, uint8_t *buf, uint8_t len)
{
  int i;

  if (send_byte(cmd, APPLESMC_CMD_PORT) || send_argument(key)) {
    fprintf(stderr, "%.4s: read arg fail\n", key);
    return -1;
  }

  if (send_byte(len, APPLESMC_DATA_PORT)) {
    fprintf(stderr, "%.4s: read len fail\n", key);
    return -1;
  }

  for (i = 0; i < len; i++) {
    if (wait_read()) {
      fprintf(stderr, "%.4s: read data[%d] fail\n", key, i);
      return -1;
    }
    buf[i] = inb(APPLESMC_DATA_PORT);
  }

  return 0;
}


int
main(int argc, char **argv)
{
  key_type kt;
  uint8_t data_buf[UCHAR_MAX];
  uint8_t i;

  if (argc != 2 || strlen(argv[1]) != APPLESMC_KEY_NAME_LEN) {
    fprintf(stderr, "\nUsage: %s <4-char-key-name>\n\n", argv[0]);
    return -1;
  }

  if (ioperm(APPLESMC_START, APPLESMC_RANGE, 1) != 0) {
    perror("ioperm failed");
    return -2;
  }

  if (read_smc(APPLESMC_GET_KEY_TYPE_CMD,
               (uint8_t *)argv[1], (uint8_t *)&kt, sizeof(kt)) != 0) {
    fprintf(stderr, "\nread_smc get_key_type error\n\n");
    return -3;
  }
  printf("  type=\"");
  for (i = 0; i < APPLESMC_KEY_TYPE_LEN; i++)
    printf(isprint(kt.data_type[i]) ? "%c" : "\\x%02x",
           (uint8_t)kt.data_type[i]);
  printf("\" length=%d flags=%x\n", kt.data_len, kt.flags);

  if (read_smc(APPLESMC_READ_CMD,
               (uint8_t *)argv[1], data_buf, kt.data_len) != 0) {
    fprintf(stderr, "\nread_smc get_key_data error\n\n");
    return -4;
  }
  printf("  data=\"");
  for (i = 0; i < kt.data_len; i++)
    printf(isprint(data_buf[i]) ? "%c" : "\\x%02x",
           (uint8_t)data_buf[i]);
  printf("\"\n");

  return 0;
}
