### Concepts and Abrreviations

#### General
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
* **Routing algorithm** - The algorithm that routes the packets through the network, chooses the quickest route, makes the choices so that the data gets to the destination with as few deadlocks as possible and in the fastest way possible
* **3D NoC** - NoC Architecture that spans over 3 dimensions. 2D structures on different PCBs are connected through TSVs
* **Elevator algorithm** - algorithm that can be used for connecting 2D NoCs using different deadlock-free algorithms by implementing elevators(vertical channels)!
* **Elevator-first algorithm** - some algorithm in elevator-first routing
* **Virtual Channel(VC)**
* **Wormhole Routed NoC**
* **input-buffered**

#### Traffic Patterns
- **Uniform random**
- **Hotspot random**
- **Tornado**
- **Bit complementary**

#### Traffic Generation (maybe it's the same as a Traffic Pattern)
- **Constant Bit Rate(CBS)**

#### Metrics
- **Average latency** - ns/us time it takes the packet to traverse an average length routed path
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
- **Mesh** - a mesh of routers, each router is connected to 4 routers adjacent to it
  - **by far most common**
- **Ring** - routers connected in a ring, each router is connected to 2 neighbors
- **Butterfly Fat Tree(BFT)**
- **Binary Tree**
- **Torus**

#### Routing Algorithm
- **Deterministic**
- **Backtracking** - algorithm that introduces probing
- **Parallel Probing**

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
