import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import socket
import json

class UdpTwistBridge(Node):
    def __init__(self):
        super().__init__('udp_twist_bridge')
        
        # Opret en publisher til Twist-beskeden (standard topic til bevægelse)
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # --- Opsætning af UDP Server ---
        self.udp_ip = "0.0.0.0" # Lytter på alle netværkskort (WiFi/Ethernet)
        self.udp_port = 5000    # VIGTIGT: Denne port skal matche porten i din MAUI UdpSenderService
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        self.sock.setblocking(False) # Gør socket non-blocking, så ROS2 spin-loopet ikke fryser
        
        # Opret en timer, der kører 50 gange i sekundet (50 Hz) for at læse nye UDP pakker
        self.timer = self.create_timer(0.02, self.receive_udp_callback)
        self.get_logger().info(f"Starter UDP til Twist bro. Lytter på port {self.udp_port}...")

    def receive_udp_callback(self):
        try:
            # Læs data fra MAUI (1024 bytes buffer)
            data, addr = self.sock.recvfrom(1024)

            # Se om data kommer frem
            self.get_logger().info(f"Modtog data fra {addr}: {data}")

            message = data.decode('utf-8')
            
            # Konverter JSON tekst til et Python dictionary
            # Vi forventer f.eks.: {"linearX": 0.5, "angularZ": -0.2}
            json_data = json.loads(message)
            
            # Opret ROS2 Twist beskeden
            twist_msg = Twist()
            twist_msg.linear.x = float(json_data.get('linearX', 0.0))
            twist_msg.angular.z = float(json_data.get('angularZ', 0.0))
            
            # Send beskeden ud på ROS2 netværket
            self.publisher_.publish(twist_msg)
            
            # Fjern udkommenteringen af linjen under, hvis du vil se data i konsollen ved modtagelse
            # self.get_logger().info(f"Modtog: Lin_x={twist_msg.linear.x}, Ang_z={twist_msg.angular.z}")
            
        except BlockingIOError:
            # Sker hele tiden, fordi der ikke altid er nye pakker klar. Det ignorerer vi bare.
            pass
        except json.JSONDecodeError:
            self.get_logger().error("Kunne ikke læse JSON. Er du sikker på MAUI sender valid JSON?")
        except Exception as e:
            self.get_logger().error(f"Uventet fejl: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = UdpTwistBridge()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()