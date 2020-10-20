### Concepts and Abrreviations

#### General
* **NoC** - Network on Chip,
* **MPSoC** - Multi Processor SoC,
* **GALS** - Globally Asynchronous Locally Synchronous,
* **Data Coherency** - Routers know where to take the data from when it was moved or etc.
* **Flit** - Atomic package/packet sent over the network, Large packages to be sent will go as a burst of flits. Typically we have 3 types of Flits: Header, Data & Tail. Each Flit should have its type information inside (HDT - Head-Data-Tail)
  - `Header Flit` - HDT + destination
  - `Data Flit` - HDT + Data
  - `Tail Flit` - HDT + some final information
* **Routing algorithm** - The algorithm that routes the packets through the network, chooses the quickest route, makes the choices so that the data gets to the destination with as few deadlocks as possible and in the fastest way possible
* **3D NoC** - NoC Architecture that spans over 3 dimensions. 2D structures on different PCBs are connected through TSVs
* **Protocol Conversion** - i.e., transforming an IP interface protocol, e.g., AXI, to packet protocol and vice-versa
  - packetization - (from message 2 packet) for transmission
  - depacketization - (from packet to message) for reception
  - flitization - (from packet to flit) according to packet/flit size constraints
  - deflitization - (from flit to packet) according to packet/flit size constraints
* **Message / packet queueing** i.e., buffering is needed for messages/packets to be sent and received due to temporary unavailability of communication or computation resources
* **De / Multiplexing** - in the case of parallel organization of multiple queues
* **OCP-IP** - Protocol Conversion that should happen between the IP and the IIP. For ex. IP can pass the data in the AXI spec and then this would be transferred to a protocol that uses flits in between the IIPs.
* **Multicasting** - in terms of NoCs, multicasting would be equal to sending the same command/data something to a lot of IP's. One packet can be routed through all the nodes that need it delivered. 1packet = N destinations
* **Unicasting** - If node has to send the same packet to N nodes then it has to do so in N separate packets, 1 packet = 1 destination
  - Increases network traffic
  - reduces the complexity of switches
  - If we want the data to be processed in real-time then it could create a problem since each destination node has a different delivery time
---
#### NoC Types
- **CS** - Circuit Switched,
- **PS** - Packet Switched, more common approach
---
#### NoC Phy Elements
- **Switch / IIP** - interconnect part of the NoC node that routes the data.
- **Resource / IP** - the module connected to the NoC node, it can do computation or storage of data or external connection, generates the data that gets routed by IIPs
- **TSV** - Through Silicon Via, High Cost
- **VC** - Virtual Channel, a buffer at the input of the IIP from another IIP that makes it so that we can multiplex the input flits. Some articles have shown that the optimal number of VCs is 4.
- **CDMA IIP** - Code Division Multiple Access switch/IIP, normally poses a problem because it does not support multicasting nor can it be directly connected to a NoC. this switch uses CDMA techniques rather then MUX-based switches.
---
#### NoC Problems
- **Deadlock** - When the packages are stalled in the network because there is no way they can propagate through full buffers or the paths are passing different data already
- **LiveLock** -
---
#### Traffic Patterns (Synthetic)
- **Uniform random** - each node sends packets randomly to other nodes with an equal probability P=1/N (N-number of nodes in the network) [*Eval of Deflection pdf*]
- **Hotspot random**
- **Tornado**
- **Bit Permutation**: Node address is denoted as n bits and the destination address is computed by permuting the bits of the source address [*Eval of Deflection pdf*]
  - **Bit Complement** - di = Complement(Si)
  - **Bit Reverse** - di = Si-1-l
  - **Bit Rotate** - di = si+1 mod n
  - **Transpose** - di = si+n/2 mod n
  - **Shuffle** - di = si-1 mod n
