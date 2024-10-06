import sys, os
sys.path.append(os.getcwd())

from brian2 import *
from heterosynaptic_plasticity_sim.util.parameters import Params
from heterosynaptic_plasticity_sim.util.model import ng_model, syn_model, on_post_model, ng_rst, ng_thr, on_pre_model, set_namespace_of
import matplotlib.pyplot as plt

#dt adjustment
defaultclock.dt = 2.5 * ms

#Stimulation protocols
SLFS_stim = TimedArray(np.tile([20.0, 20.0, 20.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 900) * Hz, 50 * ms)
STET_stim = TimedArray(np.tile(np.concatenate(([100], np.zeros(600))), 3) * Hz, 1 * second)
WLFS_stim = TimedArray([5, 0] * Hz, 900 * second) # KONTROL EDILECEK
WTET_stim = TimedArray([100, 0] * Hz, 0.2 * second)

STIM_PROTOCOL = 'WLFS'

if STIM_PROTOCOL == 'SLFS':
    title = 'LLTD'
if STIM_PROTOCOL == 'WLFS':
    title = 'ELTD'
if STIM_PROTOCOL == 'WTET':
    title = 'ELTP'
if STIM_PROTOCOL == 'STET':
    title = 'LLTP'

if STIM_PROTOCOL == 'WTET' or STIM_PROTOCOL == 'STET':
    h_lines_above_one = True
if STIM_PROTOCOL == 'SLFS' or STIM_PROTOCOL == 'WLFS':
    h_lines_above_one = False

#Poisson Group that stimulates according to stimulus protocol.
P = PoissonGroup(25, rates=f'{STIM_PROTOCOL}_stim(t)')

I = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')

#Single neuron
NG = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')

#Input synapses
IS = Synapses(source=P,
              target=I,
              model=""" dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)
                        total_syn_current_post = syn_current : amp (summed)
                        w = h_0 : coulomb                                           """,
              on_pre='syn_current += w/second',
              method='heun')
IS.connect(j='0')

#Single synapse
S = Synapses(I, NG, model=syn_model, on_pre=on_pre_model, on_post=on_post_model, method='heun')
S.connect()

#Set delays
IS.delay = Params.tau_ax_delay

S.pre_0.delay = Params.tau_ax_delay
S.pre_1.delay = Params.t_c_delay

#Set distances
S.distance = 0      #Only one synapse

#Set sigma_diffs
S.sigma_diff = 1    #Irrelevant, to avoid division by 0 it is 1.

#Set initial h value
S.h = Params.h_0

#Set namespaces
set_namespace_of(NG, IS)
set_namespace_of(P, S)
set_namespace_of(I)

#Monitor
M = StateMonitor(S, ['h', 'w', 'z', 'c'], record=True)
PM = StateMonitor(NG, ['p', 'V', 'I_bg'], record=True)
IM = StateMonitor(I, ['p', 'V', 'I_bg'], record=True)
SM = SpikeMonitor(P, record=True)

#Run for 8 hours
run(8 * 60 * 60 * second, report='text')

#Plot results
plt.figure(figsize=(22, 9))
# plt.subplot(2, 1, 1)
plt.title(title)
plt.plot(M.t / (60 * 60 * second), M.w[0]/Params.h_0, color='red', label='W/h_0 (Toplam)')
plt.plot(M.t / (60 * 60 * second), M.h[0]/Params.h_0, color='blue', label='h/h_0 (Erken Aşama)')
plt.plot(M.t / (60 * 60 * second), 1 + M.z[0], color='m', label='1 + Z (Geç Aşama)')
if h_lines_above_one:
    plt.axhline(y=(1 + Params.theta_pro / Params.h_0), color='black', label='1 + theta_pro/p_0', linestyle='dashed')
    plt.axhline(y=(1 + Params.theta_tag / Params.h_0), color='black', label='1 + theta_tag/p_0', linestyle='dashed')
else:
    plt.axhline(y=(1 - Params.theta_pro/Params.h_0), color='black', label='1 - theta_pro/p_0', linestyle='dashed')
    plt.axhline(y=(1 - Params.theta_tag/Params.h_0), color='black', label='1 - theta_tag/p_0', linestyle='dashed')
plt.xlabel('Zaman (saat)')
plt.ylabel('')
plt.legend()
"""
plt.subplot(2, 1, 2)
plt.plot(M.t / (60 * 60 * second), M.z[0], color='green', label='Z')
plt.plot(PM.t / (60 * 60 * second), PM.p[0], color='purple', label='protein')
plt.xlabel('Zaman (saat)')
plt.ylabel('')
plt.legend()
"""
current_time = datetime.datetime.now().strftime("%m%d%Y_%H%M")
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL, f'{STIM_PROTOCOL}_{current_time}')
if not os.path.exists(directory):
    os.makedirs(directory)
