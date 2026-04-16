import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped #Twist
import socket
import json

class UdpTwistBridge(Node):
    def __init__(self):
        super().__init__('udp_twist_bridge')
        self.publisher_ = self.create_publisher(TwistStamped, '/cmd_vel', 10) # Vi bruger 'turtle1/cmd_vel' for at matche det, som turtlesim forventer / minus Twist
        
        self.udp_ip = "0.0.0.0"
        self.udp_port = 5000
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.udp_ip, self.udp_port))
        
        # VIGTIGT: Dette forhindrer scriptet i at fryse, mens det venter på data
        self.sock.setblocking(False) 
        
        # Tjekker efter ny data 20 gange i sekundet (0.05) uden at blokere
        self.timer = self.create_timer(0.05, self.timer_callback)
        self.get_logger().info(f"Lytter efter UDP-pakker på port {self.udp_port}...")

    def timer_callback(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            tekst_data = data.decode('utf-8')
            self.get_logger().info(f"Modtog: {tekst_data} fra {addr}")
            
            json_data = json.loads(tekst_data)
            
            msg = TwistStamped()            #msg = Twist()

            # Tilføj det obligatoriske tidsstempel og frame (kræves af Webots/Jazzy)
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.header.frame_id = 'base_link'

            # Vi kigger efter BÅDE store og små bogstaver for at fikse C#-problemet
            msg.linear.x = float(json_data.get('LinearX', json_data.get('linearX', 0.0)))
            msg.angular.z = float(json_data.get('AngularZ', json_data.get('angularZ', 0.0)))
            
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
        node.get_logger().info("Lukker pænt ned...")
    finally:
        node.sock.close()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()