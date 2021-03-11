# !/usr/bin/env python
import os

# Refer to opts.py for details about the flags
# graph/dataset flags
problem = "e-obm"
graph_family = "er"
weight_distribution = "uniform"
weight_distribution_param = "5 100"  # seperate by a space
graph_family_parameters = "0.05 0.1 0.15 0.2"
u_size = 100  # 10
v_size = 100  # 30
dataset_size = 10000
val_size = 100
eval_size = 1000
num_edges = 100
extention = "/{}_{}_{}_{}_{}by{}".format(
    problem,
    graph_family,
    weight_distribution,
    weight_distribution_param,
    u_size,
    v_size,
).replace(" ", "")

train_dataset = "dataset/train" + extention

val_dataset = "dataset/val" + extention

eval_dataset = "dataset/eval" + extention

# model flags
batch_size = 1
embedding_dim = 30  # 60
n_heads = 2  # 3
n_epochs = 20
checkpoint_epochs = 5
eval_baselines = "greedy"  # ******
lr_model = 0.0001
lr_decay = 0.9
n_encode_layers = 3
baseline = "exponential"
# directory io flags
output_dir = "saved_models"
log_dir = "logs_dataset"

# model evaluation flags
eval_models = "attention ff"
eval_output = "figures"
# this is a single checkpoint. Example: outputs_dataset/e-obm_20/run_20201226T171156/epoch-4.pt
load_path = None
# load_path = "../output_e-obm_er_5by15_p=0.01_uniform_m=5_v=100_a=3/e-obm_20/run_20201222T163026/epoch-69.pt"
# ../output_e-obm_er_5by15_p=0.05_uniform_m=5_v=100_a=3/e-obm_20/run_20201222T163107/epoch-69.pt \
# ../output_e-obm_er_5by15_p=0.1_uniform_m=5_v=100_a=3/e-obm_20/run_20201222T163157/epoch-69.pt \
# ../output_e-obm_er_5by15_p=0.15_uniform_m=5_v=100_a=3/e-obm_20/run_20201222T163441/epoch-69.pt \
# ../output_e-obm_er_5by15_p=0.2_uniform_m=5_v=100_a=3/outputs_e-obm_er_5by15_p=0.2_uniform_m=5_v=100_a=3/e-obm_20/run_20201222T170215/epoch-79.pt"

# this is a list of attention model checkpoints seperated by space. The number of checkpoints should be the same as the length of eval_set
# Note: checkpoints must be in the same order as eval set (i,e. checkpoint1 must be for graph paramter 0.05, etc.)

# 10by60
# attention_models = "../output_e-obm_er_10by60_p=0.01_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.01_uniform_m=5_v=100_a=3/attention/run_20210310T043543/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.05_uniform_m=5_v=100_a=3/attention/run_20210310T022438/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.1_uniform_m=5_v=100_a=3/attention/run_20210310T022441/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.15_uniform_m=5_v=100_a=3/attention/run_20210310T022543/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.2_uniform_m=5_v=100_a=3/attention/run_20210310T022545/epoch-69.pt"


# 100by100
attention_models = "../output_e-obm_er_100by100_p=0.05_uniform_m=5_v=100_a=3/attention/run_20210310T052217/epoch-59.pt \
../output_e-obm_er_100by100_p=0.1_uniform_m=5_v=100_a=3/outputs_e-obm_er_100by100_p=0.1_uniform_m=5_v=100_a=3/attention/run_20210310T052324/epoch-59.pt \
../output_e-obm_er_100by100_p=0.15_uniform_m=5_v=100_a=3/outputs_e-obm_er_100by100_p=0.15_uniform_m=5_v=100_a=3/attention/run_20210310T052320/epoch-59.pt \
../output_e-obm_er_100by100_p=0.2_uniform_m=5_v=100_a=3/outputs_e-obm_er_100by100_p=0.2_uniform_m=5_v=100_a=3/attention/run_20210310T052524/epoch-59.pt \
"

# 10by30
# attention_models = "../output_e-obm_er_10by30_p=0.01_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.01_uniform_m=5_v=100_a=3/attention/run_20210310T043543/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.05_uniform_m=5_v=100_a=3/attention/run_20210310T022430/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.1_uniform_m=5_v=100_a=3/attention/run_20210310T022430/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.15_uniform_m=5_v=100_a=3/attention/run_20210310T022430/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.2_uniform_m=5_v=100_a=3/attention/run_20210310T022430/epoch-69.pt"

# this is a list of feedforward model checkpoints seperated by space. The number of checkpoints should be the same as the length of eval_set
# Note: checkpoints must be in the same order as eval set (i,e. checkpoint1 must be for graph paramter 0.05, etc.)
# 10by30
# ff_models = "../output_e-obm_er_10by30_p=0.01_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.01_uniform_m=5_v=100_a=3/ff/run_20210310T083836/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.05_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.05_uniform_m=5_v=100_a=3/ff/run_20210310T083836/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.1_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.1_uniform_m=5_v=100_a=3/ff/run_20210310T083922/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.15_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.15_uniform_m=5_v=100_a=3/ff/run_20210310T083920/epoch-69.pt \
# ../output_e-obm_er_10by30_p=0.2_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by30_p=0.2_uniform_m=5_v=100_a=3/ff/run_20210310T083920/epoch-69.pt"

