import sys, os
sys.path.append(os.getcwd())

from brian2 import *
from heterosynaptic_plasticity_sim.fig3.util.model_fig1c import *
import matplotlib.pyplot as plt

# dt adjustment
defaultclock.dt = 2.5 * ms

#Patterns
stet_pattern = np.tile(np.concatenate(([100], np.zeros(600))), 3)
slfs_pattern = np.tile([20.0, 20.0, 20.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 900)
wtet_pattern = [100, 0]
wlfs_pattern = [8, 0] # Adjusted to 6 because the original value (1) doesn't work for some reason.

# Stimulation protocols
WTET1_stim = TimedArray(np.concatenate((np.zeros(int(3600 * second / (0.1 * second))) , wtet_pattern)) * Hz, 0.1 * second)
STET_stim = TimedArray(stet_pattern * Hz, 1 * second)
SLFS_stim = TimedArray(slfs_pattern * Hz, 50 * ms)
WLFS_stim = TimedArray(wlfs_pattern * Hz, 900 * second)
WTET2_stim = TimedArray(np.concatenate((np.zeros(int(3600 * second / (0.2 * second))) , wtet_pattern)) * Hz, 0.2 * second)

STIM_PROTOCOL_S1 = 'WLFS'
STIM_PROTOCOL_S2 = 'SLFS'

if STIM_PROTOCOL_S1 == 'WTET1' and STIM_PROTOCOL_S2 == 'STET':
    title = 'non_tagged ELTP'
if STIM_PROTOCOL_S1 == 'WTET2' and STIM_PROTOCOL_S2 == 'STET':
    title = 'tagged ELTP'

# Poisson Group that stimulates according to stimulus protocol.
P_1 = PoissonGroup(25, rates=f'{STIM_PROTOCOL_S1}_stim(t)')
P_2 = PoissonGroup(25, rates=f'{STIM_PROTOCOL_S2}_stim(t)')

# Input neuron group
In = NeuronGroup(2, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')
In2 = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')

# Single neuron
Out = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')
Out2 = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')

# Input synapses
IS_1 = Synapses(source=P_1,
                target=In,
                model=""" dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)
                        tsc1_post = syn_current : amp (summed)
                        w = h_0 : coulomb                                           """,
                on_pre='syn_current += w/second',
                method='heun')
IS_1.connect(j='0')

IS_2 = Synapses(source=P_2,
                target=In,
                model=""" dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)
                        tsc2_post = syn_current : amp (summed)
                        w = h_0 : coulomb                                           """,
                on_pre='syn_current += w/second',
                method='heun')
IS_2.connect(j='1')

IS_3 = Synapses(source=P_1,
                target=In2,
                model=""" dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)
                        tsc2_post = syn_current : amp (summed)
                        w = h_0 : coulomb                                           """,
                on_pre='syn_current += w/second',
                method='heun')
IS_3.connect()

# Single synapse
S = Synapses(In, Out, model=syn_model_1, on_pre=on_pre_model, on_post=on_post_model, method='heun')
S.connect(j='0')
S2 = Synapses(In2, Out2, model=syn_model_1, on_pre=on_pre_model, on_post=on_post_model, method='heun')
S2.connect()

# Set delays
IS_1.delay = Params.tau_ax_delay
IS_2.delay = Params.tau_ax_delay

S.pre_0.delay = Params.tau_ax_delay
S.pre_1.delay = Params.t_c_delay

# Set distances
S.distance = [abs(j - i) for i in range(In.N) for j in range(Out.N)]

# Set sigma_diffs
S.sigma_diff = 7    # One of the defaults used in the article.

# Set initial h value
S.h = Params.h_0

S2.pre_0.delay = Params.tau_ax_delay
S2.pre_1.delay = Params.t_c_delay

# Set distances
S2.distance = 0

# Set sigma_diffs
S2.sigma_diff = 7    # One of the defaults used in the article.

# Set initial h value
S2.h = Params.h_0

# Set namespaces
set_namespace_of(P_1, IS_1)
set_namespace_of(P_2, IS_2)
set_namespace_of(None, IS_3)
set_namespace_of(In, S)
set_namespace_of(In2, S2)
set_namespace_of(Out)
set_namespace_of(Out2)

# Monitor
M = StateMonitor(S, 'w', record=True)
M2 = StateMonitor(S2, 'w', record=True)

#Run for 8 hours
run(8 * 60 * 60 * second, report='text')

# Plot results
plt.figure(figsize=(25, 7))
plt.subplot(1, 2, 1)
plt.plot(M2.t / (60 * 60 * second) , M2.w[0]/Params.h_0, color='blue', label=f'S1:{STIM_PROTOCOL_S1}')
plt.xlabel('Zaman (saat)')
plt.ylabel('W/h_0')
plt.ylim(0, 2.5)
plt.legend(loc='best')
plt.subplot(1, 2, 2)
plt.plot(M.t / (60 * 60 * second) , M.w[0]/Params.h_0, color='blue', label=f'S1:{STIM_PROTOCOL_S1}')
plt.plot(M.t / (60 * 60 * second) , M.w[1]/Params.h_0, color='red', label=f'S2:{STIM_PROTOCOL_S2}')
plt.xlabel('Zaman (saat)')
plt.ylabel('')
plt.ylim(0, 2.5)
plt.legend(loc='best')
plt.suptitle(title)
current_time = datetime.datetime.now().strftime("%m%d%Y_%H%M")
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL_S1 + '-' + STIM_PROTOCOL_S2)
if not os.path.exists(directory):
    os.makedirs(directory)
figure_path = os.path.join(directory, f'{current_time}.png')
plt.savefig(figure_path)