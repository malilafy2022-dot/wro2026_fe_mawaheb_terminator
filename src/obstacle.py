
from pybricks.ev3devices import GyroSensor, Motor, UltrasonicSensor, ColorSensor
from pybricks.hubs import EV3Brick
from pybricks.messaging import AppData
from pybricks.parameters import Axis, Button, Direction, Port, Stop, Color
from pybricks.tools import StopWatch, multitask, run_task, wait
from ustruct import unpack

DIRECTION_RIGHT = "right"
DIRECTION_LEFT = "left"

# Set up.
ev3 = EV3Brick()
motor_1 = Motor(Port.D, Direction.COUNTERCLOCKWISE)
motor_2 = Motor(Port.C, Direction.CLOCKWISE)
motor_steering = Motor(Port.A, Direction.COUNTERCLOCKWISE)
gyro = GyroSensor(Port.S4)
ultrasonic_right = UltrasonicSensor(Port.S2)
ultrasonic_left = UltrasonicSensor(Port.S3)
ultrasonic_front = UltrasonicSensor(Port.S1)
app = AppData([(0, 10)])
angle = 0
target_angle = 0
speed_drive = 450
kp_angle = -2.4
kp_camera = 0.04
kp_distance = 0
distance_front = 0
distance_right = 0
distance_left = 0
distance_side_threshold = 1800
distance_front_threshold = 200
distance_side_following = 450
x_green = 1180
x_red = 100
y_threshold = 0
y_ref = 80
stop_watch_section = StopWatch()
stop_watch_total = StopWatch()
turns = 0
cls = -1
x = -1
y = -1
w = -1
h = -1
direction = None

async def read_camera():
    global cls, x, y, w, h
    await wait(0)
    while True:
        await wait(0)
        cls, x, y, w, h = unpack('hhhhh', app.get_bytes(0))

async def check_gyro():
    global angle
    await wait(0)
    angle = gyro.angle()
    await wait(250)
    if abs(angle - gyro.angle()) >= 4:
        await ev3.speaker.beep(500, 100)
        raise SystemExit

async def subtask():
    global distance_right
    distance_right = await ultrasonic_right.distance()

async def subtask2():
    global distance_left
    distance_left = await ultrasonic_left.distance()

async def subtask3():
    global distance_front
    distance_front = await ultrasonic_front.distance()

async def read_sensors():
    global angle, distance_right, distance_left, distance_front
    await wait(0)
    while True:
        await wait(0)
        angle = gyro.angle()
        await multitask(
            subtask(),
            subtask2(),
            subtask3(),
        )

def adaptive_gain():
    return max(y / y_ref, 0.4)

