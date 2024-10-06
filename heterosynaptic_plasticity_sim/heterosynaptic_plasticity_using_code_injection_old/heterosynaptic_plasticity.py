from brian2 import *
import os
from heterosynaptic_plasticity_sim.heterosynaptic_plasticity_using_code_injection_old.util.model import *

set_device('cpp_standalone')
prefs.codegen.cpp.extra_compile_args_msvc = ['-std:c++20']

c_diff = 1
sigma_diff = 7
N_stimulated_syn = 50
calcium_table = [(N_stimulated_syn + 1)]

cpp_file_id = 'injected_code.hpp'

cpp_functions = '''
double new_array_in_table(double** table, int index, int size) {
    table[index] = new double[size];
    for (int i = 0; i < size; i++) {table[index][i] = 0.0;}
    return 0;
}
double exponential_decay(double input, double decay_rate, double dt) {
    return input * (1 - decay_rate * dt);
}
double heterosynaptic_plasticity_on_spike(int array_idx, int index, int size) {
    for (int i = 0; i < size; ++i) {
        double effect_magnitude = c_diff * exp(-(abs(index - i)/sigma_diff) * (abs(index - i)/sigma_diff));
        table[array_idx][index] += effect_magnitude;
        table[array_idx][i] -= effect_magnitude;
    }
    return table[array_idx][index];
}
double concentration_increment_on_spike(int array_idx, int index, double value) {
    table[array_idx][index] += value;
    return table[array_idx][index];
}
double get_value(int array_idx, int index) {
    return table[array_idx][index];
}
double _set_value(int array_idx, int index, double value) {
    table[array_idx][index] = value;
    return value;
}
'''


def init_array(_calcium_table):
    with open(cpp_file_id, 'w') as f:
        f.write("#pragma once\n")
        f.write('#include <iostream>\n')
        f.write('#include <string.h>\n')
        f.write('#include <windows.h>\n')
        f.write(f'static const double c_diff = {c_diff};\n')
        f.write(f'static const int sigma_diff = {sigma_diff};\n')
        f.write(f'static const LPVOID lpAddress = (LPVOID)0x00400000;\n')
        f.write(f'static const SIZE_T dwSize = sizeof(double*) * {len(calcium_table)};\n')
        f.write(f'static const DWORD flAllocationType = MEM_COMMIT | MEM_RESERVE;\n')
        f.write(f'static const DWORD flProtect = PAGE_READWRITE;\n')
        f.write(f'static inline double** table = nullptr;\n')
        f.write('int init_table() {\n')
        f.write('MEMORY_BASIC_INFORMATION memInfo;\n')
        f.write('SIZE_T result = VirtualQuery(lpAddress, &memInfo, sizeof(memInfo));\n')
        f.write('if (memInfo.State == MEM_FREE) {\n')
        f.write(f'LPVOID lpMemory = VirtualAlloc(lpAddress, dwSize, flAllocationType, flProtect);\n')
        f.write(f'table = (double**)lpMemory;\n')
        f.write('} else {\n')
        f.write(f'table = (double**)lpAddress;\n')
        f.write('};\n')
        f.write(f'      std::cout << table << std::endl;\n')
        for idx, item in enumerate(_calcium_table):
            f.write(f'  auto* ptr = new double[{item}];\n')
            f.write(f'  table[{idx}] = ptr;\n')
            f.write(f'  for (int i = 0; i < {item}; ++i) {{\n')
            f.write(f'      ptr[i] = 0.0;\n')
            f.write(f'  }}\n')
        f.write(f'  return 0;\n')
        f.write('}\n')
        f.write(cpp_functions + '\n')
        f.write('static inline int result = init_table();')


init_array(calcium_table)


