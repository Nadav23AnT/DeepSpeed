import torch
import apex
import deepspeed
import argparse
import pytest
import json
import os
from common import distributed_test, skipIfRocm
from simple_model import SimpleModel, SimpleOptimizer, random_dataloader, args_from_dict


@skipIfRocm
def test_lamb_fp32_grad_clip(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Lamb",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1, 2])
    def _test_lamb_fp32_grad_clip(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device,
                                        dtype=torch.float)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_lamb_fp32_grad_clip(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_lamb_fp16_basic(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Lamb",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "fp16": {
            "enabled": True
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1, 2])
    def _test_lamb_fp16_basic(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_lamb_fp16_basic(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_lamb_fp16_empty_grad(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Lamb",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "fp16": {
            "enabled": True
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=True, rank=args.local_rank)

    @distributed_test(world_size=[2])
    def _test_lamb_fp16_empty_grad(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_lamb_fp16_empty_grad(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_adam_fp32_empty_grad(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "fp16": {
            "enabled": False
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=True, rank=args.local_rank)

    @distributed_test(world_size=[2])
    def _test_adam_fp32_empty_grad(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device,
                                        dtype=torch.float)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adam_fp32_empty_grad(args=args, model=model, hidden_dim=hidden_dim)


def test_adamw_fp16_basic(tmpdir):
    config_dict = {
        "train_batch_size": 1,
        "steps_per_print": 1,
        "fp16": {
            "enabled": True
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1])
    def _test_adamw_fp16_basic(args, model, hidden_dim):
        optimizer = torch.optim.AdamW(params=model.parameters())
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             optimizer=optimizer)
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adamw_fp16_basic(args=args, model=model, hidden_dim=hidden_dim)


def test_adamw_fp16_empty_grad(tmpdir):
    config_dict = {
        "train_batch_size": 1,
        "steps_per_print": 1,
        "fp16": {
            "enabled": True
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=True)

    @distributed_test(world_size=[1])
    def _test_adamw_fp16_empty_grad(args, model, hidden_dim):
        optimizer = torch.optim.AdamW(params=model.parameters())
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             optimizer=optimizer)
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adamw_fp16_empty_grad(args=args, model=model, hidden_dim=hidden_dim)


@pytest.mark.parametrize('zero_stage, use_cpu_offload',
                         [
                             (1,
                              False),
                             (2,
                              False),
                             (2,
                              True),
                         ])
def test_adam_fp16_zero_onecycle_compatibility(tmpdir, zero_stage, use_cpu_offload):
    config_dict = {
        "train_batch_size": 1,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "scheduler": {
            "type": "OneCycle",
            "params": {
                "cycle_first_step_size": 16000,
                "cycle_first_stair_count": 8000,
                "decay_step_size": 16000,
                "cycle_min_lr": 1e-06,
                "cycle_max_lr": 3e-05,
                "decay_lr_rate": 1e-07,
                "cycle_min_mom": 0.85,
                "cycle_max_mom": 0.99,
                "decay_mom_rate": 0.0
            }
        },
        "fp16": {
            "enabled": True
        },
        "zero_optimization": {
            "stage": zero_stage,
            "cpu_offload": use_cpu_offload
        }
    }

    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=True)

    @distributed_test(world_size=[1])
    def _test_adam_fp16_zero_onecycle_compatibility(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adam_fp16_zero_onecycle_compatibility(args=args,
                                                model=model,
                                                hidden_dim=hidden_dim)


@pytest.mark.parametrize('zero_stage, use_cpu_offload',
                         [
                             (1,
                              False),
                             (2,
                              False),
                             (2,
                              True),
                         ])
@skipIfRocm
def test_zero_static_scale(tmpdir, zero_stage, use_cpu_offload):
    config_dict = {
        "train_batch_size": 4,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "fp16": {
            "enabled": True,
            "loss_scale": 138.
        },
        "zero_optimization": {
            "stage": zero_stage,
            "cpu_offload": use_cpu_offload
        }
    }
    args = args_from_dict(tmpdir, config_dict)

    @distributed_test(world_size=2)
    def _test_zero_static_scale(args):
        hidden_dim = 10
        model = SimpleModel(hidden_dim, empty_grad=True)
        model, optim, _,_ = deepspeed.initialize(args=args,
                                            model=model,
                                            model_parameters=model.parameters())

        # Ensure the static scaler is configured.
        assert optim.dynamic_loss_scale == False
        assert optim.loss_scaler.loss_scale == 138.

        # Now make sure things work..
        data_loader = random_dataloader(model=model,
                                        total_samples=10,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_zero_static_scale(args)


@skipIfRocm
def test_zero_static_scale_deprecated_format(tmpdir):
    config_dict = {
        "train_batch_size": 4,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "fp16": {
            "enabled": True,
            "loss_scale": 138.
        },
        "zero_optimization": True
    }
    args = args_from_dict(tmpdir, config_dict)

    @distributed_test(world_size=2)
    def _test_zero_static_scale(args):
        hidden_dim = 10
        model = SimpleModel(hidden_dim, empty_grad=True)
        model, optim, _,_ = deepspeed.initialize(args=args,
                                            model=model,
                                            model_parameters=model.parameters())

        # Ensure the static scaler is configured.
        assert optim.dynamic_loss_scale == False
        assert optim.loss_scaler.loss_scale == 138.

        # Now make sure things work..
        data_loader = random_dataloader(model=model,
                                        total_samples=10,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_zero_static_scale(args)


@pytest.mark.parametrize('zero_stage, use_cpu_offload',
                         [
                             (1,
                              False),
                             (2,
                              False),
                             (2,
                              True),
                         ])
def test_zero_allow_untested_optimizer(tmpdir, zero_stage, use_cpu_offload):
    config_dict = {
        "train_batch_size": 4,
        "steps_per_print": 1,
        "fp16": {
            "enabled": True,
        },
        "zero_optimization": {
            "stage": zero_stage,
            "cpu_offload": use_cpu_offload
        },
        "zero_allow_untested_optimizer": False
    }
    args = args_from_dict(tmpdir, config_dict)

    @distributed_test(world_size=[1])
    def _test_zero_allow_untested_optimizer(args):
        hidden_dim = 10
        model = SimpleModel(hidden_dim, empty_grad=True)
        optimizer = SimpleOptimizer(model.parameters())
        with pytest.raises(AssertionError):
            model, optim, _,_ = deepspeed.initialize(args=args,
                                                    model=model,
                                                    optimizer=optimizer,
                                                    model_parameters=model.parameters())

    _test_zero_allow_untested_optimizer(args)


@pytest.mark.parametrize('zero_stage, use_cpu_offload',
                         [
                             (1,
                              False),
                             (2,
                              False),
                             (2,
                              True),
                         ])
@skipIfRocm
def test_zero_empty_partition(tmpdir, zero_stage, use_cpu_offload):
    config_dict = {
        "train_micro_batch_size_per_gpu": 1,
        "gradient_accumulation_steps": 1,
        "fp16": {
            "enabled": True,
            "initial_scale_power": 8
        },
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "zero_optimization": {
            "stage": zero_stage,
            "cpu_offload": use_cpu_offload,
            "reduce_bucket_size": 100,
            "allgather_bucket_size": 100
        }
    }
    args = args_from_dict(tmpdir, config_dict)

    @distributed_test(world_size=[3])
    def _test_zero_empty_partition(args):
        hidden_dim = 1
        model = SimpleModel(hidden_dim)
        # Ensure model has 2 parameters, to cause empty partition with DP=3
        assert len(list(model.parameters())) == 2
        model, _, _, _ = deepspeed.initialize(args=args,
                                              model=model,
                                              model_parameters=model.parameters())

        # Now make sure things work..
        data_loader = random_dataloader(model=model,
                                        total_samples=1,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_zero_empty_partition(args)


def test_adam_amp_basic(tmpdir):
    config_dict = {"train_batch_size": 1, "steps_per_print": 1, "amp": {"enabled": True}}
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1])
    def _test_adam_amp_basic(args, model, hidden_dim):
        optimizer = torch.optim.Adam(params=model.parameters())
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             optimizer=optimizer)
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adam_amp_basic(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_lamb_amp_basic(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Lamb",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "amp": {
            "enabled": True,
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1, 2])
    def _test_lamb_amp_basic(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_lamb_amp_basic(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_adam_amp_o2(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "amp": {
            "enabled": True,
            "opt_level": "O2"
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1, 2])
    def _test_adam_amp_o2(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adam_amp_o2(args=args, model=model, hidden_dim=hidden_dim)


@skipIfRocm
def test_adam_amp_o2_empty_grad(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "amp": {
            "enabled": True,
            "opt_level": "O2"
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False, rank=args.local_rank)

    @distributed_test(world_size=[2])
    def _test_adam_amp_o2_empty_grad(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _test_adam_amp_o2_empty_grad(args=args, model=model, hidden_dim=hidden_dim)


@pytest.mark.parametrize('zero_stage, optimizer_constructor',
                         [(1,
                           apex.optimizers.FusedAdam),
                          (2,
                           torch.optim.Adam),
                          (2,
                           apex.optimizers.FusedAdam)])
def test_zero_supported_client_optimizer(tmpdir, zero_stage, optimizer_constructor):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "fp16": {
            "enabled": True
        },
        "zero_optimization": {
            "stage": zero_stage
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, empty_grad=False)

    @distributed_test(world_size=[1])
    def _test_zero_supported_client_optimizer(args, model, optimizer_constructor):
        client_optimizer = optimizer_constructor(params=model.parameters())
        model, _, _, _ = deepspeed.initialize(args=args,
                                               model=model,
                                               optimizer=client_optimizer)

    _test_zero_supported_client_optimizer(args=args,
                                          model=model,
                                          optimizer_constructor=optimizer_constructor)


@skipIfRocm
def test_zero2_reduce_scatter_off(tmpdir):
    config_dict = {
        "train_batch_size": 2,
        "steps_per_print": 1,
        "optimizer": {
            "type": "Adam",
            "params": {
                "lr": 0.00015
            }
        },
        "gradient_clipping": 1.0,
        "zero_optimization": {
            "stage": 2,
            "contiguous_gradients": True,
            "allgather_bucket_size": 2000000000,
            "reduce_bucket_size": 200000000,
            "overlap_comm": False,
            "reduce_scatter": False
        },
        "fp16": {
            "enabled": True
        }
    }
    args = args_from_dict(tmpdir, config_dict)
    hidden_dim = 10

    model = SimpleModel(hidden_dim, rank=args.local_rank)

    @distributed_test(world_size=[2])
    def _helper(args, model, hidden_dim):
        model, _, _,_ = deepspeed.initialize(args=args,
                                             model=model,
                                             model_parameters=model.parameters())
        data_loader = random_dataloader(model=model,
                                        total_samples=50,
                                        hidden_dim=hidden_dim,
                                        device=model.device)
        for n, batch in enumerate(data_loader):
            loss = model(batch[0], batch[1])
            model.backward(loss)
            model.step()

    _helper(args=args, model=model, hidden_dim=hidden_dim)