## 10by60
# ff_models = "../output_e-obm_er_10by60_p=0.01_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.01_uniform_m=5_v=100_a=3/ff/run_20210310T083915/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.05_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.05_uniform_m=5_v=100_a=3/ff/run_20210310T083914/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.1_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.1_uniform_m=5_v=100_a=3/ff/run_20210310T083914/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.15_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.15_uniform_m=5_v=100_a=3/ff/run_20210310T083914/epoch-69.pt \
# ../output_e-obm_er_10by60_p=0.2_uniform_m=5_v=100_a=3/outputs_e-obm_er_10by60_p=0.2_uniform_m=5_v=100_a=3/ff/run_20210310T083907/epoch-69.pt"


# 100by100
ff_models = "../output_e-obm_er_100by100_p=0.05_uniform_m=5_v=100_a=3/outputs_e-obm_er_100by100_p=0.05_uniform_m=5_v=100_a=3/ff/run_20210310T084054/epoch-69.pt \
../output_e-obm_er_100by100_p=0.1_uniform_m=5_v=100_a=3/ff/run_20210310T084054/epoch-69.pt \
../output_e-obm_er_100by100_p=0.15_uniform_m=5_v=100_a=3/ff/run_20210310T084103/epoch-69.pt \
../output_e-obm_er_100by100_p=0.2_uniform_m=5_v=100_a=3/ff/run_20210310T084210/epoch-69.pt"
eval_batch_size = 50
eval_set = graph_family_parameters


def make_dir():
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(eval_output):
        os.makedirs(eval_output)

    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists("data/train"):
        os.makedirs("data/train")

    if not os.path.exists("data/val"):
        os.makedirs("data/val")

    if not os.path.exists("data/eval"):
        os.makedirs("data/eval")


def generate_data():
    for n in graph_family_parameters.split(" "):
        # the naming convention here should not be changed!
        train_dir = train_dataset + "/parameter_{}".format(n)
        val_dir = val_dataset + "/parameter_{}".format(n)
        eval_dir = eval_dataset + "/parameter_{}".format(n)

        generate_train = """python data/generate_data.py --problem {} --dataset_size {} --dataset_folder {} \
                            --u_size {} --v_size {} --graph_family {} --weight_distribution {} \
                            --weight_distribution_param {} --graph_family_parameter {}""".format(
            problem,
            dataset_size,
            train_dir,
            u_size,
            v_size,
            graph_family,
            weight_distribution,
            weight_distribution_param,
            n,
        )

        generate_val = """python data/generate_data.py --problem {} --dataset_size {} --dataset_folder {}  \
                            --u_size {} --v_size {} --graph_family {} --weight_distribution {} \
                            --weight_distribution_param {} --graph_family_parameter {} --seed 20000""".format(
            problem,
            val_size,
            val_dir,
            u_size,
            v_size,
            graph_family,
            weight_distribution,
            weight_distribution_param,
            n,
        )

        generate_eval = """python data/generate_data.py --problem {} --dataset_size {} --dataset_folder {} \
                            --u_size {} --v_size {} --graph_family {} --weight_distribution {} \
                            --weight_distribution_param {} --graph_family_parameter {} --seed 40000""".format(
            problem,
            eval_size,
            eval_dir,
            u_size,
            v_size,
            graph_family,
            weight_distribution,
            weight_distribution_param,
            n,
        )

        print(generate_train)
        # os.system(generate_train)

        print(generate_val)
        # os.system(generate_val)

        # print(generate_eval)
        os.system(generate_eval)


def train_model():
    for n in graph_family_parameters.split(" "):
        # the naming convention here should not be changed!
        train_dir = train_dataset + "/parameter_{}".format(n)
        val_dir = val_dataset + "/parameter_{}".format(n)
        save_dir = output_dir + extention + "/parameter_{}".format(n)
        train = """python run.py --encoder mpnn --problem {} --batch_size {} --embedding_dim {} --n_heads {} --u_size {}  --v_size {} --n_epochs {} \
                    --train_dataset {} --val_dataset {} --dataset_size {} --val_size {} --checkpoint_epochs {} --baseline {} \
                    --lr_model {} --lr_decay {} --output_dir {} --log_dir {} --n_encode_layers {} --num_edges {} --save_dir {} --graph_family_parameter {}""".format(
            problem,
            batch_size,
            embedding_dim,
            n_heads,
            u_size,
            v_size,
            n_epochs,
            train_dir,
            val_dir,
            dataset_size,
            val_size,
            checkpoint_epochs,
            baseline,
            lr_model,
            lr_decay,
            output_dir,
            log_dir,
            n_encode_layers,
            num_edges,
            save_dir,
            n,
        )

        # print(train)
        os.system(train)


def evaluate_model():
    evaluate = """python eval.py --problem {} --embedding_dim {} --load_path {} --ff_models {} --attention_models {} --eval_baselines {} \
        --baseline {} --eval_models {} --eval_dataset {}  --u_size {} --v_size {} --eval_set {} --eval_size {} --eval_batch_size {} \
        --n_encode_layers {} --n_heads {} --output_dir {} --batch_size {} --encoder mpnn""".format(
        problem,
        embedding_dim,
        load_path,
        ff_models,
        attention_models,
        eval_baselines,
        baseline,
        eval_models,
        eval_dataset,
        u_size,
        v_size,
        eval_set,
        eval_size,
        eval_batch_size,
        n_encode_layers,
        n_heads,
        output_dir,
        eval_batch_size,
    )

    # print(evaluate)
    os.system(evaluate)


if __name__ == "__main__":
    # make the directories if they do not exist
    make_dir()
    # generate_data()
    # train_model()
    evaluate_model()
