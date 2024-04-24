import time
import xmlrpc.client

# Connect to the XML-RPC server
sensor_helsinki = xmlrpc.client.ServerProxy('http://localhost:8001')
sensor_lahti = xmlrpc.client.ServerProxy('http://localhost:8002')

# Call methods exposed by the server
try:
    # Start measurement reading
    sensor_helsinki.start_measurement()
    sensor_lahti.start_measurement()
    print("Measurement reading started.")

    # Start measurement dispatch
    sensor_helsinki.start_dispatch()
    sensor_lahti.start_dispatch()
    print("Measurement dispatch started.")

    # Get sensor information
    sensor_info_helsinki = sensor_helsinki.get_sensor_info()
    sensor_info_lahti = sensor_lahti.get_sensor_info()
    print("Sensor Information Helsinki:")
    print(sensor_info_helsinki)
    print("Sensor Information:")
    print(sensor_info_lahti)

    """
    # Stop measurement reading
    server.stop_measurement()
    print("Measurement reading stopped.")

    # Stop measurement dispatch
    server.stop_dispatch()
    print("Measurement dispatch stopped.")

    # Stop the XML-RPC server
    server.stop_server()
    print("XML-RPC server stopped.")
    """
except Exception as e:
    print(f"Error: {e}")
