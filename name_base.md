### Concepts and Abrreviations

#### General

* **NoC** - Network on Chip
* **TSV** - Through Silicon Via
  - High cost
* **Flit** - Part of a package that we need to send through the network
* **Deadlock** - When the packages are stalled in the network because there is no way they can propagate through full buffers or the paths are passing different data already
* **Routing algorithm** - The algorithm that routes the packets through the network, chooses the quickest route, makes the choices so that the data gets to the destination with as few deadlocks as possible and in the fastest way possible
* **3D NoC** - NoC Architecture that spans over 3 dimensions. 2D structures on different PCBs are connected through TSVs
* **Elevator algorithm** - algorithm that can be used for connecting 2D NoCs using different deadlock-free algorithms by implementing elevators(vertical channels)!
* **Elevator-first algorithm** - some algorithmIn elevator-first routing

#### Traffic Patterns
- **Uniform random**
- **Hotspot random**
- **Tornado**
- **Bit complementary**

#### Metrics
- **Average latency**
- **Aggregate throughput**
- **Energy consumption per flit**
- **injection ratio** - Flits/Node/Cycle
