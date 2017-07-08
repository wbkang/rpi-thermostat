
data = {'conn_string': 'sqlite:////home/pi/weather.db'}
dust = {'mcp3008':
        {'clk':18,
         'miso': 23,
         'mosi': 24,
         'cs': 25,
         'led': 17
         },
        'sample_interval': 30
        }
temphumid = {'dht11':
             {'pin':4},
             'sample_interval': 30
             }
temppressure = {'pressure':
                {'correction':1.63},
                'sample_interval': 30
                }


