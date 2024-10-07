# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg

# Create a portal context.
pc = portal.Context()

# Begin building the RSpec.
request = pc.makeRequestRSpec()

# Create the central node (router).
central_node = request.XenVM("central")
central_node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"

# Enable IP forwarding on the central node.
central_node.addService(pg.Execute(shell="/bin/sh", command="sysctl -w net.ipv4.ip_forward=1"))

# Create spoke nodes and links to the central node.
num_spokes = 5
for i in range(1, num_spokes + 1):
    # Create a spoke node.
    node = request.XenVM("node{}".format(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"

    # Add an interface to the spoke node and assign an IP address.
    spoke_iface = node.addInterface("ifc_node{}".format(i))
    spoke_iface.addAddress(pg.IPv4Address("10.0.{}.2".format(i), "255.255.255.0"))

    # Create a unique interface on the central node for this link.
    central_iface = central_node.addInterface("ifc_central{}".format(i))
    central_iface.addAddress(pg.IPv4Address("10.0.{}.1".format(i), "255.255.255.0"))

    # Create a link between the central node and the spoke node.
    link = request.Link("link{}".format(i))
    link.addInterface(central_iface)
    link.addInterface(spoke_iface)
    link.bandwidth = 1000  # Set bandwidth to 1 Gbps

    # Add static routes on the spoke node to reach other spokes via the central router.
    for j in range(1, num_spokes + 1):
        if i != j:
            # Route to subnet 10.0.j.0/24 via the central node's interface.
            node.addService(pg.Execute(
                shell="/bin/sh",
                command="ip route add 10.0.{j}.0/24 via 10.0.{i}.1".format(j=j, i=i)
            ))

# Output the RSpec.
pc.printRequestRSpec()
