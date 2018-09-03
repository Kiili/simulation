import rospy
from std_msgs.msg import Int32
from std_msgs.msg import Float32
from std_msgs.msg import Float64

def validate_speed_percentage_arg(i):
    def validate_speed_percentage(speed_function):
        def validate_percentage(*args):
            percentage = args[i]
            if percentage not in range(-99, 100):
                raise ValueError("Speed percentage must be in range -99 .. 99")
            return speed_function(*args)

        return validate_percentage

    return validate_speed_percentage


def validate_speed_percentage(speed_function):
    return validate_speed_percentage_arg(1)(speed_function)


class PiBot:
    def make_callback_for_sensor(self, attribute_name):
        def callback(value):
            setattr(self, attribute_name, value.data)

        return callback

    def subscribe_to_line_sensors(self):
        prefix = "/robot/line_sensor/"
        suffix = "/intensity"
        rospy.Subscriber(prefix + "left_first" + suffix, Float32,
                         self.make_callback_for_sensor("third_line_sensor_from_left"))
        rospy.Subscriber(prefix + "left_second" + suffix, Float32,
                         self.make_callback_for_sensor("second_line_sensor_from_left"))
        rospy.Subscriber(prefix + "left_third" + suffix, Float32, self.make_callback_for_sensor("leftmost_line_sensor"))
        rospy.Subscriber(prefix + "right_first" + suffix, Float32,
                         self.make_callback_for_sensor("third_line_sensor_from_right"))
        rospy.Subscriber(prefix + "right_second" + suffix, Float32,
                         self.make_callback_for_sensor("second_line_sensor_from_right"))
        rospy.Subscriber(prefix + "right_third" + suffix, Float32,
                         self.make_callback_for_sensor("rightmost_line_sensor"))

    def subscribe_to_ir_sensors(self):
        prefix = "/robot/ir/"
        suffix = "/value"

        rospy.Subscriber(prefix + "front_left" + suffix, Float64, self.make_callback_for_sensor("front_left_ir"))
        rospy.Subscriber(prefix + "front_middle" + suffix, Float64, self.make_callback_for_sensor("front_middle_ir"))
        rospy.Subscriber(prefix + "front_right" + suffix, Float64, self.make_callback_for_sensor("front_right_ir"))

        rospy.Subscriber(prefix + "rear_left_0" + suffix, Float64,
                         self.make_callback_for_sensor("rear_left_straight_ir"))
        rospy.Subscriber(prefix + "rear_left_45" + suffix, Float64,
                         self.make_callback_for_sensor("rear_left_diagonal_ir"))
        rospy.Subscriber(prefix + "rear_left_90" + suffix, Float64, self.make_callback_for_sensor("rear_left_side_ir"))

        rospy.Subscriber(prefix + "rear_right_0" + suffix, Float64,
                         self.make_callback_for_sensor("rear_right_straight_ir"))
        rospy.Subscriber(prefix + "rear_right_45" + suffix, Float64,
                         self.make_callback_for_sensor("rear_right_diagonal_ir"))
        rospy.Subscriber(prefix + "rear_right_90" + suffix, Float64,
                         self.make_callback_for_sensor("rear_right_side_ir"))

    def subscribe_to_encoders(self):
        prefix = "/robot/wheel/"
        suffix = "/position"

        rospy.Subscriber(prefix + "left" + suffix, Int32, self.make_callback_for_sensor("left_wheel_encoder"))
        rospy.Subscriber(prefix + "right" + suffix, Int32, self.make_callback_for_sensor("right_wheel_encoder"))

    def __init__(self, robot_nr=1):
        # IRs
        self.front_left_ir = 0
        self.front_middle_ir = 0
        self.front_right_ir = 0
        self.rear_left_straight_ir = 0
        self.rear_left_diagonal_ir = 0
        self.rear_left_side_ir = 0
        self.rear_right_straight_ir = 0
        self.rear_right_diagonal_ir = 0
        self.rear_right_side_ir = 0

        # Line sensors
        self.leftmost_line_sensor = 0
        self.second_line_sensor_from_left = 0
        self.third_line_sensor_from_left = 0
        self.rightmost_line_sensor = 0
        self.second_line_sensor_from_right = 0
        self.third_line_sensor_from_right = 0

        # Encoders
        self.right_wheel_encoder = 0
        self.left_wheel_encoder = 0

        rospy.init_node("pibot", anonymous=True)

        # Publishers
        self.right_wheel_speed_publisher = rospy.Publisher("/robot/wheel/right/vel_cmd", Float32, queue_size=1)
        self.left_wheel_speed_publisher = rospy.Publisher("/robot/wheel/left/vel_cmd", Float32, queue_size=1)

        # Subscribe
        self.subscribe_to_ir_sensors()
        self.subscribe_to_line_sensors()
        self.subscribe_to_encoders()

        #TODO: copy constants from PiBot
        # Constants
        self.UPDATE_TIME = 0.005
        self.SENSOR_LIMITS = [(100, 1000)] * 6 + [(50, 800)] * 2 + [(0, 1023)] * 6 + [(50, 800)]
        self.WHEEL_DIAMETER = 0.025
        self.TICK_PER_DEGREE = 1

    def get_front_left_ir(self):
        return self.front_left_ir

    def get_front_middle_ir(self):
        return self.front_middle_ir

    def get_front_right_ir(self):
        return self.front_right_ir

    def get_front_irs(self):
        return [self.get_front_left_ir(), self.get_front_middle_ir(), self.get_front_right_ir()]

    def get_rear_left_straight_ir(self):
        return self.rear_left_straight_ir

    def get_rear_left_diagonal_ir(self):
        return self.rear_left_diagonal_ir

    def get_rear_left_side_ir(self):
        return self.rear_left_side_ir

    def get_rear_right_straight_ir(self):
        return self.rear_right_straight_ir

    def get_rear_right_diagonal_ir(self):
        return self.rear_right_diagonal_ir

    def get_rear_right_side_ir(self):
        return self.rear_right_side_ir

    def get_rear_irs(self):
        return [
            self.get_rear_left_side_ir(), self.get_rear_left_diagonal_ir(), self.get_rear_left_straight_ir(),
            self.get_rear_right_straight_ir(), self.get_rear_right_diagonal_ir(), self.get_rear_right_side_ir()
        ]

    def get_irs(self):
        return self.get_front_irs() + self.get_rear_irs()

    def get_leftmost_line_sensor(self):
        return self.leftmost_line_sensor

    def get_second_line_sensor_from_left(self):
        return self.second_line_sensor_from_left

    def get_third_line_sensor_from_left(self):
        return self.third_line_sensor_from_left

    def get_rightmost_line_sensor(self):
        return self.rightmost_line_sensor

    def get_second_line_sensor_from_right(self):
        return self.second_line_sensor_from_right

    def get_third_line_sensor_from_right(self):
        return self.third_line_sensor_from_right

    @validate_speed_percentage
    def set_left_wheel_speed(self, percentage):
        """
        :param percentage: -99 .. 99
        """
        value = Float32()
        value.data = percentage
        self.left_wheel_speed_publisher.publish(value)

    @validate_speed_percentage
    def set_right_wheel_speed(self, percentage):
        """
        :param percentage: -99 .. 99
        """
        value = Float32()
        value.data = percentage
        self.right_wheel_speed_publisher.publish(value)

    @validate_speed_percentage
    def set_wheels_speed(self, percentage):
        """
        :param percentage: -99 .. 99
        """
        self.set_left_wheel_speed(percentage)
        self.set_right_wheel_speed(percentage)

    def get_right_wheel_encoder(self):
        return self.right_wheel_encoder

    def get_left_wheel_encoder(self):
        return self.left_wheel_encoder
