# DesFaaS
DesFaaS is a cross-Level joint dynamic deployment system for serverless stateful functions.

For function migration, we realize a user-independent automated function migration process, support synchronous and asynchronous migration mechanisms of function instances under heterogeneous migration media, and support efficient and low-consumption migration of serverless stateful functions.

For state access, we realize a user-independent automated state data scheduling process, supports master-slave state consistency and state lifecycle management under distributed storage, and supports flexible and efficient access to state data of serverless functions.

Based on the function migration and state access components, we design DesFaaS to support dynamic deployment of location-variable stateful functions. Combining the proposed function migration and state scheduling strategies, we achieve the autonomous and reliable operation of serverless stateful function clusters.

# Deploy DesFaaS to manage your stateful serverless functions.

You could refer to the following document for actual DesFaaS deployment.

[deployment.md](https://github.com/WhaleSpring/DesFaaS/docs/deployment.md)

# Access state data in OpenFaaS stateful functions

You could use StateRW class we provide to access state data of DesFaaS, contruct http requests directly to access state data of stateful functions.

Here is the doc of StateRW class:

[StateRW.md](https://github.com/WhaleSpring/DesFaaS/docs/StateRW.md)