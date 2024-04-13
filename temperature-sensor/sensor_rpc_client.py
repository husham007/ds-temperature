import time
import xmlrpc.client

# Connect to the XML-RPC server
server = xmlrpc.client.ServerProxy('http://localhost:8000')

# Call methods exposed by the server
try:
    # Start measurement reading
    server.start_measurement()
    print("Measurement reading started.")

    # Start measurement dispatch
    server.start_dispatch()
    print("Measurement dispatch started.")

    # Get sensor information
    sensor_info = server.get_sensor_info()
    print("Sensor Information:")
    print(sensor_info)

    # Stop measurement reading
    server.stop_measurement()
    print("Measurement reading stopped.")

    # Stop measurement dispatch
    server.stop_dispatch()
    print("Measurement dispatch stopped.")

    # Stop the XML-RPC server
    server.stop_server()
    print("XML-RPC server stopped.")

except Exception as e:
    print(f"Error: {e}")
