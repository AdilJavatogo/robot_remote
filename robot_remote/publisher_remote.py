import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import Bool # Antager vi har et topic der sender True/False for kryds
import socket
import json

class UdpTwistBridge(Node):
    def __init__(self):
        super().__init__('udp_twist_bridge')

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10) # Vi bruger 'turtle1/cmd_vel' for at matche det, som turtlesim forventer / minus Twist

        # NYT: Abonner på et topic, der fortæller om vi er i et kryds
        self.intersection_sub = self.create_subscription(Bool, '/is_intersection', self.intersection_callback, 10)
        self.is_in_intersection = False # Standard antagelse: vi er på en gang
        
        self.udp_ip = "0.0.0.0"
        self.udp_port = 5000
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        
        # VIGTIGT: Dette forhindrer scriptet i at fryse, mens det venter på data
        self.sock.setblocking(False) 
        
        # Tjekker efter ny data 20 gange i sekundet (0.05) uden at blokere
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info(f"Lytter efter UDP-pakker på port {self.udp_port}...")

    # NYT: Opdater status når vi får ny viden fra lidaren
    def intersection_callback(self, msg):
        self.is_in_intersection = msg.data

    def timer_callback(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            tekst_data = data.decode('utf-8')
            self.get_logger().info(f"Modtog: {tekst_data} fra {addr}")
            
            json_data = json.loads(tekst_data)
            
            
            msg = Twist()

            # Vi kigger efter BÅDE store og små bogstaver for at fikse C#-problemet
            # Hent rå joystick værdier fra MAUI appen
            joystick_forward_backward = float(json_data.get('LinearX', json_data.get('linearX', 0.0)))
            joystick_right_left = float(json_data.get('AngularZ', json_data.get('angularZ', 0.0)))

            # Altid brug X til frem/tilbage
            msg.linear.x = joystick_forward_backward

            # SMART LOGIK HER:
            if self.is_in_intersection:
                # Vi er i et kryds: Brug joystick til at dreje (Angular Z)
                msg.angular.z = joystick_right_left
                msg.linear.y = 0.0
            else:
                # Vi er på en lige gang: Brug joystick til at køre sidelæns (Linear Y)
                msg.linear.y = joystick_right_left
                msg.angular.z = 0.0
            
            self.publisher_.publish(msg)
            
        except BlockingIOError:
            # Ingen data i køen lige nu. Programmet kører bare videre.
            pass
        except json.JSONDecodeError:
            self.get_logger().error("Modtog data, men det var ikke gyldigt JSON")
        except Exception as e:
            self.get_logger().error(f"Uventet fejl: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = UdpTwistBridge()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Lukker ned...")
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()