@implementation('cpp', f'''
#include "{cpp_file_id}"
double apply_exp_dcy(int table_row, int index, double k, double h) {{
    table[table_row][index] = exponential_decay(table[table_row][index], k, h);
    return table[table_row][index];
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1, 1], result=1)
def apply_exp_dcy(array_index: int, index: int, k: float, h: float): return


@implementation('cpp', f'''
#include "{cpp_file_id}"
double exp_dcy(double input, double k, double h) {{
    return exponential_decay(input, k, h);
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1], result=1)
def exp_dcy(input: int, k: float, h: float): return


@implementation('cpp', f'''
double set_value(int table_row, int index, double value) {{
    _set_value(table_row, index, value);
    return value;
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1], result=1)
def set_value(array_index: int, index: int, value: float): return


@implementation('cpp', f"""
#include "{cpp_file_id}"
double hp_on_spike(int table_row, int index, int size) {{
    return heterosynaptic_plasticity_on_spike(table_row, index, size);
}}
""", include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1], result=1)
def hp_on_spike(array_index: int, index: int, size: int): return


@implementation('cpp', f'''
#include "{cpp_file_id}"
double pre_inc_on_spike(int table_row, int index, double incrementAmount) {{
    return concentration_increment_on_spike(table_row, index, incrementAmount);
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1], result=1)
def pre_inc_on_spike(array_index: int, index: int, incrementAmount: float): return

@implementation('cpp', f'''
#include "{cpp_file_id}"
double post_inc_on_spike(int table_row, int index, double incrementAmount) {{
    return concentration_increment_on_spike(table_row, index, incrementAmount);
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1, 1], result=1)
def post_inc_on_spike(array_index: int, index: int, incrementAmount: float): return


@implementation('cpp', f'''
#include "{cpp_file_id}"
double read_value(int table_row, int index) {{
    return get_value(table_row, index);
}}
''', include_dirs=[os.getcwd()])
@check_units(arg=[1, 1], result=1)
def read_value(array_index: int, index: int): return

defaultclock.dt = 2.5 * ms

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

decay_rate = 0.1

HS = Synapses(source=I
              , target=NG
              , model= syn_model + """
              dummy : 1
              c = set_value(0, i, exp_dcy(read_value(0, i), decay_rate, dt)) : 1
              ksi = sqrt(tau_h*(int(c > theta_p) + int(c > theta_d))) * sigma_pl : coulomb * second
              dh/dt = (0.1*(h_0 - h) + upsilon_p *(1 * ncoulomb - h) * int(c > theta_p) - upsilon_d*h*int(c > theta_d) + ksi*xi/(sqrt(1*second)))/tau_h : coulomb (clock-driven)
              """,
              on_pre={'pre_0': "syn_current += w/second", 'pre_1': "dummy = pre_inc_on_spike(0, i, c_pre)"},
              on_post=f"""
              dummy = post_inc_on_spike(0, i, c_post) + hp_on_spike(0, i, {calcium_table[0]})
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

M = StateMonitor(HS, ['h', 'w', 'z', 'c'], record=[0, 50])
PM = StateMonitor(NG, 'p', record=True)

run(1 * 60 * 60 * second, report='text')

plt.figure(figsize=(22, 9))

plt.subplot(1, 2, 1)
plt.title('Heterosynaptic Plasticity Fig5')
plt.plot(M.t / (60 * 60 * second), M.c[0], color='black', label="C.0")
plt.xlabel('Time (h)')
plt.ylabel('c')

plt.subplot(1, 2, 2)
plt.plot(M.t / (60 * 60 * second), M.c[1], color='red', label="C.50")
plt.xlabel('Time (h)')
plt.ylabel('c')

current_time = datetime.datetime.now().strftime("%m%d%Y_%H%M")
directory = os.path.join(os.getcwd(), 'figures', STIM_PROTOCOL)
if not os.path.exists(directory):
    os.makedirs(directory)
figure_path = os.path.join(directory, f'{STIM_PROTOCOL}_{current_time}.png')
plt.savefig(figure_path)














