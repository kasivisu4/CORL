# !/usr/bin/env python

import os
import json
import pprint as pp

import torch
import torch.optim as optim
from torch.utils.data import DataLoader

# from nets.critic_network import CriticNetwork
from options import get_options
from train import train_epoch, validate, get_inner_model, eval_model, evaluate
from policy.attention_model_v2 import AttentionModel
from policy.ff_model_v2 import FeedForwardModel
from policy.greedy import Greedy
from policy.greedy_rt import GreedyRt
from policy.simple_greedy import SimpleGreedy

import numpy as np
import time
from tqdm import tqdm

import math
import matplotlib.pyplot as plt

from torch.nn import DataParallel
from policy.attention_model_v2 import set_decode_type
from log_utils import log_values
from functions import move_to

# from nets.pointer_network import PointerNetwork, CriticNetworkLSTM
from functions import torch_load_cpu, load_problem


def eval_models(opts, models, problem):
    """
    Evaluate the models on a specific set of graph family parameters
    """
    pass


def validate_many(opts, model, problem):
    """
    Evaluate the models on a range of graph family parameters
    """

    crs = []
    avg_crs = []
    min_p, max_p = float(opts.eval_range[0]), float(opts.eval_range[1])
    for i, j in enumerate(
        np.arange(min_p, max_p, (min_p + max_p) / opts.eval_num_range)
    ):
        dataset_folder = opts.eval_dataset

        eval_dataset = problem.make_dataset(
            dataset_folder, opts.eval_size, opts.problem
        )
        eval_dataloader = DataLoader(
            eval_dataset, batch_size=opts.eval_batch_size, num_workers=1
        )

        avg_ratio, cr, avg_cr = validate(model, eval_dataloader, opts)
        crs.append(cr)
        avg_crs.append(avg_cr)
    plt.figure(1)
    plt.plot(np.arange(min_p, max_p, (min_p + max_p) / opts.eval_num_range), crs)
    plt.xlabel("Graph family parameter")
    plt.ylabel("Competitive ratio")

    plt.savefig(opts.eval_output + "/competitive_ratio.png")

    plt.figure(2)
    plt.plot(np.arange(min_p, max_p, (min_p + max_p) / opts.eval_num_range), avg_crs)
    plt.xlabel("Graph family parameter")
    plt.ylabel("Average ratio to optimal")

    plt.savefig(opts.eval_output + "/avg_optim_ratio.png")


def get_op_ratios(opts, model, problem):
    """
    given the model, run the model on the evaluation dataset and return the optmiality ratios
    """
    # get the path to the test set dir
    ops = []
    # for i in graph family parameters
    for i in range(len(opts.eval_set)):
        # get the eval dataset as a pytorch dataset object
        eval_dataset = problem.make_dataset(
            opts.eval_dataset, opts.eval_size, opts.eval_size, opts.problem, opts
        )
        eval_dataloader = DataLoader(
            eval_dataset, batch_size=opts.eval_batch_size, num_workers=0
        )

        op = evaluate(model, eval_dataloader, opts)
        ops.append(op.cpu().numpy())
    return np.array(ops)


def set_box_color(bp, color):
    plt.setp(bp["boxes"], color=color)
    plt.setp(bp["whiskers"], color=color)
    plt.setp(bp["caps"], color=color)
    plt.setp(bp["medians"], color="#4d4d4d")


def plot_box(opts, data):
    """
    plots the box data.
    data is a list of (|graph family param| x |training examples|) arrays
    """
    plt.figure()
    num = len(data)
    plt.xlabel("Graph family parameter")
    plt.ylabel("Optimality ratio")
    ticks = opts.eval_set  # ["0.01", "0.05", "0.1", "0.15", "0.2"]
    colors = ["#d53e4f", "#3288bd", "#7fbf7b", "#fee08b", "#fc8d59", "#e6f598"]
    i = 0
    for d in data:
        bp = plt.boxplot(
            d.T,
            positions=np.array(range(len(d))) * num + (0.2 * i),
            sym="",
            widths=0.6,
            whis=(0, 100),
        )
        set_box_color(bp, colors[i])
        i += 1

    plt.xlim(-1 * num, len(ticks) * num)
    # plt.ylim(0, 1)
    plt.xticks(range(0, len(ticks) * num, num), ticks)
    plt.savefig(
        opts.eval_output
        + "/{}_{}by{}.png".format(opts.graph_family, opts.u_size, opts.v_size)
    )


