from Maix import GPIO

but_a=GPIO(GPIO.GPIO1, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

but_b = GPIO(GPIO.GPIO2, GPIO.IN, GPIO.PULL_UP) #PULL_UP is required here!

isButtonPressedA = 0
isButtonPressedB = 0

while True:

    if but_a.value() == 0 and isButtonPressedA == 0:
      print("A is PRESSED")
      isButtonPressedA = 1

    if but_a.value() == 1 and isButtonPressedA == 1:
      print("A is RELEASED")
      isButtonPressedA = 0

    if but_b.value() == 0 and isButtonPressedB == 0:
      print("B is PRESSED")
      isButtonPressedB = 1

    if but_b.value() == 1 and isButtonPressedB == 1:
      print("B is RELEASED")
      isButtonPressedB = 0
