#! /usr/bin/env python
# -*- coding: utf-8 -*-

import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import matplotlib.pyplot as plt
import pickle as pk


LS_MODELS = ("Gaussian", "Voigt", "Doniach-Sunjic")
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

c1, _, c2, _, c3 = st.beta_columns((1, 0.1, 1, 0.1, 4))

with c1:
    st.header("Fitting directives")
    files = st.file_uploader("Upload data")
    print(dir(files))
    if files is None:
        pass
    else:
        with open(files.read(), 'rb') as f_pkl:
            res = pk.load(f_pkl)


    inits = st.file_uploader("Initial conditions")
    if inits is None:
        pass
    else:
        pass

    numpeak_selected = st.selectbox("Number of lineshape components", tuple(range(1, 21)))
    peak_func = st.selectbox("Lineshape function", LS_MODELS)
    numbg_selected = st.selectbox("Number of background components", (0, 1, 2))
    bg_func = st.selectbox("Background function", ("Gaussian", "Exponential", "Constant"))

with c2:
    st.header("Fitting panel")
    isfit = st.button("Run fit", key="fitButton")
    issave = st.button("Save fit", key="saveButton")
    # with st.beta_container():
    # Generate lineshape component parameter widgets
    for i in range(1, numpeak_selected+1):
        ls_params = LS_PARAMS[peak_func]
        with st.beta_expander(ls_preftext + str(i) + " " + peak_func):
            for lsp in ls_params:
                st.slider(ls_preftext + str(i) + "_" + lsp)

    # Generate background parameter widgets
    if numbg_selected > 0:
        bg_params = BG_PARAMS[bg_func]
        with st.beta_expander(bg_preftext + str(i) + " " + bg_func):
            for bgp in bg_params:
                st.slider(bg_preftext + str(i) + "_" + bgp)

with c3:
    st.header('Display panel')
    f, ax = plt.subplots()
    st.pyplot(f)