def load_models(opts):
    """
    Load models (here we refer to them as data) from load_path
    """
    load_data = {}
    load_datas = []
    path = opts.load_path if opts.load_path is not None else []
    if path is not None:
        print("  [*] Loading data from {}".format(path))
        load_data = torch_load_cpu(path)
        load_datas.append(load_data)
    return load_datas


def load_attention_models(opts):
    """
    load models from the attention models dir
    """
    load_data = {}
    load_datas = []
    attention_dir = (
        opts.eval_attention_dir if opts.eval_attention_dir is not None else []
    )
    print(" Loading all the attention models from {}".format(attention_dir))
    for path in os.listdir(attention_dir):
        load_data = torch_load_cpu(path)
        load_datas.append(load_data)
    return load_datas


def load_ff_models(opts):
    """
    load models from the feed forward models dir
    """
    load_data = {}
    load_datas = []
    ff_dir = opts.eval_ff_dir if opts.eval_ff_dir is not None else []
    print("Loading all the feed forward models from {}".format(ff_dir))
    for path in os.listdir(ff_dir):
        load_data = torch_load_cpu(path)
        load_datas.append(load_data)
    return load_datas


def initialize_models(opts, models, load_datas):
    problem = load_problem(opts.problem)
    for m in range(len(opts.eval_models)):
        model_class = {"attention": AttentionModel, "ff": FeedForwardModel}.get(
            opts.eval_models[m], None
        )
        model = model_class(
            opts.embedding_dim,
            opts.hidden_dim,
            problem=problem,
            n_encode_layers=opts.n_encode_layers,
            mask_inner=True,
            mask_logits=True,
            normalization=opts.normalization,
            tanh_clipping=opts.tanh_clipping,
            checkpoint_encoder=opts.checkpoint_encoder,
            shrink_size=opts.shrink_size,
            num_actions=opts.u_size + 1,
            n_heads=opts.n_heads,
        ).to(opts.device)

        if opts.use_cuda and torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model)

        # Overwrite model parameters by parameters to load
        model_ = get_inner_model(model)
        model_.load_state_dict(
            {**model_.state_dict(), **load_datas[m].get("model", {})}
        )
        models.append(model)


def initialize_attention_models(opts, attention_models, load_attention_datas):
    problem = load_problem(opts.problem)
    for m in range(len(load_attention_datas)):
        model = AttentionModel(
            opts.embedding_dim,
            opts.hidden_dim,
            problem=problem,
            n_encode_layers=opts.n_encode_layers,
            mask_inner=True,
            mask_logits=True,
            normalization=opts.normalization,
            tanh_clipping=opts.tanh_clipping,
            checkpoint_encoder=opts.checkpoint_encoder,
            shrink_size=opts.shrink_size,
            num_actions=opts.u_size + 1,
            n_heads=opts.n_heads,
        ).to(opts.device)

        if opts.use_cuda and torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model)

        # Overwrite model parameters by parameters to load
        model_ = get_inner_model(model)
        model_.load_state_dict(
            {**model_.state_dict(), **load_attention_datas[m].get("model", {})}
        )
        attention_models.append(model)


def initialize_ff_models(opts, ff_models, load_ff_datas):
    problem = load_problem(opts.problem)
    for m in range(len(load_ff_datas)):
        model = FeedForwardModel(
            opts.embedding_dim,
            opts.hidden_dim,
            problem=problem,
            n_encode_layers=opts.n_encode_layers,
            mask_inner=True,
            mask_logits=True,
            normalization=opts.normalization,
            tanh_clipping=opts.tanh_clipping,
            checkpoint_encoder=opts.checkpoint_encoder,
            shrink_size=opts.shrink_size,
            num_actions=opts.u_size + 1,
            n_heads=opts.n_heads,
        ).to(opts.device)

        if opts.use_cuda and torch.cuda.device_count() > 1:
            model = torch.nn.DataParallel(model)

        # Overwrite model parameters by parameters to load
        model_ = get_inner_model(model)
        model_.load_state_dict(
            {**model_.state_dict(), **load_ff_datas[m].get("model", {})}
        )
        ff_models.append(model)


