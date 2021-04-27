### Concepts and Abrreviations

#### General
- **MPSoC** - Multi Processor SoC
- **GALS** - Globally Asynchronous Locally Synchronous,
- **Data Coherency** - Routers know where to take the data from when it was moved or etc.
- **3D NoC** - NoC Architecture that spans over 3 dimensions. 2D structures on different PCBs are connected through TSVs
- **Protocol Conversion** - i.e., transforming an IP interface protocol, e.g., AXI, to packet protocol and vice-versa
  - packetization - (from message 2 packet) for transmission
  - depacketization - (from packet to message) for reception
  - flitization - (from packet to flit) according to packet/flit size constraints
  - deflitization - (from flit to packet) according to packet/flit size constraints
- **Message / packet queueing** i.e., buffering is needed for messages/packets to be sent and received due to temporary unavailability of communication or computation resources
- **De / Multiplexing** - in the case of parallel organization of multiple queues
- **OCP-IP** - Protocol Conversion that should happen between the IP and the IIP. For ex. IP can pass the data in the AXI spec and then this would be transferred to a protocol that uses flits in between the IIPs.
- **Multicasting** - in terms of NoCs, multicasting would be equal to sending the same command/data something to a lot of IP's. One packet can be routed through all the nodes that need it delivered. 1packet = N destinations
- **Unicasting** - If node has to send the same packet to N nodes then it has to do so in N separate packets, 1 packet = 1 destination
  - Increases network traffic
  - reduces the complexity of switches
  - If we want the data to be processed in real-time then it could create a problem since each destination node has a different delivery time
- **Hop** - a `single` jump between closest to each other nodes
- **IP** - Intellectual Property
- **IIP** - Interconnect Intellectual Property
---
## **Network on Chip**
Network on Chip(`NoC`), Interconnect Network that connects multiple modules
- replacement of `BUSES & CROSSBARs` for `Switches & Resources (Terminals and Nodes)`

> The network on chip is a router-based packet switching network between SoC modules.(wikipedia)

> NoC technology applies the theory and methods of computer networking to on-chip communication and brings notable improvements over conventional bus and crossbar communication architectures.(wikipedia)

Previous to NoC approach on the chip IPs were connected in th Soc manner, through a BUS, this had it's disadvantages like `single channel global interconnection, low bandwidth, high latency, power consumption and poor scalability`.


**self-throttling network** - with more congestion the time to send/receive the data increases (in the processor <-> memory scenario)

**Network Load** - describes how often resource is being utilized (if a single Resource is over-utilized while other are under-utilized it leads to load imbalance )\

**Total Input bandwidth** - bits/s that the network can take from all of the network inputs\
**Network ideal capacity** - when every channel inside the network has it's bandwidth used entirely, to achieve a fraction of it is required to have a good combination of Flow Control, Routing Algorithm & the topology for a given traffic\
**Network Speedup** - ratio between total input bandwidth and ideal network capacity, it is best to have speedup > 1. Having speedup > 1 means that the network in it's ideal state can take N times the input bandwidth provided by the Terminals/Source Nodes

**Direct Network** - each node is also a terminal
**Indirect Network** - some nodes only pass the packets and don't generate them
> Some networks might not pass into Direct/Indirect category

**Network Locality** - how local is your traffic, traffic is local when source and destination nodes are close to each other, there might be local sections that mostly send the data between themselves and on some rare occasion send the data to a far off node

