import salt.utils.platform
from collections import OrderedDict

try:
    import wmi  # pylint: disable=import-error
    import salt.utils.winapi
    HAS_DEPENDENCIES = True
except ImportError:
    HAS_DEPENDENCIES = False

# Define the module's virtual name
__virtualname__ = "netbios"

TcpipNetbiosOptions = OrderedDict(
    default=0,
    enabled=1,
    disabled=2
)

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
                    "NetBIOS": list(TcpipNetbiosOptions.keys())[config.TcpipNetbiosOptions]
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

        if setting not in TcpipNetbiosOptions.keys():
            return False

        for config in c.Win32_NetworkAdapterConfiguration(IPEnabled=True):
            return_code = config.SetTcpipNetbios(TcpipNetbiosOptions[setting])[0]

            if return_code == 0:
                result = "Success. Set NetBIOS to {0}.".format(setting)
            elif return_code == 1:
                result = "Success. Set NetBIOS to {0}. Reboot required."
                __salt__["system.set_reboot_required_witnessed"]()
            elif return_code == 100:
                result = "DHCP not enabled. Cannot set to default."
            else:
                result = "Error setting NetBIOS to {0}. Error code: {1}".format(setting, return_code)

            current = {
                config.Description: {
                    "Index": config.Index,
                    "Result": result
                }
            }

            ret.append(current)

    return ret
