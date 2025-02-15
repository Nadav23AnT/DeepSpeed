# Copyright (c) Microsoft Corporation.
# SPDX-License-Identifier: Apache-2.0

# DeepSpeed Team

import argparse

from typing import Any

from ...checkpoint import CheckpointEngineBase
from ...config_v2 import RaggedInferenceEngineConfig
from ...model_implementations.inference_policy_base import ContainerMap, InferenceV2Policy
from ...model_implementations.llama_v2.llama_v2_containers import Llama2NonTransformerContainer, Llama2TransformerContainer
from ...model_implementations.llama_v2.llama_v2_model import Llama2InferenceModel


class Llama2Policy(InferenceV2Policy):

    def __init__(self, checkpoint_engine: CheckpointEngineBase, model_config: argparse.Namespace) -> None:
        super().__init__(checkpoint_engine, model_config)

    def instantiate_model(self, engine_config: RaggedInferenceEngineConfig, mp_group: Any) -> Llama2InferenceModel:
        return Llama2InferenceModel(config=self._model_config, engine_config=engine_config, base_mp_group=mp_group)

    def build_container_map(self) -> ContainerMap:
        map = ContainerMap()

        transformer_containers = [Llama2TransformerContainer(self.model) for _ in range(self.model.num_layers)]

        map.set_transformer_params(['model.layers'], transformer_containers)

        map.set_non_transformer_params(Llama2NonTransformerContainer(self.model))

        map.set_unmapped_params(
            [f'model.layers.{i}.self_attn.rotary_emb.inv_freq' for i in range(self.model.num_layers)])

        return map
