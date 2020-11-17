#! /usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import pickle as pk
import pesfit as pf
import ast

import sys
sys.path.append("lineweaver")
import utils as u


LS_MODELS = ("Voigt", "Gaussian", "Doniach-Sunjic")
LS_PARAMS = {"Gaussian":("Amplitude", "Center", "Sigma"),
            "Voigt":("Amplitude", "Center", "Sigma", "Gamma"),
            "Doniach-Sunjic":("Amplitude", "Center")}
BG_PARAMS = {"Gaussian":("Amplitude", "Center", "Sigma"),
            "Exponential":("Amplitude", "Decay"),
            "Constant":("Constant")}

ls_preftext = "lp"
bg_preftext = "bg"


st.set_page_config(layout="wide")
# st.write("""<div align="center">
#             Multicomponent spectrum annotator
#         </div>""")

st.write("""
        # Multicomponent spectrum annotator
        ##### @author: R. Patrick Xian
        """)

data, inits = [], []
c1, _, c2, _, c3, _, c4 = st.beta_columns((1.2, 0.08, 1, 0.08, 4, 0.08, 1))

with c1: # Column 1
    st.header("Fitting directives")
    
    # File loading (returns None if no file has been loaded)
    fdata = st.file_uploader("Upload data")
    if fdata is None:
        xdat = np.arange(0, 1, 0.01)
        ydat = np.sinc(xdat)
    else:
        data = list(ast.literal_eval(fdata.read().decode("utf-8")))
        xdat, ydat = data["xdata"], data["ydata"]

    finits = st.file_uploader("Initial conditions")
    if finits is None:
        numpeak = st.selectbox("Number of lineshape components", tuple(range(1, 21)), key="sb_numpeak")
        peak_func = st.selectbox("Lineshape function", LS_MODELS, key="sb_peakfunc")
        numbg = st.selectbox("Number of background components", (0, 1, 2), key="sb_numbg")
        bg_func = st.selectbox("Background function", ("Gaussian", "Exponential", "Constant"), key="sb_bgfunc")
    else:
        inits = list(ast.literal_eval(finits.read().decode("utf-8")))
        n_inits = len(inits)

        keys = [list(dct.keys())[0] for dct in inits]
        n_bg = int(np.sum([bg_preftext in k for k in keys]))
        n_ls = int(np.sum([ls_preftext in k for k in keys]))

        numpeak = st.selectbox("Number of lineshape components", tuple(range(1, 21)), index=n_ls-1, key="sb_numpeak")
        peak_func = st.selectbox("Lineshape function", LS_MODELS, key="sb_peakfunc")
        numbg = st.selectbox("Number of background components", (0, 1, 2), index=n_bg-1, key="sb_numbg")
        bg_func = st.selectbox("Background function", ("Gaussian", "Exponential", "Constant"), key="sb_bgfunc")

    # Build spectrum model
    if numbg == 0:
        specbg = 'None'
    else:
        specbg = bg_func
    mdl = pf.fitter.model_generator(peaks={peak_func:numpeak}, background=specbg)
    pars = mdl.make_params()
    # print(mdl)


with c2: # Column 2
    st.header("Parameter tuner")

    if len(inits) == 0:
        # Generate lineshape component parameter widgets
        for i in range(1, numpeak+1):
            ls_params = LS_PARAMS[peak_func]
            lsstr = ls_preftext + str(i)
            lspref = lsstr + "_"
            with st.beta_expander(lsstr + " " + peak_func):
                for lsp in ls_params:
                    st.slider(lspref + lsp)

        # Generate background component parameter widgets
        if numbg > 0:
            bg_params = BG_PARAMS[bg_func]
            with st.beta_expander(bg_preftext + str(i) + " " + bg_func):
                for bgp in bg_params:
                    st.slider(bg_preftext + str(i) + "_" + bgp)

    else:
        # Update lineshape component parameter widgets
        for i in range(1, numpeak+1):
            ls_params = LS_PARAMS[peak_func]
            lsstr = ls_preftext + str(i)
            lspref = lsstr + "_"
            pos = np.argwhere([lspref in k for k in keys])
            idx = pos.item()
            cndts = inits[idx][lspref]
            with st.beta_expander(lsstr + " " + peak_func):
                for lsp in ls_params:
                    lspdict = dict(cndts[lsp.lower()])
                    vmin = u.cvfloat(lspdict.pop("min", None))
                    vmax = u.cvfloat(lspdict.pop("max", None))
                    val = u.cvfloat(lspdict.pop("value", None))
                    vary = lspdict.pop("vary", True)
                    st.slider(lspref + lsp, min_value=vmin, max_value=vmax, value=None)

        # Update background component parameter widgets
        if numbg > 0:
            bg_params = BG_PARAMS[bg_func]
            with st.beta_expander(bg_preftext + str(i) + " " + bg_func):
                for bgp in bg_params:
                    st.slider(bg_preftext + str(i) + "_" + bgp)

        xdat = np.arange(0.65, -8, -0.017595)
        pf.fitter.varsetter(pars, inits[1:], ret=False)
        initall = mdl.eval(x=xdat, params=pars)
        initcomp = mdl.eval_components(x=xdat, params=pars)


with c3: # Column 3
    st.header("Display panel")
    renderer = st.selectbox("Rendering tool", ("matplotlib", "bokeh", "altair"))
    
    if renderer == "matplotlib":
        f, ax = plt.subplots(figsize=(10, 6))
        ax.axvline(x=0.5, ls='--')

        if len(inits) == 0:
            pass
        else:
            for k, v in initcomp.items():
                ax.plot(xdat, v)
            ax.plot(xdat, initall, c='g')
            ax.set_xlim([min(xdat), max(xdat)])
            ax.set_xlabel('Energy (eV)', fontsize=15)
            ax.set_ylabel("Normalized intensity (a.u.)", fontsize=15)

        st.pyplot(f)

    elif renderer == "bokeh":
        pass

    elif renderer == "ältair":
        pass


with c4: # Column 4
    st.header("Fitting panel")
    isfit = st.button("Run fit", key="fitButton")
    issave = st.button("Save fit", key="saveButton")
    isclear = st.button("Refresh", key="refreshButton")
    
    # If the "Run fit" button is pressed, run the optimization algorithm
    if isfit:
        out = pf.fitter.pointwise_fitting(xdat, ydat, model=mdl, params=pars, jitter_init=False,
                                  shifts=np.arange(-0.08, 0.09, 0.01), verbose=True, ynorm=True)

    # if the "Save fit" button is pressed, output file
    if issave:
        pass

    # if the "Refresh" button is pressed, switch to the initialization
    if isclear:
        pass