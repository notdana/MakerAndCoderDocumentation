import sensor
import image
import lcd
import time
import utime
from machine import UART
from Maix import GPIO
from fpioa_manager import *
import KPU as kpu
import gc

Px = -0.4

fm.register(34,fm.fpioa.UART1_TX)
fm.register(35,fm.fpioa.UART1_RX)
uart = UART(UART.UART1, 115200, timeout=1000, read_buf_len=4096)

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

# Define LAB color thresholds for different colors
thresholds = {
    'red':     (0, 100, 42, 127, 20, 127),   # Red LAB threshold
    'green':   (0, 100, -128, -20, 20, 127), # Green LAB threshold
    'blue':    (0, 100, -128, 0, -128, -20), # Blue LAB threshold
    'orange':  (0, 100, 20, 50, 40, 80)      # Orange LAB threshold
}

target_lab_threshold = (0, 0, 0, 0, 0, 0)
prev_area = 0

task = kpu.load(0x300000)
anchor = (1.889, 2.5245, 2.9465, 3.94056, 3.99987, 5.3658, 5.155437, 6.92275, 6.718375, 9.01025)
a = kpu.init_yolo2(task, 0.5, 0.3, 5, anchor)


roi = (0, 0, 320, 240)  # Adjust according to the area you want to monitor
motion_threshold = 100  # Lower value to be more sensitive to pixel differences
previous_image = sensor.snapshot()


