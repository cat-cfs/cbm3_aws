import shortuuid


def get_uuid() -> str:
    return shortuuid.uuid()


def get_names(uuid) -> dict[str, str]:
    return dict(
        run_activity=f"cbm3_run_activity_{uuid}",
        autoscale_launch_template=f"cbm3_run_launch_template_{uuid}",
        autoscale_group=f"cbm3_autoscale_group_{uuid}",
        run_task_state_machine=f"cbm3_run_task_state_machine_{uuid}",
        run_state_machine=f"cbm3_run_state_machine_{uuid}",
        state_machine_policy=f"cbm3_state_machine_policy_{uuid}",
        state_machine_role=f"cbm3_state_machine_role_{uuid}",
        instance_s3_policy=f"cbm3_s3_instance_policy_{uuid}",
        instance_iam_role=f"cbm3_iam_instance_role_{uuid}",
    )


def get_step_functions_executions_name(uuid) -> dict[str, str]:
    return dict(
        step_functions_execution=f"cbm3_aws_step_functions_execution_{uuid}"
    )
