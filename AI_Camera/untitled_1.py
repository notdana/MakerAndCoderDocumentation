import sensor

sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.run(1)

target_lab_threshold = (0, 100, 25, 35, -52, -42)

prev_area = 0

while True:
    img = sensor.snapshot()

    blobs = img.find_blobs([target_lab_threshold], x_stride = 2, y_stride = 2, pixels_threshold = 100, merge = True, margin = 20)

    if blobs:
        max_area = 0
        target = blobs[0]
        for b in blobs:
            if b.area() > max_area:
                max_area = b.area()
                target = b

        prev_area = target.area()
        tmp = img.draw_rectangle(target[0:4])
        tmp = img.draw_cross(target[5], target[6])
