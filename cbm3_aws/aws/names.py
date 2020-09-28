from cbm3_aws.namespace import Namespace
import shortuuid


def get_uuid():
    return shortuuid.uuid()


def get_names(uuid):
    return Namespace(
        run_activity=f"cbm3_run_activity_{uuid}",
        autoscale_launch_template=f"cbm3_run_launch_template_{uuid}",
        autoscale_group=f"cbm3_autoscale_group_{uuid}",
        run_task_state_machine=f"cbm3_run_task_state_machine_{uuid}",
        run_state_machine=f"cbm3_run_state_machine_{uuid}")


def get_step_functions_executions_name(uuid):
    return Namespace(
        step_functions_execution=f"cbm3_aws_step_functions_execution_{uuid}")
