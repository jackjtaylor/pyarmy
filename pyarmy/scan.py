import asyncio

import aiohttp
from socket import socket, AF_INET, SOCK_DGRAM
from ifaddr import get_adapters
from ipaddress import IPv4Address, ip_interface, IPv4Network


def get_private_ip_address() -> IPv4Address:
    with socket(AF_INET, SOCK_DGRAM) as sock:
        route = "8.8.8.8"
        sock.connect((route, 1))
        sock_ip = sock.getsockname()[0]

    ip_address = IPv4Address(sock_ip)
    assert ip_address.is_private
    return ip_address


def get_private_ip_address_prefix_length(ip_address: IPv4Address) -> int:
    adapters = get_adapters()
    for adapter in adapters:
        if adapter.ips:
            for ip in adapter.ips:
                if ip.ip == str(ip_address):
                    return ip.network_prefix
    raise ValueError(f"No networks found to match {ip_address}")


async def query_host(ip_address: IPv4Address) -> IPv4Address | None:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://{ip_address}:9393/role") as response:
                role = await response.text()
                if role == "Manager":
                    return ip_address
    except:
        pass


async def find_manager(network: IPv4Network) -> IPv4Address:
    tasks = [
        asyncio.create_task(scan_host(host))
        for host in interface.network.hosts()
        if host.version == 4 and str(host) != str(host_ip)
    ]

    other_open_hosts = [host for host in await asyncio.gather(*tasks) if host]


async def main():
    host_ip = get_private_ip_address()

    host_ip_prefix_length = get_private_ip_address_prefix_length(host_ip)

    interface = ip_interface(f"{str(host_ip)}/{host_ip_prefix_length}")
    network = interface.network
    assert network.version == 4

    manager_ip = await find_manager(interface.network)


if __name__ == "__main__":
    asyncio.run(main())
