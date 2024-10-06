import sys, os
sys.path.append(os.getcwd())

from heterosynaptic_plasticity_sim.util.parameters import Params

ng_model = """
total_syn_current : amp

dV/dt = (V_rev - V + R*(total_syn_current + I_bg))/tau_mem : volt

dI_bg/dt = (I_0 - I_bg + sigma_wn*xi_bg)/tau_syn : amp

ep_w_change : coulomb

dp/dt = (-p + alpha * int(ep_w_change > theta_pro))/tau_p : 1
"""

syn_model = """
dsyn_current/dt = -syn_current/tau_syn : amp (clock-driven)

total_syn_current_post = syn_current : amp (summed)

w = h + (h_0 * z) : coulomb

ksi = sqrt(tau_h*(int(c > theta_p) + int(c > theta_d))) * sigma_pl : coulomb * second

dc/dt = -c/tau_c : 1 (clock-driven)

dh/dt = (0.1*(h_0 - h) + upsilon_p *(1 * ncoulomb - h) * int(c > theta_p) - upsilon_d*h*int(c > theta_d) + ksi*xi/(sqrt(1*second)))/tau_h : coulomb (clock-driven)

dz/dt = (p_post*(1 - z)*int((h - h_0) > theta_tag) -p_post*(z + 0.5)*int((h_0 - h) > theta_tag))/tau_z : 1 (clock-driven)

ep_w_change_post = abs(h - h_0) : coulomb (summed) 

sigma_diff : 1

distance : 1
"""

on_pre_model = {'pre_0': "syn_current += w/second", 'pre_1': "c += c_pre"}

on_post_model = """
c += c_post * int(exp(-(distance/sigma_diff) * (distance/sigma_diff)) > rand())
"""

ng_rst = """
V = V_res
"""

ng_thr = 'V > V_th'


def set_namespace_of(ng=None, s=None, params=None):
    if params is None:
        params = Params()

    if ng is not None:
        ng.namespace['tau_mem'] = params.tau_mem
        ng.namespace['V_rev'] = params.V_rev
        ng.namespace['R'] = params.R
        ng.namespace['V_th'] = params.V_th
        ng.namespace['V_res'] = params.V_reset
        ng.namespace['I_0'] = params.I_0
        ng.namespace['sigma_wn'] = params.sigma_wn
        ng.namespace['tau_syn'] = params.tau_syn
        ng.namespace['alpha'] = params.alpha
        ng.namespace['theta_pro'] = params.theta_pro
        ng.namespace['tau_p'] = params.tau_p
        ng.namespace['w_stim'] = params.w_stim
        ng.namespace['N_stim'] = params.N_stim

    if s is not None:
        s.namespace['tau_syn'] = params.tau_syn
        s.namespace['h_0'] = params.h_0
        s.namespace['tau_h'] = params.tau_h
        s.namespace['theta_p'] = params.theta_p
        s.namespace['theta_d'] = params.theta_d
        s.namespace['sigma_pl'] = params.sigma_pl
        s.namespace['upsilon_d'] = params.upsilon_d
        s.namespace['upsilon_p'] = params.upsilon_p
        s.namespace['tau_c'] = params.tau_c
        s.namespace['c_pre'] = params.c_pre
        s.namespace['c_post'] = params.c_post
        s.namespace['theta_tag'] = params.theta_tag
        s.namespace['tau_z'] = params.tau_z
