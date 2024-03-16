# StateRW class

StateRW is a class to help stateful functions to access state data stored in DesFaaS.

Here is an example of page visit conter application to use StateRW to connect with DesFaaS about OpenFaaS stateful functions.

<code>

    import os

    from .state_RW.state import StateRW

    def handle(req):
        function_name = os.getenv("function_name")

        # Initial the StateRW class
        state = StateRW(function_name)
        
        # Read state data
        count = state.state_read()
        
        # Update state data
        count += 1

        # Write state data
        state.state_write(count)

        # Function return value
        return count
</code>