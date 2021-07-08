#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

import os
import time
from dataclasses import dataclass, field
from typing import Any, List

import hydra
from mephisto.operations.hydra_config import register_script_config
from omegaconf import DictConfig

from parlai.crowdsourcing.tasks.turn_annotations_static.turn_annotations_blueprint import (
    STATIC_BLUEPRINT_TYPE,
)
from parlai.crowdsourcing.tasks.turn_annotations_static.util import run_static_task
from parlai.crowdsourcing.utils.mturk import MTurkRunScriptConfig


TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))


defaults = [
    {'mephisto/blueprint': STATIC_BLUEPRINT_TYPE},
    {"mephisto/architect": "heroku"},
    {"mephisto/provider": "mturk_sandbox"},
    {"conf": "example"},
]


@dataclass
class ScriptConfig(MTurkRunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    qua_id: str = str(time.time())
    monitoring_log_rate: int = field(
        default=30,
        metadata={
            'help': 'Frequency in seconds of logging the monitoring of the crowdsourcing task'
        },
    )
    multiple_tasks: bool = field(
        default=False,
        metadata={"help": "Read tasks from database and create multiple tasks at once"}
    )


register_script_config(name='scriptconfig', module=ScriptConfig)


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    run_static_task(cfg=cfg, task_directory=TASK_DIRECTORY)


if __name__ == "__main__":
    main()
