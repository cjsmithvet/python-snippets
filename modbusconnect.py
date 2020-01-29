from pymodbus.client.sync import ModbusTcpClient

client = ModbusTcpClient('10.0.0.120')
print "I think I connected"
client.write_coil(1, True)
print "I wrote something"
result = client.read_coils(1,1)
print "I attempted a read"
print(result.bits[0])
client.close()
