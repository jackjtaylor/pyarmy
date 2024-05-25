# pyright: strict

import asyncio
from socket import socket, AF_INET, SOCK_DGRAM

from aiohttp import ClientSession, ClientTimeout, ClientConnectorError
from ifaddr import get_adapters
from ipaddress import IPv4Address, ip_interface, IPv4Network


def get_local_network_address() -> IPv4Address:
    """
    This function gets the local network address of this device.
    This functions opens a connection to a fake server and port. This works to get the local
    network address, as the created socket uses a datagram (UDP) protocol and therefore does not
    need to handshake with the server.
    This means no data is ever transmitted, yet the local network address can be found.
    :return: The network address
    """
    sock = socket(AF_INET, SOCK_DGRAM)

    # This creates a fake server and port to be used
    server = "1"
    port = 1

    with sock:
        sock.connect((server, port))
        address = sock.getsockname()[0]

    return IPv4Address(address)


def get_network_prefix_length_by_address(address: IPv4Address) -> int:
    """
    This function finds the subnet mask length of a network. This function gets all network
    interfaces present on the device, and finds which interface uses the supplied address.
    If this function is used with the address used to access the internet, more information about
    the local network can be revealed.
    :param address: The network prefix length
    :return: int
    """
    for adapter in get_adapters():
        # This asks if the adapter has any addresses
        if adapter.ips:
            # This loops through each network linked to an adapter
            for ip in adapter.ips:
                if ip.ip == str(address):
                    return ip.network_prefix

    raise ValueError(f"There were no adapters found that matched {address}.")


async def get_role(address: IPv4Address) -> str | None:
    """
    This function gets the role of an address, by querying the corresponding application.
    If the application is running on the address, a role will be returned.
    If no application is present, or the device is not running or accepting connections,
    nothing will be returned.
    :param address: The address to query
    :return: The role of the address
    """
    try:
        async with ClientSession(timeout=ClientTimeout(total=1)) as session:
            request = f"http://{address}:9393/role"

            # This requests the address for a role response
            async with session.get(request) as response:
                role = await response.text()

                # This checks what role was found
                if "Manager" in role:
                    return "Manager"

    # This handles other cases, where a response is missing or incorrect
    except ClientConnectorError:
        return None
    else:
        raise RuntimeError("There has been an unknown error.")


async def find_manager(network: IPv4Network) -> IPv4Address | None:
    tasks = [
        asyncio.create_task(get_role(host))
        for host in network.hosts()
        if str(host) != "192.168.0.164"
    ]

    managers = tuple(host for host in await asyncio.gather(*tasks) if host)
    if len(managers) > 1:
        raise ValueError(f"Multiple managers found for {network}")

    if len(managers) == 1:
        return managers[0]


async def main():
    local_address = get_local_network_address()

    network_prefix_length = get_network_prefix_length_by_address(local_address)

    interface = ip_interface(f"{str(local_address)}/{network_prefix_length}")

    network = interface.network
    assert network.version == 4

    manager_ip = await find_manager(network)
    print(manager_ip)


if __name__ == "__main__":
    asyncio.run(main())