---
## Unit of information in NoCs
- **Message** - unit of transfer from client to the network  -> it can generate 1 or more packets
- **Packet** - unit of transfer that the message is divided into, recognized in the packet-based Flow Control, might consist of flits
- **Flit** - smallest unit of information in the network, recognized in the flit-based Flow Control. Atomic package/packet sent over the network, Large packages to be sent will go as a burst of flits.
  - has it's `TYPE` inside and other information depending on the type
  - **Flit Types**
    - `HEADER` (at the start and stores the information about the destination and some other info, while traversing the network is allocates resources for the following flits)
    - `BODY/PAYLOAD` (stores data, can be 0 or more of them)
    - `TAIL` (at the end of the packet, it deallocates resources allocated by the header flit)
    - [opt] `NULL` ( can be 0 or more of them, doesn't store any productive data)
---
## Packet Switched NoC
Each packet holds the information required to decide how it should be routed in the network
At each node the packet is processed and routed to an output. That is true even for packets that travel the same route.
- `according to Analysis and evaluation of circuit switched NoC and packet switched NoC by Shaoteng Liu et al.`
  - when Packet size increases performance drops
  - compared to CS it can achieve a lower max frequency

---
## Circuit Switched NoC
connections are first setup and are held as data flows through without an interference

#### Types:
- **Non-Blocking** - can handle all circuit requests that are a permutation of sources and destinations, a dedicated path can be formed between source and destination
- **Strictly Non-Blocking** - if a new path can be setup without rearranging current paths
- **Rearrangeably non-blocking** - when you need to rearrange already existing paths to setup a new path

`according to Analysis and evaluation of circuit switched NoC and packet switched NoC by Shaoteng Liu et al.`
  - has longer setup time
  - guaranteed throughput & latency
  - can achieve a higher than PS clock frequency
  - has higher energy efficiency
  - with increased packet size performance also increases
  - might be better for some NoC applications (dependent on the traffic patters & requirements)

> An Example of a CS NoC can be a CROSSBAR n x m Network. It has directions between sources and destinations with no intermediate stages. Each node consists of m n:1 crossbars / one for each output

> Clos network has everything connected to everything but with stages (butterfly topology)

---
## NoC Phy Elements
- **Switch / Node / IIP** - interconnect part of the NoC node that routes the data.
- **Resource / Source Node / Terminal / IP** - the module connected to the NoC node, it can do computation or storage of data or external connection, generates the data that gets routed by IIPs
- **TSV** - Through Silicon Via, High Cost
- **VC** - Virtual Channel, a buffer at the input of the IIP from another IIP that makes it so that we can multiplex the input flits. Some articles have shown that the optimal number of VCs is 4.
- **CDMA IIP** - Code Division Multiple Access switch/IIP, normally poses a problem because it does not support multicasting nor can it be directly connected to a NoC. this switch uses CDMA techniques rather then MUX-based switches.
---
## NoC Problems
#### **Deadlock**
When the packages are stalled in the network because there is no way they can propagate through full buffers or the paths are passing different data already.
Or when packets wait on each other to release resources.

Scenario in which packets in a specific cycle wait for each other to release resources and by doing so both packets are blocked indefinitely.

Such congestion might spread to a whole network because it cuts of possible routes for packets to travel and with deterministic routing algorithms those packets can't choose a different path.

**to avoid/prevent:**
- **deadlock avoidance** - methods that prevent deadlock entirely
- **deadlock recovery** - methods that detect & correct deadlocks inside the network

> Good way to prevent deadlocks from happening is to implement packet & resource priority, for example HOP Counts(packet that has been in the network longer has more priority) and also by implementing some form of static input priority (input left has more priority when it wants to allocate a resource than input right)


- depends on the Flow Control chosen

##### Types of deadlock
| FC |  Agent | Resource | Cordiality |
| --- | --- | --- | --- |
| CS | Connection | Physical Channel | Multiple |
| Packet-based | Packet | Packet Buffer | Single |
| Flit-based | Packet | Virtual Channel| Multiple |

#### **LiveLock**
When the package is routed in the Network `indefinitely` through misroutes

- might appear when non-minimal routing is possible
- **to prevent**
  - allow only N misroutes( after that packet should be routed on a minimal path or is dropped)

---
## Traffic Patterns
describe how messages are distributed from each source to each possible destination

#### Types
- **Random** - each source node sends packets/messages to destination nodes with some probability
  - **Uniform random** - each node sends packets randomly to other nodes with an equal probability P=1/N (N-number of nodes in the network) [*Eval of Deflection pdf*]
  - **Hotspot random**
- **Permuatation** - maps source onto destination, performs stress tests on the network
  - **Bit Permutation**: Node address is denoted as n bits and the destination address is computed by permuting the bits of the source address [*Eval of Deflection pdf*]
    - **Bit Complement** - `di = Complement(Si)`
    - **Bit Reverse/Reversal** - `di = Si-1-l`, source 0 sends the data to dest N-1 and the other way around
    - **Bit Rotate** - `di = si+1 mod n`
  - **Digit Permutation** - each radix-k digit of the destination address `d` is a function of some source digit (only apply to k-ary n-fly / k-ary n-cube topologies)
    - **Tornado** - `d = sx + ([k/2]-1) mod k` (designed for `Torus`)
    - **Neighbor** - `d = sx + 1 mod k`
- **Transpose** - `di = si+n/2 mod n`
- **Shuffle** - `di = si-1 mod n`

> for example FFT is an example of SHUFFLE Type

> Bad Topologies look better with Random Traffic because it improves load balance

> To stress the topology it's good to use  PERMUTATION traffic, because then each source send it's packets to a single destination every time -> which might test load imbalance

> k-ary n-fly = Butterfly k-ary n-cube Torus

---
#### Quality of Service (QoS)
fair allocation of resources under some service policy
rules that dictate how many packets can be dropped, what should be the throughput etc
- **Reliability** - how often the packet should be properly routed (most cases 100%)
- **Availability** -

---
## Network Performance Metrics
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
## Network Cost Metrics
- average/peak energy/power consumption
- network area overhead
- total area
- average/peak temperature
---
## Topology
static assignment of channels and nodes in an interconnect network\
defines how Resources & Switches are connected\
arrangement of switches & resources
### Specifies
- type of connections (mesh, torus, ring)
- radix of a switch (`TODO: what does switch radix mean ?`)
- number of stages (0, 1, 2)
- width and bit-rate of a channel

### Performance based on Topology
- **Bandwidth / Throughput** - data rate in bits/s that network accepts per input port
  - depends on Routing and Flow Control
  - *Ideal*
    - no idle cycles on bottleneck channels
    - perfect load balance as a result of routing
  - maximum throughput occurs with `channel saturation` (if channels are not saturated then maximum throughput was not obtained)
- **Latency** - time it takes a packet to traverse the network (arrive at the destination)
  - `head latency` - time it takes for the header flit to arrive at the destination
  - `serialization latency` - time required for the tail to catch up, time for the packet of length L to cross a channel with limited bandwidth
  - with no contention
- **Path diversity** - defines the number of paths packet can take to traverse the network
  - topology with multiple minimal paths for the packet to choose is more `robust`
  - adds to robustness by balancing load across channels and allowing the network to tolerate faulty channels and nodes
  - to balance load it is sometimes required to place packets onto non-minimal paths (not possible in some routing algorithms)

> when `non-minimal` routing is used there is a risk of a deadloacks and livelocks! It is neccessary to implement some preventing/restoring functionality from the state of a lock

> Usually it's better to use a general topology in favor of an application specific one because there is a possibility that traffic changes. In that case irregular/specific topology has a high chance of having load imbalance.

### Consists of:
- **Channels (C)** - connect nodes / carry packets/flits from node to node
  - **channel width** - number of signals it has (bit width)
  - **channel frequency** - rate of transferring bits on each signal
  - **channel latency** - time required for a bit to travel the channel
  - **channel bandwidth** - [bits/s] how many bits per second a node can send through it (width * freq)
- **Routers** - that route the data flowing from input channels to output channels

### Types
- **Star** - 1 central router, everything connected to it
  - Max number of Hops = 2
  - high load on the central node prone to being a bottleneck
  - if the central node breaks then whole network stops working
- **Mesh** - 2D/3D Mesh of routers:
  - nodes are connected to each other (nodes on the edges/sides have less conections)
  - good scalability & path diversity
  - increase of nodes makes a very big diameter
  - bandwidth will differ node to node
  - Regular 2D mesh - all resources are the same Size
  - Irregular 2D mesh - resources can be of any size.
- **Ring** - routers connected in a ring, each router is connected to `2` neighbors
  - with more nodes in this topology is the increase of diameter which degrades performance
  - single break in the ring breakdowns the entire network (it could still work but with tiny loads[1 packet at a time/ only non-blocking transactions])
- **Tree Topologies**
  - **Fat Tree**
    - intermediate routers work as forwarding routers
    - leave routers are connected to clients/terminals
    - some path diversity available
    - high router / client ratio
  - **Butterfly**
    - lack of path diversity (only single path available for any A -> B)
    - long network diameter that consumes more energy
  - **Binary Tree**
- **Torus**
  - k-ary 2-cube with k nodes in each dimension. It's a Mesh Topology with the additional connection between routers at the opposite edges through wrap-around links.
  - has the bigger Throughput for the uniform random, transpose and bit complement traffic compared with Mesh.
  - long wires that connect side/edge nodes limit the highest frequency of the network
-  **Star-Mesh** - Topology combination that enhances throughput by having the resources connected to the Star Toplogoy Switches first. Those Star Switches are then assembled into Mesh Topology.
- **Bus-Mesh** - bus-based connections and global mesh routers
---
## Routing
way to choose a path from A to B\
determines wchich path should be taken by the packet out of possible ones
- depends on the topology
- determines how the ideal performance is realised

#### Good Algorithm
- has load balancing in case traffic is not uniform
- chooses shortest paths possible

> Most of the time to increase load balance for oblivious routing algorithms you need to implement non-minimalistic routing which in turn make the paths longer

**Minimal Routing** - packets have to choose the shortest path every time

**Non-Minimal Routing** - packets don't have to choose a shortest path every time

#### Routing algorithms categories based on
- **How a Path is choosen**
  - **Deterministic** - always chooses the same path from A -> B,
    - ignores path diversity even if there are multiple minimal paths, which increases load imbalance
    - cheap & easy to implement
    - are `oblivious`
    - good for irregular topologies (because a good adaptive random algorithm is more difficult to implement for irregular topos)
    - load imbalance that is imposes onto the network might be great for particular traffic patterns
    - subject to low bandwidth because it might put a heavy load on some channels in the network (local load imbalance)
  - **Oblivious** - choose a route without considering the present state of the network
    - simple & cheap to implement
    - main trade-off between locality vs load imbalance\
      (packets might not choose a shortest path even for nodes that are only 1 hop apart)
  - **Adaptive** - chooses a route with knowledge about the state of the network, they adapt to the state of the network
    - for this to work switch/node needs to have knowledge about surrounding nodes
    - Flow Control is knit tightly with Adaptive Routing
    - good adaptive routing should outperform oblivious routing because it has a higher cost of implementation (more info is sent across the network, needs to implement more avoidance/prevention/correction for dead & livelocks, etc)
    - practical adaptive routing might lead to local load balance but global load imbalance, because routing decisions are based on local information
    - there might be a problem with slow adaptation to traffic changes when there is a big delay and adjacent nodes don't get back the congestion information fast enough (`backpressure`)
    - for rapid adaptation and quick response it might be preferred to have short ques (short buffers) because the congestion information travels faster through the network
    - **information that can be used:**
      - `local/global` state
      - `current/historical` information (last N cycles)
    - `stiff` flow control "should" be better with adaptive routing
    - `minimal adaptive routing` good at local load balancing but bad at global load balancing
    - `non-minimal adaptive / Fully Adaptive routing`
      - hard to achieve GLOBAL LOAD IMBALANCE
      - might lead to `livelock`*(it might happen when a packet is misrouted 50% of the time)*
- **When routing is performed**
  - **all-at-once** - packet path is determined at the source node, there might be a lot of paths but 1 is chosen and it is encoded into the packet which in turns results in an overhead
  - **incremental** - there are multiple paths that a packet can take, then on each hop per packet the path is reevaluated. This cannot be done with every routing algorithm that is available with all-at-once routing

**Backpressure** - propagates backwards, carries information that a congestion happened at the current node, can be used to sense congestion if queues on a node are filled it might mean that there is congestion further down in the node. Provide info about Availability of buffers to downstream nodes.


>Typically in adaptive routing until there is congestion packets are routed through minimal paths. When a congestion is detected packets might be routed through an `unproductive` channel (aka `misrouting`)

**misrouting** - to send a packet through a channel that doesn't progress the packet to the destination

> to prevent livelock you need to implement measures that guarantee PROGRESS over time (ex. allow N misroutes(after N do minimal routing), allow 1/N hops to be a misroute)

> Hybrid Routing - do adaptive routing in a section of a network and then in smaller sections do deterministic/oblivious routing

#### Algorithms
- **Dimension-Order / XY(2D) / x-first**
  - simplest algorithm, packet goes along the 1 dimension this dimension value is met, after that it starts moving along the second then third dimension
  - Deadlock-free
  - Deterministic
  - Minimal
- **Destination-tag routing**
  - (used for Butterfly Topology) bits of the destination address is used to select an output port of each switch, bit 0 is used for switch at level 0 and bit 1 is used for the next switch
- **i-route** -
- **Backtracking** - algorithm that introduces probing
- **Parallel Probing**
- **Deflection** - divides into 2 parts: [*Eval of Deflection pdf*]
  - *Routing computation* - gets the productive direction to the destination. Incoming packets are prioritized by the hop counts the packet has been routed in the network.
  - *Output Allocation* - Router allocates the output for each packet depending on the priority from highest to lowest. Introduces a load-aware technique which considers the information that it gets from the neighboring routers to balance the network load in the output allocation. Each Router transmits the number of packets in the last 4 cycles as load information to its four neighbors. Router should choose the output as the one with the least traffic.
  - *Characteristics*:
    - does not drop but misroutes (deflects) packets when resources are contented by 2 or more packets
    - fully adaptive routing algorithm
    - requires same number of inputs and outputs
    - No buffers (area cost is much lower)
    - Deadlock-free - packets never have to wait in the router
    - There is a need to prevent livelock by limiting the number of misrouting, this is done by the age-based prioritization of the packets.
- **Elevator-first** - elevator algorithm that prioritizes elevators when traversing the NOC, algorithm that can be used for connecting 2D NoCs using different deadlock-free algorithms by implementing elevators(vertical channels)!, this is done this way because of a high cost of TSV, you have limited Elevators(that allow traversing between Z dimension)
---
## Flow Control
dictates which messages get access to particular network resources over time\
manages the allocation of resources to packets as they progress along their route\
determines how network's resources (channels, bandwidth, buffer capacity, etc) are allocated to packets traversing the network

- must minimize the channel idleness
- should be fair
- should prevent/avoid deadlock

#### Good Flow Control
- allocates resources efficiently
- achieves a high fraction of an ideal performances
- delivers packets with a low latency

**Buffer** - storage in the node that allows packets to be held temporarily at the node

**Packet Dropping** - situation when a packet can't get resources and is dropped from the network (it is not properly routed to the destination)


#### Types
- **bufferless** - packets that would have to wait for resources are dropped or misrouted
  - flow control has no buffering and acts as a channel allocation for competing packets
  - competing packets need an arbiter that will choose which packet has more priority
- **buffered** - packets wait for resources in buffers for their time to use the resources
  - it drastically increases performance (no drops, no misroutes)
  - **Packet-based** - packet is the unit of information that is buffered
    - channel bandwidth & buffers are allocated for a packet
    - **Store & Forward**
      - each node along the route waits until a packet from a previous node has been full received before forwarding it
      - requires allocation of a buffer at a forward node -> exclusive use of the forward channel
      - if requirements are not met it waits until they are without blocking an output channel
      - has very high latency (serialization latency is experienced at each hop)
    - **Cut-Through**
      - less latency (vs Store&Forward) because it doesn't wait for the whole packet to be received before it starts forwarding(sends it as soon as header is present)
      - sends packets forward as soon as header is received and resources are allocated
      - SHORTCOMINGS:
        - allocation in packets (inefficient use of buffer storage)
        - contention latency is increased(high priority packet has to wait for a low priority packet resource de-allocation to be forwarded)
  - **Flit-based** - flit is the unit of information that is buffered
    - reduces node/router storage required for correct operation (because you don't need to store full packets)
    - provides stiffer back-pressure
    - more efficient use of storage
    - **Wormhole**
      - similar to Cut-Through but with resource allocation for flits and not packets
      - when a header flit arrives at the a node it must acquire resources before it can be forwarded through a channel (virtual channel)
      - body flits of a packet use the virtual channel acquired by the head flit and require only 1 flit bandwidth and 1 flit buffer to advance.
      - tail flit acts like a body flit but it also releases a virtual channel as it passes
      - uses storage/buffer space more efficiently than CUT-THROUGH
      - `Blocking` might occur with wormhole FC because the channel is owned by a packet, but buffers are allocated on a flit-by-flit basis.
      - bandwidth of a channel can only be used by flits from a single packet
    - **Virtual Channgel (VC)**
      - associates multiple Virtual Channels with one Physical channel
      - overcomes the problem of `BLOCKING` in Wormhole FC
      - should have a higher throughput than Wormhole
      - when 2 packets try to access the same output channel there is a need to differentiate them in the output channel (to properly place them into virtual channels of a forward node) and that can be done through interleaving
      - if you have 2 virtual channels that want to allocate an output channel you can only provide half the bandwidth to each (with fair arbitration) and that means that inputs that are appearing at full bandwidth will have input buffers filled faster then they are drained resulting in a congestion, it also means that on the output of the forward node you have half of the cycles idle(half rate), this can be used by different packets since the channel is not blocked half the time.
      - interleaving as `fair arbitration` results in a higher average latency than `winner-takes-all`
      - `unfair arbitration` reduces the average latency of virtual channels and has flow control with no throughput latency
      - Virtual channels allow packets to pass blocked packets(used to avoid deadlock)
      - VCs can also be used to assign priority or to classify/separate traffic


> Buffering decouples allocation of adjacent channels in time

> to send the packet over to the forward node you need to be sure that it has the resources available to process the packet. That's why you need to allocate those resources in advance to traverse the network

> Virtual channels hold the state needed to coordinate the handling of the flits of a packet over a channel (at a minimum it should store the state [Waiting for resource, IDLE, active])

---
#### Queue Mechanism
- **SFQ** - Stochastic Fairness Queueing
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