while(True):
    gc.collect()  # Free memory

    img = sensor.snapshot()

    if uart.any():  # Check if data is available in the buffer
        data = uart.read()  # Read the incoming data
        if data:
            decoded_data = data.decode('utf-8')  # Decode the byte string to a normal string
            if decoded_data == "Num Of faces":
                code = kpu.run_yolo2(task, img)
                if code:
                    uart.write(str(len(code)))
                    print(len(code))
                else:
                    print('0')
                    uart.write('0')

            elif  decoded_data.startswith('F') and len(decoded_data) == 2:
                face_number = int(decoded_data[1])
                code = kpu.run_yolo2(task, img)

                if code:
                    if  len(code) > face_number:
                        print(code[face_number].x(),code[face_number].y(),code[face_number].w(),code[face_number].h(),code[face_number].value())
                        face = code[face_number]
                        face_info = "{},{},{},{},{}".format(face.x(), face.y(), face.w(), face.h(), face.value())
                        uart.write(face_info)

            elif decoded_data == "Num Of boxes":
                blobs = img.find_blobs([target_lab_threshold], x_stride = 2, y_stride = 2, pixels_threshold = 100, merge = True, margin = 20)
                if blobs:
                    print(len(blobs))
                    uart.write(str(len(blobs)))
                else:
                    print('0')
                    uart.write('0')

            elif  decoded_data.startswith('C') and len(decoded_data) >= 12:
                code = decoded_data[0]  # This will be 'C'

                # Initialize variables for extracting numbers
                values = []
                num_str = ""

                # Iterate through the string starting from the second character
                for index, char in enumerate(decoded_data[1:]):
                    #print("Character at index {index + 1}:" ,char)  # Debug output
                    if char.isdigit() or (char == '-' and not num_str):  # Check if it's part of a number
                        num_str += char  # Build the number string
                    else:
                        # If we encounter a non-digit and num_str is not empty, process it
                        if num_str:
                            try:
                                values.append(int(num_str))  # Convert to int and append to values list
                            except ValueError as e:
                                print("ValueError:  for num_str:", num_str)  # Debug output for conversion
                            num_str = ""  # Reset for the next number

                # After the loop, check if there's a number left to add
                if num_str:
                    try:
                        values.append(int(num_str))  # Convert the last number
                    except ValueError as e:
                        print("ValueError: {e} for num_str: ",num_str)  # Debug output for conversion

                # Output the results
                print("Code:", code)
                print("Values:", values)
                if len(values) == 6:
                    target_lab_threshold = (values[0], values[1], values[2], values[3], values[4], values[5])

            elif  decoded_data.startswith('B') and len(decoded_data) == 2:
                Box_number = int(decoded_data[1])
                blobs = img.find_blobs([target_lab_threshold], x_stride=2, y_stride=2, pixels_threshold=100, merge=True, margin=20)
                if blobs and len(code) >= Box_number:
                    sorted_blobs = sorted(blobs, key=lambda b: b.area(), reverse=True)
                    print(sorted_blobs[Box_number].x(),sorted_blobs[Box_number].y(),sorted_blobs[Box_number].w(),sorted_blobs[Box_number].h(),sorted_blobs[Box_number].area())
                    box = sorted_blobs[Box_number]
                    box_info = "{},{},{},{},{}".format(box.x(), box.y(), box.w(), box.h(), box.area())
                    uart.write(box_info)

            elif  decoded_data.startswith('M') and len(decoded_data) >= 8:
                code = decoded_data[0]  # This will be 'C'

                # Initialize variables for extracting numbers
                values = []
                num_str = ""

                # Iterate through the string starting from the second character
                for index, char in enumerate(decoded_data[1:]):
                    #print("Character at index {index + 1}:" ,char)  # Debug output
                    if char.isdigit() or (char == '-' and not num_str):  # Check if it's part of a number
                        num_str += char  # Build the number string
                    else:
                        # If we encounter a non-digit and num_str is not empty, process it
                        if num_str:
                            try:
                                values.append(int(num_str))  # Convert to int and append to values list
                            except ValueError as e:
                                print("ValueError:  for num_str:", num_str)  # Debug output for conversion
                            num_str = ""  # Reset for the next number

                # After the loop, check if there's a number left to add
                if num_str:
                    try:
                        values.append(int(num_str))  # Convert the last number
                    except ValueError as e:
                        print("ValueError: {e} for num_str: ",num_str)  # Debug output for conversion

                # Output the results
                print("Code:", code)
                print("Values:", values)
                roi = (values[0], values[1], values[2], values[3])
                print(roi)

            elif  decoded_data.startswith('T') and len(decoded_data) >= 2:
                code = decoded_data[0]  # This will be 'C'

                # Initialize variables for extracting numbers
                values = []
                num_str = ""

                # Iterate through the string starting from the second character
                for index, char in enumerate(decoded_data[1:]):
                    #print("Character at index {index + 1}:" ,char)  # Debug output
                    if char.isdigit() or (char == '-' and not num_str):  # Check if it's part of a number
                        num_str += char  # Build the number string
                    else:
                        # If we encounter a non-digit and num_str is not empty, process it
                        if num_str:
                            try:
                                values.append(int(num_str))  # Convert to int and append to values list
                            except ValueError as e:
                                print("ValueError:  for num_str:", num_str)  # Debug output for conversion
                            num_str = ""  # Reset for the next number

                # After the loop, check if there's a number left to add
                if num_str:
                    try:
                        values.append(int(num_str))  # Convert the last number
                    except ValueError as e:
                        print("ValueError: {e} for num_str: ",num_str)  # Debug output for conversion

                # Output the results
                print("Code:", code)
                print("Values:", values)
                motion_threshold = values[0]
                print(motion_threshold)

            elif decoded_data == "detect Motion":

                sensor.set_pixformat(sensor.GRAYSCALE)  # Grayscale for simplicity
                sensor.set_framesize(sensor.QQVGA)  # Small resolution to save memory
                sensor.skip_frames(time=2000)
                sensor.set_auto_gain(False)  # Consistent lighting
                sensor.set_auto_whitebal(False)

                # Take an initial snapshot
                previous_image = sensor.snapshot()

            elif decoded_data == "Get rate":

                img = sensor.snapshot()

                # Calculate the pixel difference between the current and previous images within the ROI
                diff = img.difference(previous_image)

                # Check if the amount of motion (difference) exceeds a threshold
                diff_value = diff.get_statistics(roi=roi).mean()
                print(diff_value)
                uart.write(str(diff_value))


                # Take an initial snapshot
                previous_image = img.copy()  # Use copy to avoid aliasing

            elif decoded_data == "QR":
                res = img.find_qrcodes()
                if len(res)> 0:
                    print(res[0].payload())
                    uart.write(str(res[0].payload()))

            elif decoded_data == "QRVersion":
                res = img.find_qrcodes()
                if len(res)> 0:
                    print(res[0].version())
                    uart.write(str(res[0].version()))

            elif decoded_data == "BarCode":
                res = img.find_barcodes()
                if len(res)> 0:
                    print(res[0].payload())
                    uart.write(str(res[0].payload()))

            elif decoded_data == "BarType":
                res = img.find_barcodes()
                if len(res)> 0:
                    print(res[0].type())
                    uart.write(str(res[0].type()))

            elif decoded_data == "GetSignal":
                target_lab_threshold = (0, 100, 42, 52, 35, 45)   #R
                blobs = img.find_blobs([target_lab_threshold], x_stride = 2, y_stride = 2, pixels_threshold = 100, merge = True, margin = 20)
                if blobs:
                    print("RED")
                    uart.write("RED")
                else:
                    target_lab_threshold = (0, 100, -38, -28, 30, 40)  #G
                    blobs = img.find_blobs([target_lab_threshold], x_stride = 2, y_stride = 2, pixels_threshold = 100, merge = True, margin = 20)
                    if blobs:
                        print("Green")
                        uart.write("GREEN")
                    else:
                        uart.write("No Signal")


            elif decoded_data == "Discover Color":
                detected_color = None    # Variable to hold detected color

                # Iterate over each color threshold and check for blobs in the image
                for color, threshold in thresholds.items():
                    blobs = img.find_blobs([threshold], pixels_threshold=200, area_threshold=200, merge=True)
                    if blobs:
                        # If blobs are found, draw rectangles and set detected color
                        for blob in blobs:
                            img.draw_rectangle(blob.rect(), color=(255, 0, 0))  # Draw a rectangle around detected blob
                            img.draw_cross(blob.cx(), blob.cy())                # Draw a cross in the middle of the blob
                        detected_color = color
                        break  # Stop once the first color is detected

                # Display the image on the LCD
                lcd.display(img)

                # If a color is detected, print the result
                if detected_color:
                    print("Detected Color: ",detected_color)
                    uart.write(detected_color)
                else:
                    print("No color detected")
                    uart.write("No color detected")

            elif decoded_data == "Normal init":
                sensor.set_pixformat(sensor.RGB565)
                sensor.set_framesize(sensor.QVGA)
                sensor.run(1)
                sensor.set_auto_gain(True)  # Consistent lighting
                sensor.set_auto_whitebal(True)

            else:
                print("Not")

a = kpu.deinit(task)
