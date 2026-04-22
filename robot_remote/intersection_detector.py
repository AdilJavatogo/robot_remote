import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool

class IntersectionDetectorNode(Node):
    def __init__(self):
        super().__init__('intersection_detector')

        # Opret en subscriber for lidar data (/scan)
        self.subscription = self.create_subscription(LaserScan,'/base_scan',self.lidar_callback,10)

        # Opret en publisher for kryds-status (/is_intersection)
        self.publisher_ = self.create_publisher(Bool, '/is_intersection', 10)

        # Parametre for detektion (juster efter behov)
        self.min_side_distance = 1.0  # Mindste afstand til siderne før det betragtes som åbent (i meter)
        # Vælg vinkler for venstre og højre side. Eksempel: +/- 90 grader
        # Lidar data er typisk i radianer. 90 grader = pi/2
        self.angle_offset_deg = 90.0
        self.angle_offset_rad = self.angle_offset_deg * (3.14159 / 180.0)
        self.angle_width_deg = 20.0 # Hvor stor en vinkel-vifte vi ser på for hver side
        self.angle_width_rad = self.angle_width_deg * (3.14159 / 180.0)

    def lidar_callback(self, msg):
        # Dette kaldes hver gang, der kommer nye lidardata

        # Find indekser i ranges-listen, der svarer til siderne
        left_angle_center = self.angle_offset_rad # +/- 90 grader, juster evt. alt efter din lidar's orientering
        right_angle_center = -self.angle_offset_rad

        def get_average_range(msg, angle_center, angle_width):
            # Forenklet funktion til at gennemsnitlig-gøre rækkevidden for en bestemt vinkel-vifte
            # (Vigtigt: Du skal også håndtere "uendelige" eller "ugyldige" målinger i en rigdig løsning)
            start_angle = angle_center - (angle_width / 2.0)
            end_angle = angle_center + (angle_width / 2.0)

            total_range = 0.0
            valid_ranges = 0

            # Løb igennem ranges og akkumuler gyldige målinger
            for i, r in enumerate(msg.ranges):
                current_angle = msg.angle_min + (i * msg.angle_increment)
                # Tjek om vinklen er inden for vores vifte
                if start_angle <= current_angle <= end_angle:
                    if msg.range_min < r < msg.range_max and not (r != r): # Tjek for gyldig rækkevidde og ikke NaN
                        total_range += r
                        valid_ranges += 1

            if valid_ranges > 0:
                return total_range / valid_ranges
            else:
                return 1000.0 # Hvis ingen gyldige målinger, antag uendelig åbent (men tænk over en bedre håndtering i produktion)

        # Få gennemsnitsafstande til siderne
        left_average = get_average_range(msg, left_angle_center, self.angle_width_rad)
        right_average = get_average_range(msg, right_angle_center, self.angle_width_rad)

        # Detekter om der er et kryds
        intersection_detected = left_average > self.min_side_distance and right_average > self.min_side_distance

        # Opret en Bool besked og udgiv kryds-status
        status_msg = Bool()
        status_msg.data = intersection_detected
        self.publisher_.publish(status_msg)

        if intersection_detected:
            self.get_logger().info('Kryds detekteret!')

def main(args=None):
    rclpy.init(args=args)
    node = IntersectionDetectorNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()