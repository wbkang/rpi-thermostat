#include <stdio.h>
#include <wiringPi.h>
#include <stdint.h>
#include <Python.h>

// spi clock delay
static unsigned int delayMs = 10;
static const unsigned int dust_sensor_delay = 28; // must wait 28 microsec after flash
static const unsigned int dust_charge_delay = 100; // 100millis

static void spi_delay(void) {
	delayMicroseconds(delayMs);
}

typedef struct {
    unsigned int clk;
    unsigned int din;
    unsigned int dout;
    unsigned int cs;
} spi_info;

static unsigned int g_led_pin;
static spi_info g_spi_info;

static PyObject *DustError;

/* somewhat from wikipedia */
static uint8_t SPI_transfer_byte(spi_info info, uint8_t byte_out)
{
    unsigned int clk = info.clk;
    unsigned int din = info.din;
    unsigned int dout = info.dout;
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

// Read from Sharp GP2Y1010 dust sensor via MCP3008 dust sensor
static PyObject *
read_dust(PyObject *self, PyObject *args) {
    unsigned int adc;
    
    if (!PyArg_ParseTuple(args, "i", &adc)) {
        return NULL;
    }

    if (adc < 0 || adc > 7) {
        return PyErr_Format(DustError, "adc[%d] out of range, has to be 0-7", adc);
    }
    
    uint8_t part1, part2, part3;
    Py_BEGIN_ALLOW_THREADS
    spi_info info = g_spi_info;
    unsigned int clk = info.clk;
    unsigned int dout = info.dout;
    unsigned int cs = info.cs;
    unsigned int led = g_led_pin;

	digitalWrite(clk, LOW);
    digitalWrite(dout, HIGH);
    digitalWrite(led, LOW);
    delay(dust_charge_delay); // LED CHARGE!
    digitalWrite(led, HIGH);
    digitalWrite(cs, LOW);
    spi_delay();
    delayMicroseconds(dust_sensor_delay);
    // read mcp3008 bit-bang style
    part1 = SPI_transfer_byte(info, (3 << 6) | ((adc & 0x7) << 3));
    part2 = SPI_transfer_byte(info, 0);
    part3 = SPI_transfer_byte(info, 0);
    digitalWrite(cs, HIGH);
    digitalWrite(led, LOW);
    Py_END_ALLOW_THREADS
    unsigned int value = (part1 & 1) << 9 | (part2 << 1) | (part3 >> 7);
    return PyLong_FromLong(value);
}

static PyObject*
setup(PyObject *self, PyObject *args, PyObject *keywords) {
    
    static char *kwlist[] = {"clk", "dout", "din", "cs", "led", NULL};
    unsigned int clk, dout, din, cs, led;

    if (!PyArg_ParseTupleAndKeywords(
                args, 
                keywords,
                "iiiii",
                kwlist,
                &clk,
                &dout,
                &din,
                &cs,
                &led)) {
        return NULL;
    }

    Py_BEGIN_ALLOW_THREADS
    wiringPiSetupGpio();
    g_spi_info = (spi_info) { clk = clk, .din = din, .dout = dout, .cs = cs};
    g_led_pin = led;
    pinMode(clk, OUTPUT);
    pinMode(dout, OUTPUT);
    pinMode(din, INPUT);
    pinMode(cs, OUTPUT);
	pinMode(led, OUTPUT);
    digitalWrite(cs, HIGH); 
    digitalWrite(clk, HIGH); 
    digitalWrite(dout, HIGH); 
    Py_END_ALLOW_THREADS
    Py_RETURN_NONE;
}

static PyMethodDef methods[] = {
    {"setup", setup, METH_VARARGS | METH_KEYWORDS, "Setup gpio"},
    {"read", read_dust, METH_VARARGS, "Read dust value between 0 and 1023"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef cdustmodule ={
    PyModuleDef_HEAD_INIT,
    "cdust",
    NULL,
    -1,
    methods
};

PyMODINIT_FUNC PyInit_cdust(void) {
    PyObject *m = PyModule_Create(&cdustmodule);
    if (m == NULL) {
        return NULL;
    }
    DustError = PyErr_NewException("cdust.error", NULL, NULL);
    Py_INCREF(DustError);
    PyModule_AddObject(m, "error", DustError);
    return m;
}
