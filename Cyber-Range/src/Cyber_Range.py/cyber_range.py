import docker
import time

client = docker.from_env()

NETWORK_NAME = "cyber_range_net"

ATTACKER_IMAGE = "custom-attacker"
ATTACKER_NAME = "attacker"

VICTIM_IMAGE = "vulnerables/web-dvwa"
VICTIM_NAME = "victim"
VICTIM_PORTS = {"80/tcp": 8000}


def create_network():
    try:
        net = client.networks.get(NETWORK_NAME)
        print(f"[+] Network {NETWORK_NAME} already exists")
    except docker.errors.NotFound:
        print(f"[+] Creating network {NETWORK_NAME}")
        net = client.networks.create(NETWORK_NAME, driver="bridge")
    return net


def start_container(name, image, ports=None, env=None):
    print(f"[+] Starting container {name} ({image})")
    container = client.containers.run(
        image,
        name=name,
        detach=True,
        tty=True,
        ports=ports or {},
        environment=env or {},
    )
    return container


def setup_lab():
    net = create_network()

    victim = start_container(
        VICTIM_NAME,
        VICTIM_IMAGE,
        ports=VICTIM_PORTS,
        env={"MYSQL_PASS": "password"}
    )
    net.connect(victim)

    attacker = start_container(
        ATTACKER_NAME,
        ATTACKER_IMAGE
    )
    net.connect(attacker)

    print("\n[+] Lab setup complete")
    print(f"    Victim (DVWA): http://localhost:{list(VICTIM_PORTS.values())[0]}")
    print("    Attacker shell: docker exec -it attacker /bin/bash\n")

    return attacker, victim


def teardown_lab():
    print("\n[+] Tearing down lab...")
    for name in [ATTACKER_NAME, VICTIM_NAME]:
        try:
            c = client.containers.get(name)
            print(f"    Stopping & removing {name}")
            c.stop()
            c.remove()
        except docker.errors.NotFound:
            pass

    try:
        net = client.networks.get(NETWORK_NAME)
        print(f"    Removing network {NETWORK_NAME}")
        net.remove()
    except docker.errors.NotFound:
        pass

    print("[+] Lab teardown complete")


if __name__ == "__main__":
    try:
        attacker, victim = setup_lab()
        print("[+] Waiting for services to come online...")
        time.sleep(15)

        print("[+] Lab is live. Press Enter to teardown.")
        input()
    finally:
        teardown_lab()
