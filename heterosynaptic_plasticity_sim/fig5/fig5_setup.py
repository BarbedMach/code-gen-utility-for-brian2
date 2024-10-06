from code_gen_util.CPP_Generator import CPP_Generator
from brian2 import *
from matplotlib import pyplot as plt
import os
from heterosynaptic_plasticity_sim.fig5.util.model import *

# Simulation specific parameters:
N_stimulated_syn = 20
defaultclock.dt = 2.5 * ms

# Instantiate CPP code generation module.
cpp_generator = CPP_Generator()

# Code generation target:
cpp_target = "generated_code.hpp"

# Set Brian2 to cpp mode and use c++20 standard.
set_device("cpp_standalone")
prefs.codegen.cpp.extra_compile_args_msvc = ['-std:c++20']

# Add extra headers that will be used in the simulation.
cpp_generator.add_header("cmath")

# Declare globally used variables.
c_diff = 0.7
cpp_generator.new_constant("double", "c_diff", c_diff)

sigma_diff = 7
cpp_generator.new_constant("int", "sigma_diff", sigma_diff)

# Calcium is held outside to be able to implement heterosynaptic plasticity.
calcium_array_size = N_stimulated_syn + 1
cpp_generator.new_array1d("calcium_array", calcium_array_size, 0.0)

# Define the functions to be injected.
cpp_generator.add_cpp_func(
    "double _get_val(int idx) {"
    "   return calcium_array[idx];"
    "}"
)

cpp_generator.add_cpp_func(
    "double _set_val(int idx, double val) {"
    "   calcium_array[idx] = val;"
    "   return val;"
    "}"
)

cpp_generator.add_cpp_func(
    "double _exp_dcy(int idx, double decay_rate, double dt) {"
    "   calcium_array[idx] -= calcium_array[idx] * decay_rate * dt;"
    "   return calcium_array[idx];"
    "}"
)

cpp_generator.add_cpp_func(
    "double _inc_val(int idx, double increment_val) {"
    "   calcium_array[idx] += increment_val;"
    "   return calcium_array[idx];"
    "}"
)

cpp_generator.add_cpp_func(
    "double _heterosynaptic_plasticity(int idx) {"
    f"   for (int i = 0; i < {calcium_array_size}; ++i) {{"
    "       double distance = abs(idx - i);"
    "       double effect_magnitude = c_diff * exp(-(distance * distance)/(sigma_diff * sigma_diff));"
    "       double effect = effect_magnitude * (calcium_array[idx] - calcium_array[i]);"
    "       calcium_array[idx] -= effect;"
    "       calcium_array[i] += effect;"
    "   }"
    "   return calcium_array[idx];"
    "}"
)

# Generate the file
cpp_generator.generate(cpp_target)

# Insert destructor call, currently not working properly (minor issue)
# device.insert_code('after_end', cpp_generator.generate_delete_call())

# Bind the added functions with implementations.


@implementation("cpp",
f'''
#include "{cpp_target}"
double get_val(int idx) {{
    return _get_val(idx);
}}''', include_dirs=[os.getcwd()])
@check_units(result=1)
def get_val(idx):
    pass


@implementation("cpp",
f'''
#include "{cpp_target}"
double set_val(int idx, double val) {{
    return _set_val(idx, val);
}}''', include_dirs=[os.getcwd()])
@check_units(result=1)
def set_val(idx, val):
    pass


@implementation("cpp",
f'''#include "{cpp_target}"
double exp_dcy(int idx, double decay_rate, double dt) {{
    return _exp_dcy(idx, decay_rate, dt);
}}''', include_dirs=[os.getcwd()])
@check_units(result=1)
def exp_dcy(idx, decay_rate, dt):
    pass


@implementation("cpp",
f'''#include "{cpp_target}"
double inc_val(int idx, double inc_val) {{
  return _inc_val(idx, inc_val);
}}''', include_dirs=[os.getcwd()])
@check_units(result=1)
def inc_val(idx, inc_val):
    pass


@implementation("cpp",
f'''#include "{cpp_target}"
double heterosynaptic_plasticity(int idx) {{
    return _heterosynaptic_plasticity(idx);
}}''', include_dirs=[os.getcwd()])
@check_units(result=1)
def heterosynaptic_plasticity(idx):
    pass


SLFS_stim = TimedArray(np.tile([20.0, 20.0, 20.0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 900) * Hz, 50 * ms)
STET_stim = TimedArray(np.tile(np.concatenate(([100], np.zeros(600))), 3) * Hz, 1 * second)
WLFS_stim = TimedArray([1, 0] * Hz, 900 * second)
WTET_stim = TimedArray([100, 0] * Hz, 0.2 * second)

STIM_PROTOCOL = 'STET'

P = PoissonGroup(25, rates=f'{STIM_PROTOCOL}_stim(t)')

I = NeuronGroup(N_stimulated_syn + 1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')


NG = NeuronGroup(1, model=ng_model, threshold=ng_thr, reset=ng_rst, refractory=Params.t_ref, method='euler')

IS = Synapses(source=P,
              target=I,
              model=""" dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)
                        total_syn_current_post = syn_current : amp (summed)
                        w = h_0 : coulomb                                           """,
              on_pre='syn_current += w/second',
              method='heun')
IS.connect(f'j!={N_stimulated_syn}')

HS = Synapses(source=I
              , target=NG
              , model= syn_model + f"""
              dummy : 1
              c = set_val(i, exp_dcy(i, 3.5, dt)) : 1
              """,
              on_pre={'pre_0': "syn_current += w/second", 'pre_1': "dummy = inc_val(i, c_pre)"},
              on_post=f"""
              dummy = inc_val(i, c_post) + heterosynaptic_plasticity(i)
              """
              )
HS.connect()

IS.delay = Params.tau_ax_delay

HS.pre_0.delay = Params.tau_ax_delay
HS.pre_1.delay = Params.t_c_delay

HS.h = Params.h_0

set_namespace_of(P, IS)
set_namespace_of(NG, HS)
set_namespace_of(I)

M = StateMonitor(HS, ['h', 'w', 'z', 'c'], record=[0, N_stimulated_syn])
PM = StateMonitor(NG, 'p', record=True)

run(1 * 60 * 60 * second, report='text')


plt.figure(figsize=(25, 7))
plt.plot(M.t / (60 * 60 * second) , M.w[0]/Params.h_0, color='blue', label=f'Stimulated synapse')
plt.plot(M.t / (60 * 60 * second) , M.w[1]/Params.h_0, color='red', label=f'Unstimulated synapse')
plt.xlabel('Time (h)')
plt.ylabel('W/W_0')
plt.legend(loc='best')
current_time = datetime.datetime.now().strftime("%m%d%Y_%H%M")
directory = os.path.join(os.getcwd(), 'figures')
if not os.path.exists(directory):
    os.makedirs(directory)
figure_path = os.path.join(directory, f'{current_time}.png')
plt.savefig(figure_path)





