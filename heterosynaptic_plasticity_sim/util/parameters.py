import sys, os
sys.path.append(os.getcwd())

from brian2 import *
from dataclasses import dataclass
@dataclass
class Params:
    delta_t = 0.2 * ms  # Duration of timestep for numerical computation.
    tau_mem = 10 * ms  # Membrane time constant.
    tau_syn = 5 * ms  # Synaptic time constant, also for external background current.
    tau_ax_delay = 3 * ms  # Axonal spike delay.
    t_ref = 2 * ms  # Duration of refractory period.
    R = 10 * Mohm  # Membrane resistance.
    V_rev = -65 * mV  # Reversal (equilibrium) potential.
    V_reset = -70 * mV  # Reset potential.
    V_th = -55 * mV  # Threshold potential for spiking.
    sigma_wn = 0.05 * nA * sqrt(second)  # Standard deviation for Gaussian noise
    # in external background current.
    I_0 = 0.15 * nA  # Mean of the external background current.
    N_e = 1600  # Number of excitatory neurons.
    N_i = 400  # Number of inhibitory neurons.

    p_c = 0.1  # Probability of a connection existing between two neurons.
    h_0 = 0.420075 * ncoulomb  # Initial excitatory -> excitatory coupling strength.
    w_ei = 2 * h_0  # Excitatory -> inhibitory coupling strength.
    w_ie = 4 * h_0  # Inhibitory -> excitatory coupling strength.
    w_ii = 4 * h_0  # Inhibitory -> inhibitory coupling strength.
    w_stim = h_0  # Coupling strength of synapses from putative input neurons.
    N_stim = 25  # Number of putative input neurons for stimulation.
    f_stim = 100 * Hz  # Frequency of learning/recall stimulation from putative input neurons.
    r = 0.5  # Fraction of assembly neurons that are stimulated to trigger recall.

    t_c_delay = 0.0188 * second  # Delay of postsynaptic calcium influx after presynaptic spike.
    c_pre = 0.6  # Presynaptic calcium contribution (0.6 for network adjustment).
    c_post = 0.1655  # Postsynaptic calcium contribution (0.1655 for network adjustment).
    tau_c = 0.0488 * second  # Calcium time constant.
    tau_h = 688.4 * second  # Early-phase time constant.
    tau_p = 60 * 60 * second  # Protein time constant. (60 min)
    tau_z = 60 * 60 * second  # Late-phase time constant. (60 min)
    upsilon_p = 1645.6  # Potentiation rate.
    upsilon_d = 313.1  # Depression rate.
    theta_p = 3  # Calcium threshold for potentiation.
    theta_d = 1.2  # Calcium threshold for depression.
    sigma_pl = 0.290436 * ncoulomb * sqrt(second)  # Standart deviation for plasticity fluctiations.
    alpha = 1  # Protein synthesis rate.
    theta_pro = 0.210037 * ncoulomb  # Protein synthesis threshold.
    theta_tag = 0.0840149 * ncoulomb  # Tagging threshold.