import mne
import os
import json
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from eye_tracker.general_helper_function import baseline_scaling, cluster_1samp_across_sub
from eye_tracker.plotter_functions import plot_ts_ci
import environment_variables as ev

# Set the font size:
plt.rcParams.update({'font.size': 14})


def pupil_amplitude(parameters_file, subjects):
    # First, load the parameters:
    with open(parameters_file) as json_file:
        param = json.load(json_file)
    # Load all subjects data:
    subjects_epochs = {sub: None for sub in subjects}
    # Create the directory to save the results in:
    save_dir = Path(ev.bids_root, "derivatives", "pupil_amplitude")
    if not os.path.isdir(save_dir):
        os.makedirs(save_dir)

    # Loop through each subject:
    for sub in subjects:
        print("Loading sub-{}".format(sub))
        root = Path(ev.bids_root, "derivatives", "preprocessing", "sub-" + sub, "ses-" + param["session"],
                    param["data_type"])
        file_name = "sub-{}_ses-{}_task-{}_{}_desc-{}-epo.fif".format(sub, param["session"], param["task"],
                                                                      param["data_type"],
                                                                      param["epoch_name"])
        epochs = mne.read_epochs(Path(root, file_name))
        # Extract the relevant conditions:
        epochs = epochs[param["task_relevance"]]
        # Crop if needed:
        epochs.crop(param["crop"][0], param["crop"][1])
        # Extract the relevant channels:
        epochs.pick(param["picks"])
        # Baseline correction:
        baseline_scaling(epochs, correction_method=param["baseline"], baseline=param["baseline_window"])
        subjects_epochs[sub] = epochs

    # ==================================================================================================================
    # Task relevance comparisons:
    # =====================================================================================
    # Onset locked task relevance analysis:
    # ===========================================================
    # Create the condition string:
    lock = "onset"
    conditions = ["/".join([task, lock]) for task in param["task_relevance"]]
    # Compute cluster based permutation test across subject between task relevant and irrelevant:
    evks, evks_diff, _, clusters, cluster_p_values, _ = (
        cluster_1samp_across_sub(subjects_epochs, conditions,
                                 n_permutations=param["n_permutations"],
                                 threshold=param["threshold"],
                                 tail=1))
    # Plot the results:
    fig, ax = plt.subplots(figsize=[8.3, 11.7/3])
    # Task relevant:
    plot_ts_ci(evks[conditions[0]], epochs.times, ev.colors["task_relevance"][param["task_relevance"][0]],
               ax=ax, label=param["task_relevance"][0])
    # Task irrelevant (plot the cluster only on one to avoid incremental plotting):
    plot_ts_ci(evks[conditions[1]], epochs.times, ev.colors["task_relevance"][param["task_relevance"][1]],
               ax=ax, label=param["task_relevance"][1], clusters=clusters,
               clusters_pval=cluster_p_values, clusters_alpha=0.1)
    # Decorate the axes:
    ax.set_xlabel("Time (sec.)")
    ax.set_ylabel("Pupil dilation (norm.)")
    ax.spines[['right', 'top']].set_visible(False)
    plt.legend()
    plt.title("{} locked pupil size across durations (N={})".format(lock, len(subjects)))
    plt.tight_layout()
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}.svg".format(lock)), transparent=True, dpi=300)
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}.png".format(lock)), transparent=True, dpi=300)
    plt.close()

    # ===========================================================
    # Separately for each trial durations:
    # Prepare a figure for all the durations:
    fig, ax = plt.subplots(3, 1, sharex=True, sharey=True, figsize=[8.3, 11.7/3])
    for dur_i, dur in enumerate(param["duration"]):
        # Prepare the condition strings:
        conditions = ["/".join([task, dur, lock]) for task in param["task_relevance"]]
        # Run cluster based permutation test:
        evks_dur, evks_diff_dur, _, clusters, cluster_p_values, _ = (
            cluster_1samp_across_sub(subjects_epochs, conditions,
                                     n_permutations=param["n_permutations"],
                                     threshold=param["threshold"],
                                     tail=1))
        # Plot the results:
        # Task relevant:
        plot_ts_ci(evks_dur[conditions[0]], epochs.times,
                   ev.colors["task_relevance"][param["task_relevance"][0]], ax=ax[dur_i],
                   label=param["task_relevance"][0])
        # Task irrelevant:
        plot_ts_ci(evks_dur[conditions[1]], epochs.times,
                   ev.colors["task_relevance"][param["task_relevance"][1]], ax=ax[dur_i], clusters=clusters,
                   clusters_pval=cluster_p_values, clusters_alpha=0.1,
                   label=param["task_relevance"][1])

    # Decorate the axes:
    ax[0].spines[['right', 'top']].set_visible(False)
    ax[0].set_title("Short")
    ax[1].set_ylabel("Pupil dilation (norm.)")
    ax[1].spines[['right', 'top']].set_visible(False)
    ax[1].set_title("Intermediate")
    ax[2].set_xlabel("Time (sec.)")
    ax[2].set_title("Long")
    ax[2].spines[['right', 'top']].set_visible(False)
    ax[2].legend()
    plt.suptitle("{} locked pupil size (N={})".format(lock, len(subjects)))
    plt.tight_layout()
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}_perdur.svg".format(lock)), transparent=True, dpi=300)
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}_perdur.png".format(lock)), transparent=True, dpi=300)
    plt.close()

    # ==================================================================================================================
    # Offset locked task relevance analysis:
    # ===========================================================
    # Create the condition string:
    lock = "offset"
    conditions = ["/".join([task, lock]) for task in param["task_relevance"]]
    # Compute cluster based permutation test across subject between task relevant and irrelevant:
    evks, evks_diff, _, clusters, cluster_p_values, _ = (
        cluster_1samp_across_sub(subjects_epochs, conditions,
                                 n_permutations=param["n_permutations"],
                                 threshold=param["threshold"],
                                 tail=1))
    # Plot the results:
    fig, ax = plt.subplots(figsize=[8.3, 11.7/3])
    # Task relevant:
    plot_ts_ci(evks[conditions[0]], epochs.times, ev.colors["task_relevance"][param["task_relevance"][0]],
               ax=ax, label=param["task_relevance"][0])
    # Task irrelevant (plot the cluster only on one to avoid incremental plotting):
    plot_ts_ci(evks[conditions[1]], epochs.times, ev.colors["task_relevance"][param["task_relevance"][1]],
               ax=ax, label=param["task_relevance"][1], clusters=clusters,
               clusters_pval=cluster_p_values, clusters_alpha=0.1)
    # Decorate the axes:
    ax.set_xlabel("Time (sec.)")
    ax.set_ylabel("Pupil dilation (norm.)")
    ax.spines[['right', 'top']].set_visible(False)
    plt.legend()
    plt.title("{} locked pupil size across durations (N={})".format(lock, len(subjects)))
    plt.tight_layout()
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}.svg".format(lock)), transparent=True, dpi=300)
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}.png".format(lock)), transparent=True, dpi=300)
    plt.close()

    # ===========================================================
    # Separately for each trial durations:
    # Prepare a figure for all the durations:
    fig, ax = plt.subplots(3, 1, sharex=True, sharey=True, figsize=[8.3, 11.7/3])
    for dur_i, dur in enumerate(param["duration"]):
        # Prepare the condition strings:
        conditions = ["/".join([task, dur, lock]) for task in param["task_relevance"]]
        # Run cluster based permutation test:
        evks_dur, evks_diff_dur, _, clusters, cluster_p_values, _ = (
            cluster_1samp_across_sub(subjects_epochs, conditions,
                                     n_permutations=param["n_permutations"],
                                     threshold=param["threshold"],
                                     tail=1))
        # Plot the results:
        # Task relevant:
        plot_ts_ci(evks_dur[conditions[0]], epochs.times,
                   ev.colors["task_relevance"][param["task_relevance"][0]], ax=ax[dur_i],
                   label=param["task_relevance"][0])
        # Task irrelevant:
        plot_ts_ci(evks_dur[conditions[1]], epochs.times,
                   ev.colors["task_relevance"][param["task_relevance"][1]], ax=ax[dur_i], clusters=clusters,
                   clusters_pval=cluster_p_values, clusters_alpha=0.1,
                   label=param["task_relevance"][1])
    # Decorate the axes:
    ax[0].spines[['right', 'top']].set_visible(False)
    ax[0].set_title("Short")
    ax[1].set_ylabel("Pupil dilation (norm.)")
    ax[1].spines[['right', 'top']].set_visible(False)
    ax[1].set_title("Intermediate")
    ax[2].set_xlabel("Time (sec.)")
    ax[2].set_title("Long")
    ax[2].spines[['right', 'top']].set_visible(False)
    ax[2].legend()
    plt.suptitle("{} locked pupil size (N={})".format(lock, len(subjects)))
    plt.tight_layout()
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}_perdur.svg".format(lock)), transparent=True, dpi=300)
    fig.savefig(Path(save_dir, "pupil_evoked_titr_{}_perdur.png".format(lock)), transparent=True, dpi=300)
    plt.close()


if __name__ == "__main__":
    subjects_list = ["SX102", "SX103", "SX105", "SX106", "SX107", "SX108", "SX109", "SX110", "SX111", "SX112", "SX113",
                     "SX114", "SX115", "SX118", "SX116", "SX119", "SX120", "SX121"]
    parameters = (
        r"C:\Users\alexander.lepauvre\Documents\GitHub\Reconstructed_time_analysis\eye_tracker"
        r"\03-pupil_amplitude_parameters.json ")
    pupil_amplitude(parameters, subjects_list)
