#include <stdio.h>
#include <wiringPi.h>
#include <stdint.h>

static const unsigned int CLK = 18;
static const unsigned int DIN = 23;
static const unsigned int DOUT = 24;
static const unsigned int CS = 25;
static const unsigned int LED = 17;


static unsigned int delayMs = 10;
static const unsigned int dust_sensor_delay = 28; // must wait 28 microsec after flash
static const unsigned int dust_charge_delay = 100; // 100millis

void spi_delay() {
	delayMicroseconds(delayMs);
}

/* somewhat from wikipedia */
uint8_t SPI_transfer_byte(int clk, int dout, int din, uint8_t byte_out)
{
    uint8_t byte_in = 0;
    uint8_t bit;
    int i = 0;

    for (bit = 0x80; bit; bit >>= 1, i++) {
        digitalWrite(dout, (byte_out & bit) ? HIGH : LOW);
        spi_delay();
        digitalWrite(clk, HIGH);
        if (digitalRead(din)) {
			byte_in |= bit;
		}
        spi_delay();
        digitalWrite(clk, LOW);
        spi_delay();
    }
    return byte_in;
}

uint32_t read_adc(unsigned int adc) {
	digitalWrite(CLK, LOW);
    digitalWrite(DOUT, HIGH);
    digitalWrite(LED, LOW);
    delay(dust_charge_delay); // LED CHARGE!
    digitalWrite(LED, HIGH);
    digitalWrite(CS, LOW);
    delayMicroseconds(dust_sensor_delay);
    uint8_t part1, part2, part3;
    part1 = SPI_transfer_byte(CLK, DOUT, DIN, (3 << 6) | ((adc & 0x7) << 3));
    part2 = SPI_transfer_byte(CLK, DOUT, DIN, 0);
    part3 = SPI_transfer_byte(CLK, DOUT, DIN, 0);
    digitalWrite(CS, HIGH);
    digitalWrite(LED, LOW);
    return (part1 & 1) << 9 | (part2 << 1) | (part3 >> 7);
}

void setup() {
    wiringPiSetupGpio();

    pinMode(CLK, OUTPUT);
    pinMode(DOUT, OUTPUT);
    pinMode(DIN, INPUT);
    pinMode(CS, OUTPUT);
	pinMode(LED, OUTPUT);

    digitalWrite(CS, HIGH); 
}

int main() {
    if (wiringPiSetupGpio() == -10) {
        printf("Failed to setup\n");
        return 1;
    }

    pinMode(CLK, OUTPUT);
    pinMode(DOUT, OUTPUT);
    pinMode(DIN, INPUT);
    pinMode(CS, OUTPUT);
	pinMode(LED, OUTPUT);

    digitalWrite(CS, HIGH); 
    
   printf("combined: %d/1024\n", read_adc(1));
	return 0;
}
