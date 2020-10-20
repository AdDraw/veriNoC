### Physical Part of the NoC (PHY)


#### 1st case, simple MESH NOC with XY routing algorithm

XY routing: Simply goes First to X pos vertically
When it gets to X pos it then descends or ascends to Y pos.

Packet: Could be [Xpos, Ypos, Data]
- This would be an atomic Packet, meaning that it does not consist of multiple data transfers
- 1 clock cycle = 1 packet

Routing:
1. if the switch knows it's position then -> if Internal_X_pos < or > then move left or right this better :)
2. If it does not -> then in the address Xpos would be equal to number of hops the packet wants to perform, then each Switch would decrease the hop count
   Eventually X_hop_n=0 and Y_hop_n=0 would mean that the packet arrived at the pos it wants to be at :)


- Switch Assumptions
  - we don't want to lose data in case of deadlock, we want to put incoming ones in FIFOs that move when it's possible
  - we want to implement some priority handling -> this could be done by hop counting (each node increments the hop count to increase priority)
  - we don't want to perform multiple cycle packets, only atomic ones
  - data coming from the resource has the lowest priority and is also kept in the input FIFO until there is a cycle with no incoming data packets

- Simple Arch v0.1:
  - Semi Deep (N packets, could be defined) FIFOs on each input, not on output(if the next switch can process the packet it can, if not it will be halted in this Switches input FIFO)
  - Inside simple comparison FIFO for the priority and position checking
  - Resource FIFO with lowest priority (since it has 0 hops)

- What we need?:
  - [] a modifiable FIFO module with Read and Write pointers, this will make initial processing faster
  - [] a Routing Module
  - [] Reg with Xpos and Ypos of the switch
  - [] Packet decomposition
  - [] Hop count incrementer

- Resource
  - Simulated
  - We go with simplest Packet generation