async def move():
    global target_angle, turns , direction
    await wait(0)
    motor_steering.reset_angle(0)
    while True:
        await wait(0)
        if direction == DIRECTION_RIGHT and distance_right >= distance_side_threshold and stop_watch_section.time() >= 5000 and abs(angle-target_angle)<15:
            ev3.light.off()         
            stop_watch = StopWatch()
            while distance_front > distance_front_threshold and stop_watch.time() < 3000:
                await wait(0)
                motor_1.run(speed_drive)
                motor_2.run(speed_drive)
                motor_steering.track_target(kp_angle * (angle - target_angle))
            motor_1.hold()
            motor_2.hold()
            target_angle = target_angle + 90
            motor_steering.track_target(-50)
            stop_watch = StopWatch()
            while abs(angle - target_angle) > 10 and stop_watch.time() < 2000:
                await wait(0)
                motor_1.run(-1*speed_drive)
                motor_2.run(-1*speed_drive)
            turns = turns + 1
            stop_watch_section.reset()
        elif direction == DIRECTION_LEFT and distance_left >= distance_side_threshold and stop_watch_section.time() >= 5000 and abs(angle-target_angle)<15:
            ev3.light.off()         
            stop_watch = StopWatch()
            while distance_front > distance_front_threshold and stop_watch.time() < 3000:
                await wait(0)
                motor_1.run(speed_drive)
                motor_2.run(speed_drive)
                motor_steering.track_target(kp_angle * (angle - target_angle))
            motor_1.hold()
            motor_2.hold()
            target_angle = target_angle - 90
            motor_steering.track_target(50)
            stop_watch = StopWatch()
            while abs(angle - target_angle) > 10 and stop_watch.time() < 2000:
                await wait(0)
                motor_1.run(-1*speed_drive)
                motor_2.run(-1*speed_drive)
            turns = turns + 1
            stop_watch_section.reset()
        elif direction == None and distance_right >= distance_side_threshold  and stop_watch_section.time() >= 2500 and abs(angle-target_angle)<15:
            ev3.light.off()
            ev3.screen.print("Left: ", distance_left, " Right: ", distance_right)
            direction = DIRECTION_RIGHT
            stop_watch = StopWatch()
            while distance_front > distance_front_threshold and stop_watch.time() < 3000:
                await wait(0)
                motor_1.run(speed_drive)
                motor_2.run(speed_drive)
                motor_steering.track_target(kp_angle * (angle - target_angle))
            motor_1.hold()
            motor_2.hold()
            
            target_angle = target_angle + 90
            motor_steering.track_target(-50)

            stop_watch = StopWatch()
            while abs(angle - target_angle) > 10 and stop_watch.time() < 2000:
                await wait(0)
                motor_1.run(-1*speed_drive)
                motor_2.run(-1*speed_drive)
            turns = turns + 1
            stop_watch_section.reset()            
        elif direction == None and distance_left >= distance_side_threshold and stop_watch_section.time() >= 2500 and abs(angle-target_angle)<15:
            ev3.light.off()
            ev3.screen.print("Left: ", distance_left, " Right: ", distance_right)
            direction = DIRECTION_LEFT            
            stop_watch = StopWatch()
            while distance_front > distance_front_threshold and stop_watch.time() < 3000:
                await wait(0)
                motor_1.run(speed_drive)
                motor_2.run(speed_drive)
                motor_steering.track_target(kp_angle * (angle - target_angle))
            motor_1.hold()
            motor_2.hold()
            target_angle = target_angle - 90
            motor_steering.track_target(50)
            stop_watch = StopWatch()
            while abs(angle - target_angle) > 10 and stop_watch.time() < 2000:
                await wait(0)
                motor_1.run(-1*speed_drive)
                motor_2.run(-1*speed_drive)
            turns = turns + 1
            stop_watch_section.reset()
        elif turns >= 12 and stop_watch_section.time() >= 5000:
            ev3.screen.print(stop_watch_total.time() / 1000)
            while Button.CENTER not in ev3.buttons.pressed():
                await wait(0)
                motor_1.hold()
                motor_2.hold()
                motor_steering.hold()
            raise SystemExit
        else:
            motor_1.run(speed_drive)
            motor_2.run(speed_drive)
            if abs(x-645) < 200 and y >= 200:
                ev3.light.off()
                motor_steering.track_target(0)
                stop_watch = StopWatch()
                while stop_watch.time() < 300:
                    await wait(0)
                    motor_1.run(-1 * speed_drive)
                    motor_2.run(-1*speed_drive)
            elif cls == 0 and x < x_green and y > y_threshold :
                ev3.light.on(Color.GREEN)
                motor_steering.track_target((x-x_green)*kp_camera*adaptive_gain())
            elif cls == 1 and x > x_red and y > y_threshold :
                ev3.light.on(Color.RED)
                motor_steering.track_target((x-x_red)*kp_camera*adaptive_gain()) 
            elif direction == DIRECTION_RIGHT:
                ev3.light.off()
                motor_steering.track_target(kp_angle * (angle - target_angle) + kp_distance * (distance_left - distance_side_following))

            elif direction == DIRECTION_LEFT:
                ev3.light.off()                
                motor_steering.track_target(kp_angle * (angle - target_angle) + kp_distance * (distance_right - distance_side_following))
            else:
                ev3.light.off()
                motor_steering.track_target(kp_angle * (angle - target_angle))

async def main():
    await check_gyro()
    await multitask(
        read_sensors(),
        read_camera(),
        move(),
    )


try:
    run_task(main())
except Exception as e:
    ev3.screen.print(str(e))
    wait(30000)