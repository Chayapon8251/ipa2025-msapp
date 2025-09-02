import pika

connection = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
channel = connection.channel()

channel.exchange_declare(exchange="jobs", exchange_type="direct")
channel.queue_declare(queue="router_jobs")
channel.queue_bind(queue="router_jobs", exchange="jobs", routing_key="check_interfaces")

channel.basic_publish(exchange="jobs", routing_key="check_interfaces", body="192.168.1.44")

connection.close()