
def execute_tasks():
    step_functions.start_execution(
        client=sfn_client, name=names.step_functions_execution,
        state_machine_context=state_machine_context, tasks=tasks)