
from pybricks.ev3devices import GyroSensor, Motor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.messaging import AppData
from pybricks.parameters import Axis, Button, Direction, Port, Stop, Color
from pybricks.tools import StopWatch, multitask, run_task, wait
from ustruct import unpack

# Set up.
ev3 = EV3Brick()
try:
    motor_1 = Motor(Port.D, Direction.COUNTERCLOCKWISE)
    motor_2 = Motor(Port.C, Direction.CLOCKWISE)
    motor_steering = Motor(Port.A, Direction.COUNTERCLOCKWISE)
    gyro = GyroSensor(Port.S4)
    ultrasonic_right = UltrasonicSensor(Port.S2)
    ultrasonic_left = UltrasonicSensor(Port.S3)

    angle = 0
    target_angle = 0
    speed_drive = 1500
    kp_angle = -0.7

    distance_front = 0
    distance_right = 0
    distance_left = 0
    distance_side_threshold = 1300

    stop_watch_section = StopWatch()
    stop_watch_total = StopWatch()
    turns = 0
    direction = "none"


    async def subtask():
        global distance_right
        distance_right = await ultrasonic_right.distance()

    async def subtask2():
        global distance_left
        distance_left = await ultrasonic_left.distance()

    async def read_sensors():
        global angle, distance_right, distance_left
        await wait(0)
        while True:
            await wait(0)
            angle = gyro.angle()
            await multitask(
                subtask(),
                subtask2(),
            )

    async def move():
        global target_angle, turns , direction
        await wait(0)
        motor_steering.reset_angle(0)
        while True:
            await wait(0)
            motor_1.run(speed_drive)
            motor_2.run(speed_drive)

            if (distance_right >= distance_side_threshold or distance_left >= distance_side_threshold) and (stop_watch_section.time() > 1500) and direction == "none" :
                if distance_right >= distance_side_threshold:
                    direction = "right"
                    target_angle = target_angle + 89
                    motor_steering.track_target(target_angle)
                    stop_watch_section.reset() 
                    turns = turns + 1                    
                else:
                    direction = "left"
                    target_angle = target_angle - 89
                    motor_steering.track_target(target_angle)
                    stop_watch_section.reset() 
                    turns = turns + 1
                   
            elif (distance_right >= distance_side_threshold and stop_watch_section.time() > 2300) and direction == "right":
                target_angle = target_angle + 89 
                motor_steering.track_target(target_angle)
                turns = turns + 1
                stop_watch_section.reset()
            elif (distance_left >= distance_side_threshold and stop_watch_section.time() > 2300) and direction == "left":
                target_angle = target_angle - 89
                motor_steering.track_target(target_angle)
                turns = turns + 1
                stop_watch_section.reset()        
            elif turns >= 12 and stop_watch_section.time() >= 1400:
                ev3.screen.print(stop_watch_total.time() / 1000)
                while Button.CENTER not in ev3.buttons.pressed():
                    await wait(0)
                    motor_1.hold()
                    motor_2.hold()
                    motor_steering.hold()
                raise SystemExit

            else:
                if distance_right <= 250:
                    motor_steering.track_target(-5)
                elif distance_left <= 250:
                  motor_steering.track_target(5)
                else:
                    motor_steering.track_target(kp_angle * (angle - target_angle))

    async def main():
        await multitask(
            read_sensors(),
            move(),
        )


    run_task(main())

except Exception as e:
    ev3.screen.print(str(e))    
    wait(10000)