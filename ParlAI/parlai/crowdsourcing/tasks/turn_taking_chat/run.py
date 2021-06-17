#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.


import os
import time
from mephisto.operations.operator import Operator
from mephisto.tools.scripts import load_db_and_process_config
from mephisto.abstractions.blueprints.parlai_chat.parlai_chat_blueprint import (
    BLUEPRINT_TYPE,
    SharedParlAITaskState,
)

import hydra
from omegaconf import DictConfig
from dataclasses import dataclass, field
from typing import List, Any

from mephisto.abstractions.databases.local_database import LocalMephistoDB
from mephisto.tools.data_browser import DataBrowser as MephistoDataBrowser
from mephisto.data_model.worker import Worker
from mephisto.data_model.unit import Unit

db = LocalMephistoDB()
mephisto_data_browser = MephistoDataBrowser(db=db)

TASK_DIRECTORY = os.path.dirname(os.path.abspath(__file__))

defaults = [
    {"mephisto/blueprint": BLUEPRINT_TYPE},
    {"mephisto/architect": "heroku"},
    {"mephisto/provider": "mturk_sandbox"},
    "conf/base",
    {"conf": "custom_prebuilt"},
]

from mephisto.operations.hydra_config import RunScriptConfig, register_script_config
# from mephisto.abstractions.blueprints.abstract.static_task.static_blueprint import (
#     SharedStaticTaskState,
# )

@dataclass
class TestScriptConfig(RunScriptConfig):
    defaults: List[Any] = field(default_factory=lambda: defaults)
    task_dir: str = TASK_DIRECTORY
    qua_id: str = str(time.time())
    max_turns: int = field(
        default=2,
        metadata={"help": "Number of turns before a conversation is complete"},
    )
    manual_validate: bool = field(
        default=False,
        metadata={"help": "Validate result from workers manually"}
    )
    max_count: int = field(
        default=1,
        metadata={"help": "Maximum duplicate words in replies"}
    )
    min_length: int = field(
        default=5,
        metadata={"help": "Minimum length of each reply"}
    )
    turn_timeout: int = field(
        default=300,
        metadata={
            "help": "Maximum response time before kicking "
            "a worker out, default 300 seconds"
        },
    )


register_script_config(name="scriptconfig", module=TestScriptConfig)


@hydra.main(config_name="scriptconfig")
def main(cfg: DictConfig) -> None:
    db, cfg = load_db_and_process_config(cfg)

    world_opt = {"max_turns": cfg.max_turns, "turn_timeout": cfg.turn_timeout}

    custom_bundle_path = cfg.mephisto.blueprint.get("custom_source_bundle", None)
    if custom_bundle_path is not None:
        assert os.path.exists(custom_bundle_path), (
            "Must build the custom bundle with `npm install; npm run dev` from within "
            f"the {TASK_DIRECTORY}/webapp directory in order to demo a custom bundle "
        )
        world_opt["send_task_data"] = True

    shared_state = SharedParlAITaskState(
        world_opt=world_opt, onboarding_world_opt=world_opt,
    )
    # shared_state = SharedStaticTaskState(
    #     static_task_data=[
    #         {"text": "This text is good text!"},
    #         {"text": "This text is bad text!"},
    #     ],
    #     validate_onboarding=onboarding_always_valid,
    # )
    shared_state.mturk_specific_qualifications = [
        {
            "QualificationTypeId": "00000000000000000040",
            "Comparator": "LessThanOrEqualTo",#GreaterThanOrEqualTo
            "IntegerValues": [100],
            "ActionsGuarded": "PreviewAndAccept",
        },
        {
            "QualificationTypeId": "000000000000000000L0",
            "Comparator": "GreaterThanOrEqualTo",#GreaterThanOrEqualTo
            "IntegerValues": [90],
            "ActionsGuarded": "PreviewAndAccept",
        }
    ]

    operator = Operator(db)

    operator.validate_and_run_config(cfg.mephisto, shared_state)
    operator.wait_for_runs_then_shutdown(skip_input=True, log_rate=30)

    print("....................validating result started.............")
    if not cfg.manual_validate:
        units = mephisto_data_browser.get_units_for_task_name("turn-taking-chat")
        units = [u for u in units if u.get_status() == "completed"]

        for unit in units:
            data = mephisto_data_browser.get_data_from_unit(unit)
            org_messages = [message['text'].strip().lower() for message in data['data']['messages'] if message['id'] == data['data']['agent_name']]
            messages = list(set(org_messages))

            if len(org_messages) - len(messages) >= cfg.max_count:
                unit.get_assigned_agent().reject_work("There are too many duplicates replies in your conversation.")
                print("Rejected because of too many duplicates.\n")
            else:
                monotonous = len([message for message in messages if len(message) <= cfg.min_length])
                if monotonous >= cfg.max_count:
                    unit.get_assigned_agent().reject_work("There are too many monotonous replies in your conversation.")
                    print("Rejected because of too monotonous replies.\n")
                else:
                    unit.get_assigned_agent().approve_work()
                    print("Approved and paid out.\n")


if __name__ == "__main__":
    main()
