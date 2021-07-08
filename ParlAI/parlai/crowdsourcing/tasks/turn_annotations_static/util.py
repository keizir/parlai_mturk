#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import random
import json

from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from omegaconf import DictConfig, OmegaConf

from parlai.crowdsourcing.utils.frontend import build_task
from parlai.crowdsourcing.utils.mturk import soft_block_mturk_workers

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

def run_static_task(cfg: DictConfig, task_directory: str):
    """
    Run static task, given configuration.
    """

    db, cfg = load_db_and_process_config(cfg)
    # print(f'\nHydra config:\n{OmegaConf.to_yaml(cfg)}')

    random.seed(42)

    task_name = cfg.mephisto.task.get('task_name', 'turn_annotations_static')
    soft_block_qual_name = cfg.mephisto.blueprint.get(
        'block_qualification', f'{task_name}_block'
    )
    # Default to a task-specific name to avoid soft-block collisions
    soft_block_mturk_workers(cfg=cfg, db=db, soft_block_qual_name=soft_block_qual_name)

    build_task(task_directory)

    operator = Operator(db)

    if cfg.multiple_tasks:
        units = mephisto_data_browser.get_units_for_task_name("turn-taking-chat")
        units = [u for u in units if u.get_status() == "accepted"]
        for unit in units:
            data = mephisto_data_browser.get_data_from_unit(unit)
            messages = data["data"]["messages"]
            chat_data = {
                "dialog": [[messages[i], messages[i+1]] for i in range(int(len(messages)/2))]
            }
            cfg.mephisto.task.chat_data = json.dumps(chat_data)
            cfg.mephisto.blueprint.database = True
            operator.validate_and_run_config(run_config=cfg.mephisto, shared_state=None)
    else:
        operator.validate_and_run_config(run_config=cfg.mephisto, shared_state=None)

    operator.wait_for_runs_then_shutdown(
        skip_input=True, log_rate=cfg.monitoring_log_rate
    )