figure_path = os.path.join(directory, f'{STIM_PROTOCOL}_Fig1B_andFig2.png')
plt.savefig(figure_path)
"""
# CREATE FOLDER FOR SYNAPSE PARAMETERS
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL, f'{STIM_PROTOCOL}_{current_time}', 'synapse')
if not os.path.exists(directory):
    os.makedirs(directory)

# SEPERATE PLOTS FOR SYNAPSE PARAMETERS START
plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(M.t / (60 * 60 * second), M.c[0], color='m', label='Calcium')
plt.xlabel('Time (h)')
plt.ylabel('Calcium (unit= 1)')
plt.grid()
plt.legend()
plt.savefig(f"{directory}/calcium.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(M.t / (60 * 60 * second), M.h[0]/Params.h_0, color='m', label='Early Phase Weight')
plt.xlabel('Time (h)')
plt.ylabel('Early Phase Weight')
plt.grid()
plt.legend()
plt.savefig(f"{directory}/early_phase_weight.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(M.t / (60 * 60 * second), M.z[0], color='m', label='Late Phase Weight')
plt.xlabel('Time (h)')
plt.ylabel('Late Phase Weight')
plt.grid()
plt.legend()
plt.savefig(f"{directory}/late_phase_weight.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(M.t / (60 * 60 * second), M.w[0]/Params.h_0, color='m', label='Total Weight')
plt.xlabel('Time (h)')
plt.ylabel('Total Weight')
plt.grid()
plt.legend()
plt.savefig(f"{directory}/late_phase_weight.png")
# SEPERATE PLOTS FOR SYNAPSE PARAMETERS END

# CREATE FOLDER FOR POST NEURON PARAMETERS
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL, f'{STIM_PROTOCOL}_{current_time}', 'post_neuron')
if not os.path.exists(directory):
    os.makedirs(directory)

# SEPERATE PLOTS FOR POST NEURON PARAMETERS START
plt.figure(figsize=(22, 9))
plt.clf()
plt.plot(PM.t / (60 * 60 * second), PM.V[0] * 10**3, color='m', label='Membrane Potential')
plt.xlabel('Time (h)')
plt.ylabel('Membrane Potential for Post Neuron (unit mV)')
plt.grid()
plt.savefig(f"{directory}/post_neuron_voltage.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(PM.t / (60 * 60 * second), PM.I_bg[0] * 10**9, color='m', label='Background Current')
plt.xlabel('Time (h)')
plt.ylabel('Background Current for Post Neuron (unit nA)')
plt.grid()
plt.savefig(f"{directory}/post_background_current.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(PM.t / (60 * 60 * second), PM.p[0], color='m', label='Protein Amount')
plt.xlabel('Time (h)')
plt.ylabel('Protein Amount for Post Neuron (unit 1)')
plt.grid()
plt.savefig(f"{directory}/post_protein_amount.png")
# SEPERATE PLOTS FOR POST NEURON PARAMETERS END

# CREATE FOLDER FOR PRE NEURON PARAMETERS
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL, f'{STIM_PROTOCOL}_{current_time}', 'pre_neuron')
if not os.path.exists(directory):
    os.makedirs(directory)

# SEPERATE PLOTS FOR PRE NEURON PARAMETERS START
plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(IM.t / (60 * 60 * second), IM.V[0] * 10**3, color='m', label='Membrane Potential')
plt.xlabel('Time (h)')
plt.ylabel('Membrane Potential for Pre Neuron (unit mV)')
plt.grid()
plt.savefig(f"{directory}/pre_neuron_voltage.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(IM.t / (60 * 60 * second), IM.I_bg[0], color='m', label='Background Current')
plt.xlabel('Time (h)')
plt.ylabel('Background Current for Pre Neuron (unit nA)')
plt.grid()
plt.savefig(f"{directory}/pre_background_current.png")

plt.clf()
plt.figure(figsize=(22, 9))
plt.plot(IM.t / (60 * 60 * second), IM.p[0], color='m', label='Protein Amount')
plt.xlabel('Time (h)')
plt.ylabel('Protein Amount for Pre Neuron (unit 1)')
plt.grid()
plt.savefig(f"{directory}/pre_protein_amount.png")
# SEPERATE PLOTS FOR PRE NEURON PARAMETERS END


# CREATE FOLDER FOR SPIKE TIMES
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL, f'{STIM_PROTOCOL}_{current_time}', 'spike_times')
if not os.path.exists(directory):
    os.makedirs(directory)

# WRITE SPIKE TIMES TO A TEXT FILE
with open(f'{directory}/spike_times.txt', 'w') as file:
    for idx in range(len(SM.i)):
        file.write(f'{idx}. INDEX: {SM.i[idx]}, SPIKE TIME: {SM.t[idx]}\n')
"""