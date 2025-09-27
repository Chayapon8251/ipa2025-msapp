import pika
import os
import json
import time
from netmiko import ConnectHandler
from pymongo import MongoClient
from datetime import datetime


def get_mongo_client():
    """
    Creates and returns a MongoDB client instance.
    """
    mongo_uri = os.environ.get("MONGO_URI")
    db_name = os.environ.get("DB_NAME")
    return MongoClient(mongo_uri)[db_name]


def process_message(ch, method, properties, body):
    """
    Processes messages from the RabbitMQ queue.
    """
    try:
        data = json.loads(body.decode("utf-8"))
        print(f" [x] Received {data}")

        # Worker1 and Routers
        router_ip = data.get("ip")
        username = data.get("username")
        password = data.get("password")

        # Handle the case where the router IP is missing
        if not router_ip:
            print(" [!] Missing router IP in message data. Skipping.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        net_connect = ConnectHandler(
            device_type="cisco_ios",
            host=router_ip,
            username=username,
            password=password,
        )

        output = net_connect.send_command("show ip interface brief", use_textfsm=True)
        net_connect.disconnect()
        print(f" [x] Command output from {router_ip}: {output}")

        # Worker1 and Mongo
        client = get_mongo_client()
        collection = client["interface_status"]

        # Prepare data for MongoDB
        doc_to_insert = {
            "router_ip": router_ip,
            "timestamp": datetime.utcnow(),
            "interfaces": output,
        }
        collection.insert_one(doc_to_insert)
        print(f" [x] Data from {router_ip} saved to MongoDB.")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as error:
        print(f" [!] An error occurred: {error}")
        # Acknowledge the message to remove it from the queue
        ch.basic_ack(delivery_tag=method.delivery_tag)


def main():
    """
    Main function to connect to RabbitMQ and start consuming messages.
    """
    rabbitmq_user = os.getenv("RABBITMQ_USER")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS")
    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
    params = pika.ConnectionParameters(host="rabbitmq", credentials=credentials)

    connection = None
    while not connection:
        try:
            connection = pika.BlockingConnection(params)
        except pika.exceptions.AMQPConnectionError:
            print(" [!] Failed to connect to RabbitMQ, retrying in 5 seconds...")
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue="router_jobs")
    channel.basic_consume(queue="router_jobs", on_message_callback=process_message)
    print(" [!] Waiting for messages. To exit press CTRL+C")
    channel.start_consuming()


if __name__ == "__main__":
    main()
