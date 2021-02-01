import salt.utils.platform

try:
    import wmi  # pylint: disable=import-error
    import salt.utils.winapi
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

# Define the module's virtual name
__virtualname__ = "netbios"

TcpipNetbiosOptions = [
    "default",
    "enabled",
    "disabled"
]

def __virtual__():
    """
    Only works on Windows systems
    """
    if not salt.utils.platform.is_windows():
        return False, "Module win_network: Only available on Windows"

    if not HAS_DEPENDENCIES:
        return False, "Module win_network: Missing dependencies"

    return __virtualname__

def get(interface=None):
    """
    Enables NetBIOS Option on network interfaces

    CLI Example:

    Get NetBIOS setting on ALL interfaces.

    .. code-block:: bash

        salt '*' netbios.get

    Get NetBIOS Option on a specific interface

    .. code-block:: bash

        salt '*' netbios.get Ethernet0 
    """

    ret = []

    with salt.utils.winapi.Com():
        c = wmi.WMI()
        for config in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            current = {
                config.Description: {
                    "Index": config.Index,
                    "NetBIOS": TcpipNetbiosOptions[config.TcpipNetbiosOptions]
                }
            }
            ret.append(current)

    return ret

def set(setting, interface=None):
    """
    Enables NetBIOS Option on network interfaces

    CLI Example:

    Enable NetBIOS on ALL interfaces.

    .. code-block:: bash

        salt '*' netbios.set enabled

    Disable NetBIOS on a specific interface

    .. code-block:: bash

        salt '*' netbios.set disabled Ethernet0 
    
    Sets NetBIOS to Default on specified adapter

    .. code-block:: bash

        salt '*' netbios.set default Ethernet0
    """

    ret = []
    with salt.utils.winapi.Com():
        c = wmi.WMI()
        for iface in c.Win32_NetworkAdapter(NetEnabled=True):
            ret.append(iface.NetConnectionID)
    return ret

