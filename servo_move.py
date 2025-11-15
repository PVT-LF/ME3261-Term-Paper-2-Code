# Sending to esp32 via serial port

import serial
import serial.tools.list_ports
import time

ports = serial.tools.list_ports.comports()

for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))

# Open the serial port (ensure this is the correct port for your ESP32)
ser = serial.Serial('COM7', 115200)

# Send a signal to the ESP32 to move the servo
def send_signal_to_esp32(signal):
    ser.write(signal.encode())  # Send the signal as bytes
    time.sleep(2)  # Wait for ESP32 to process the signal

# Example of sending a command based on the model's prediction
#if predicted_class == 1:  # For example, if class 1 is detected
    #send_signal_to_esp32("MOVE_SERVO")

# testing functionality with prime number list
if __name__ == '__main__':
    num = 2
    primes = set()
    while num < 100:
        print(num)
        if num == 2:
            primes.add(num)
        else:
            is_prime = True
            for prime in primes:
                if num % prime == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.add(num)
                print("is prime!")
                send_signal_to_esp32("MOVE_SERVO")
        time.sleep(0.5)
        num += 1


"""
// C++ code for ESP32
#include <ESP32Servo.h>

Servo servo1;  // Create a Servo object

void setup() {
    Serial.begin(115200);  // Initialize serial communication
    servo1.attach(13);     // Attach the servo to pin 13
    while (!Serial){;}     // Wait for Serial
}
// servo 500 - 2500
void loop() {
    if (Serial.available()) {
        String command = Serial.readString();  // Read the incoming serial command

        if (command == "MOVE_SERVO") {
            servo1.writeMicroseconds(1250); // Move servo to 90 degrees
            delay(500);  // Wait for 1 second
            servo1.writeMicroseconds(500); // Move servo back to 0 degrees
        }
        else {
            servo1.writeMicroseconds(500); // Move servo back to 0 degrees
        }
    }
}

"""