def run(opts):

    # Pretty print the run args
    pp.pprint(vars(opts))

    # Set the random seed
    torch.manual_seed(opts.seed)

    os.makedirs(opts.save_dir)
    # Save arguments so exact configuration can always be found
    with open(os.path.join(opts.save_dir, "args.json"), "w") as f:
        json.dump(vars(opts), f, indent=True)

    # Set the device
    opts.device = torch.device("cuda:0" if opts.use_cuda else "cpu")

    # Figure out what's the problem
    problem = load_problem(opts.problem)
    if opts.eval_plot:
        t = torch.load(opts.eval_results_file)
        plot_box(opts, np.array(t))
        return

    # load the basline and neural net models and save them in models, attention_models, ff_models, baseline_models

    # load models
    assert (
        opts.load_path is None
        and opts.eval_ff_dir is None
        and opts.eval_attention_dir is None
    ) or opts.resume is None, "either one of load_path, eval_ff_dir, eval_attention_dir as well as resume should be given"
    models = []
    # Initialize models
    if opts.load_path is not None:
        load_datas = load_models(opts)
        # these are the models that are specified in by the file
        initialize_models(opts, models, load_datas)
    elif opts.eval_attention_dir is not None:
        load_attention_datas = load_attention_models(opts)
        initialize_attention_models(
            opts, models, load_attention_datas
        )  # attention models from the directory
    elif opts.eval_ff_dir is not None:
        load_ff_datas = load_ff_models(opts)
        initialize_ff_models(
            opts, models, load_ff_datas
        )  # feed forwad models from the directory

    print("models: ", models)

    # Initialize baseline models
    baseline_models = []
    for i in range(len(opts.eval_baselines)):
        baseline_model_class = {
            "greedy": Greedy,
            "greedy-rt": GreedyRt,
            "simple-greedy": SimpleGreedy,
        }.get(opts.eval_baselines[i], None)
        assert baseline_model_class is not None, "Unknown baseline model: {}".format(
            opts.eval_baselines[i]
        )
        model = baseline_model_class(
            opts.embedding_dim,
            opts.hidden_dim,
            problem=problem,
            n_encode_layers=opts.n_encode_layers,
            mask_inner=True,
            mask_logits=True,
            normalization=opts.normalization,
            tanh_clipping=opts.tanh_clipping,
            checkpoint_encoder=opts.checkpoint_encoder,
            shrink_size=opts.shrink_size,
            num_actions=opts.u_size + 1,
        ).to(opts.device)
        baseline_models.append(model)

    if len(opts.eval_set) > 0:
        baseline_results = []
        trained_models_results = []
        # plot_data = []
        for m in baseline_models:  # Get the performance of the baselines
            ops = get_op_ratios(opts, m, problem)
            baseline_results.append(ops)
        for m in range(len(models)):  # Get the performance of the trained models
            ops = get_op_ratios(opts, models[m], problem)
            trained_models_results.append(ops[m])
        # print('baseline_results[0]: ', baseline_results[0])
        # print('trained_models_results ', trained_models_results)
        results = [np.array(baseline_results[0]), np.array(trained_models_results)]
        torch.save(
            results,
            opts.eval_output
            + "/{}_{}_{}_{}_{}by{}_results".format(
                opts.problem,
                opts.graph_family,
                opts.weight_distribution,
                opts.weight_distribution_param,
                opts.u_size,
                opts.v_size,
            ).replace(" ", ""),
        )
        plot_box(opts, results)
    if opts.eval_family:
        validate_many(opts, model, problem)
    if opts.eval_plot:
        plot_box(opts, np.array(torch.load(opts.eval_results_folder)))

    # elif opts.eval_model:
    #     model1 = FeedForwardModel(
    #         (opts.u_size + 1) * 2,
    #         opts.hidden_dim,
    #         problem,
    #         n_encode_layers=opts.n_encode_layers,
    #         mask_inner=True,
    #         mask_logits=True,
    #         normalization=opts.normalization,
    #         tanh_clipping=opts.tanh_clipping,
    #         checkpoint_encoder=opts.checkpoint_encoder,
    #         shrink_size=opts.shrink_size,
    #         num_actions=opts.u_size + 1,
    #     ).to(opts.device)
    #     model1_ = get_inner_model(model1)
    #     model1_.load_state_dict({**model1_.state_dict(), **load_data2.get("model", {})})
    #     eval_model([model, model1], problem, opts)


if __name__ == "__main__":
    run(get_options())