- **CBS** - Constant Bit Rate
---
#### Traffic Regulation
- **Open Loop**
- **Closed loop**
---
#### Metrics
- **Packet latency** - is the sum of Tnet (network delivery time[hop count]) for the packet being routed(1 hop = 1 router passed) and the Tsrc which is the time that the packet spent in the source queue. T = Tnet + Tsrc [*Eval of Deflection pdf*]
- **Average latency** - ns/us time it takes the packet to traverse an average length routed path
- **Throughput** - packets/cycle/node is defined as the saturation point of the network which means that the maximum accepted traffic TP = Total received number of packets / (Number of nodes * Total time) :
  - **Aggregate throughput**
  - **Average throughput** - number of Gb/Mb/packets sent on average across all the routers
- **Dropping Probability** - how many packets were dropped to the number of packets sent by the source
- **Energy consumption per flit**
- **Injection ratio** - Flits/Node/Cycle
- **Number of hops** - number of routers the data has to go through to get to the destination, could be a bit similar to average latency
- **Load** - [%] - how many sources generate packets out of all available sources
- **Packet Size** - size of the packet in **bytes**
---
#### Network Topologies
- **Star** - 1 central router, everything connected to it
  - Max number of Hops = 2
- **Mesh** - 2D/3D Mesh of routers:
  - in a 2D network the routers on edges are connected to less than 4 routers. For the sides its 3 links and for the routers located at the tips/vertexes there are 2 links. This was standardized in the Torus topology so that each Router has 4 links.
  - 3D Network has a similar behavior when it comes to routers on the edges.
  - **by far most common**
  - **medium in most comparisons**
  - Regular 2D mesh - all resources are the same Size
  - Irregular 2D mesh - resources can be of any size.
- **Ring** - routers connected in a ring, each router is connected to 2 neighbors
- **BFT** - Butterfly Fat Tree,
- **Binary Tree**
- **Torus** - k-ary 2-cube with k nodes in each dimension. It's a Mesh Topology with the additional connection between routers at the opposite edges through wrap-around links.
  - has the bigger Throughput for the uniform random, transpose and bit complement traffic compare with Mesh.
-  **Star-Mesh** - Topology combination that enhances throughput by having the resources connected to the Star Toplogoy Switches first. Those Star Switches are then assembled into Mesh Topology.
- **Bus-Mesh** - bus-based connections and global mesh routers
---
#### Routing Algorithm
- **XY / x-first** - simplest algorithm, packet goes along the X axis until the X value is met, after that it starts moving along the Y axis
  - **Properties**:
    - Deadlock-free
    - Deterministic
- **i-route** -
- **Deterministic**
- **Backtracking** - algorithm that introduces probing
- **Parallel Probing**
- **Deadlock-free**
- **Deflection** - divides into 2 parts: [*Eval of Deflection pdf*]
  - *Routing computation* - gets the productive direction to the destination. Incoming packets are prioritized by the hop counts the packet has been routed in the network.
  - *Output Allocation* - Router allocates the output for each packet depending on the priority from highest to lowest. Introduces a load-aware technique which considers the information that it gets from the neighboring routers to balance the network load in the output allocation. Each Router transmits the number of packets in the last 4 cycles as load information to its four neighbors. Router should choose the output as the one with the least traffic.
  - *Characteristics*:
    - No buffers
    - Deadlock-free - packets never have to wait in the router
    - There is a need to prevent livelock by limiting the number of misrouting, this is done by the age-based prioritization of the packets.
- **Wormhole** -
  - *Characteristics*:
    - small buffer size
- **Elevator** - algorithm that can be used for connecting 2D NoCs using different deadlock-free algorithms by implementing elevators(vertical channels)!
- **Elevator-first** - elevator algorithm that prioritizes elevators when traversing the NOC.
---
#### Routing Protocol
- **Shortest Path**
---
#### Queue Mechanism
- **SFQ** - Stochastic Fairness Queueing
---
#### Routing Scheme
- **Static**
---
#### Transmission Protocol
- **UDP** - User Datagram Protocol, the user defines the protocol by himself.
---
#### Analysis
- **Zero Load Analysis**
---
#### Security
- **Hardware Trojan HT**
- **DoS** - Denial of Service, a hacked node sends irrelevant packets through the network causing Deadlocks, increasing network traffic
- **Malignant nodes**
- **Benign nodes**
- **A**
