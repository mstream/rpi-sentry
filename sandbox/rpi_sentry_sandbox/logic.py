from gpiozero import LED, Button
from time import sleep


def logic():
    led1 = LED(21)
    led1.blink()

    def button_pressed():
        print("button pressed!")
        led2.toggle()

    led2 = LED(22)
    button = Button(11)
    button.when_pressed = button_pressed

    while True:
        sleep(0.1)
