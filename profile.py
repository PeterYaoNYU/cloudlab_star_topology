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

# Assign IP address to the central node.
central_iface = central_node.addInterface("ifc_central")
central_iface.addAddress(pg.IPv4Address("10.0.0.100", "255.255.255.0"))

# Enable IP forwarding on the central node.
central_node.addService(pg.Execute(shell="/bin/sh", command="sysctl -w net.ipv4.ip_forward=1"))

# Create spoke nodes and links to the central node.
num_spokes = 5
for i in range(1, num_spokes + 1):
    # Create a spoke node.
    node = request.XenVM("node{}".format(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD"
    
    # Add an interface to the spoke node and assign an IP address.
    iface = node.addInterface("ifc_node{}".format(i))
    iface.addAddress(pg.IPv4Address("10.0.0.{}".format(i), "255.255.255.0"))
    
    # Create a link between the central node and the spoke node.
    link = request.Link("link{}".format(i))
    link.addInterface(central_iface)
    link.addInterface(iface)
    link.bandwidth = 1000  # Set bandwidth to 1 Gbps
    
    # Enable IP forwarding on the spoke node.
    node.addService(pg.Execute(shell="/bin/sh", command="sysctl -w net.ipv4.ip_forward=1"))
    
    # Add static route on the spoke node to reach other spoke nodes via the central router.
    for j in range(1, num_spokes + 1):
        if i != j:
            node.addService(pg.Execute(shell="/bin/sh", command="ip route add 10.0.0.{} via 10.0.0.100".format(j)))

# Output the RSpec.
pc.printRequestRSpec()