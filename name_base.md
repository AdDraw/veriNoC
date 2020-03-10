### Concepts and Abrreviations

#### General
* **MPSoC** - Multi Processor SoC
* **GALS** - Globally Asynchronous, Locally Synchronous
* **Data Coherency** - ??? Routers know where to take the data from when it was moved or etc.
* **Network on Chip(NoC)**
  - Circuit Switched(CS)
  - Packet Switched(PS)
    - more common
* **TSV** - Through Silicon Via
  - High cost
* **Flit** - Atomic package/packet sent over the network, Large packages to be sent will go as a burst of flits
* **Deadlock** - When the packages are stalled in the network because there is no way they can propagate through full buffers or the paths are passing different data already
* **LiveLock** -
* **Routing algorithm** - The algorithm that routes the packets through the network, chooses the quickest route, makes the choices so that the data gets to the destination with as few deadlocks as possible and in the fastest way possible
* **3D NoC** - NoC Architecture that spans over 3 dimensions. 2D structures on different PCBs are connected through TSVs
* **Elevator algorithm** - algorithm that can be used for connecting 2D NoCs using different deadlock-free algorithms by implementing elevators(vertical channels)!
* **Elevator-first algorithm** - some algorithm in elevator-first routing
* **Virtual Channel(VC)**
* **Wormhole Routed NoC**
* **input-buffered**

#### Traffic Patterns (Synth)
- **Uniform random** - each node sends packets randomly to other nodes with an equal probability P=1/N (N-number of nodes in the network) [*Eval of Deflection pdf*]
- **Hotspot random**
- **Tornado**
- **Bit Permutation**: Node address is denoted as n bits and the destination address is computed by permuting the bits of the source address [*Eval of Deflection pdf*]
  - **Bit Complement** - di = Complement(Si)
  - **Bit Reverse** - di = Si-1-l
  - **Bit Rotate** - di = si+1 mod n
  - **Transpose** - di = si+n/2 mod n
  - **Shuffle** - di = si-1 mod n

#### Traffic Generation (maybe it's the same as a Traffic Pattern)
- **Constant Bit Rate(CBS)**

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

#### Network Topologies
- **Star** - 1 central router, everything connected to it
  - Max number of Hops = 2
- **Mesh** - 2D/3D Mesh of routers:
  - in a 2D network the routers on edges are connected to less than 4 routers. For the sides its 3 links and for the routers located at the tips/vertexes there are 2 links. This was standardized in the Torus topology so that each Router has 4 links.
  - 3D Network has a similar behavior when it comes to routers on the edges.
  - **by far most common**
  - **medium in most comparisons**
- **Ring** - routers connected in a ring, each router is connected to 2 neighbors
- **Butterfly Fat Tree(BFT)**
- **Binary Tree**
- **Torus** - k-ary 2-cube with k nodes in each dimension. It's a Mesh Topology with the additional connection between routers at the opposite edges through wrap-around links.
  - has the bigger Throughput for the uniform random, transpose and bit complement traffic compare with Mesh.

#### Routing Algorithm
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


#### Routing Protocol
- **Shortest Path**

#### Queue Mechanism
- **Stochastic Fairness Queueing(SFQ)**

#### Routing Scheme
- **Static**

#### Transmission Protocol
- **User Datagram Protocol(UDP)**

#### Analysis
- **Zero Load Analysis**
