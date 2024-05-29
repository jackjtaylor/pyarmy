# pyright: strict

import asyncio
from collections import deque
from socket import socket, AF_INET, SOCK_DGRAM
from typing import Optional

from aiohttp import ClientSession, ClientTimeout, ClientConnectorError
from ifaddr import get_adapters
from ipaddress import IPv4Address, IPv4Network, ip_interface

type IPv4AddressesAndRole = deque[tuple[IPv4Address, str]]


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
                if ip.is_IPv4 and ip.ip == str(address):
                    return ip.network_prefix

    raise ValueError(f"There were no adapters found that matched {address}.")


async def get_role(address: IPv4Address) -> tuple[IPv4Address, Optional[str]]:
    """
    This function gets the role of an address, by querying the corresponding application.
    If the application is running on the address, a role will be returned.
    If no application is present, or the device is not running or accepting connections,
    nothing will be returned.
    :todo: This function should share a session across requests.
    :param address: The address to query
    :return: The role of the address
    """
    try:
        async with ClientSession(timeout=ClientTimeout(total=0.25)) as session:
            # This uses unencrypted HTTP to set a URL to request
            port = 9255
            request = f"http://{address}:{port}/role"

            # This requests the address for a role response
            async with session.get(request) as response:
                role = await response.text()

                # This checks what role was found
                if "Manager" in role:
                    return address, role

    # This handles other cases, where a response is missing or incorrect
    except (ClientConnectorError, asyncio.TimeoutError):
        return address, None
    else:
        raise RuntimeError("There has been an unknown error.")


async def get_roles_in_network(
    network: IPv4Network,
) -> IPv4AddressesAndRole:
    """
    This function queries available addresses in the network to ask their role.
    This function asynchronously schedules HTTP requests to be sent to each address, and if any
    roles are found, it will be returned from this function.
    :param network: The network space to query
    :return: The roles found in the network
    """
    queries = deque(get_role(host) for host in network.hosts())
    responses = await asyncio.gather(*queries)

    roles: IPv4AddressesAndRole = deque(
        (host, role) for host, role in responses if role
    )

    return roles


def get_manager_from_roles(roles: IPv4AddressesAndRole) -> Optional[IPv4Address]:
    """
    This function loops through a deque of addresses and roles to find if a manager is present.
    :param roles: The deque to loop through
    :return: The manager's address, if found
    """
    managers = [host for host, role in roles if "Manager" in role]

    limit = 1
    if len(managers) > limit:
        raise ValueError("There is more than one manager on the network.")

    elif not managers:
        raise ValueError("There are no managers on the network.")

    return managers[limit - 1]


async def main():
    local_address = get_local_network_address()

    network_prefix_length = get_network_prefix_length_by_address(local_address)

    interface = ip_interface(f"{str(local_address)}/{network_prefix_length}")

    ipv4 = 4
    if interface.network.version != ipv4:
        raise ConnectionError("There was an error finding an IPv4 interface.")

    network = interface.network
    network_roles = await get_roles_in_network(network)

    manager_address = get_manager_from_roles(network_roles)
    print(manager_address)


if __name__ == "__main__":
    asyncio.run(main())
