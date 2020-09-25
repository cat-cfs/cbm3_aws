from types import SimpleNamespace
import shortuuid


def get_names(id):
    uuid = shortuuid.uuid()
    return SimpleNamespace(
        run_activity=f"cbm3_run_activity_{uuid}",
        autoscale_launch_template=f"cbm3_run_launch_template_{uuid}",
        autoscale_group=f"cbm3_autoscale_group_{uuid}",
        run_task_state_machine=f"cbm3_run_task_state_machine_{uuid}",
        run_state_machine=f"cbm3_run_state_machine_{uuid}",
        step_functions_execution=f"cbm3_aws_step_functions_execution_{uuid}")
