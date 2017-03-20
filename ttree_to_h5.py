import ROOT
import numpy as np
import pandas
from pandas import HDFStore,DataFrame
from itertools import repeat

from imager import imager

# SIGNAL
def process_signal(rootfile):

    # Access to the Ttree and read it
    print 'Accessing to the Ttree and reading it...'; print ' '
    f = ROOT.TFile(rootfile)
    t = f.Get("tree")
    n = t.GetEntries()
    print n
    NEvents = []

    # Declaration of a list of the "kinematics-list"
    kinematics_variables_mult = 7
    list_gentopkin = [[] for i in repeat(None, kinematics_variables_mult-3)]
    list_fatjetkin = [[] for i in repeat(None, kinematics_variables_mult)]
    kinematics_gentop_branches = ['GenTop_pt', 'GenTop_eta', 'GenTop_phi', 'GenTop_mass']
    #kinematics_gentop_branches = ['GenTop_pt', 'GenTop_eta', 'GenTop_phi', 'GenTop_mass', 'GenTop_tau1', 'GenTop_tau2', 'GenTop_tau3']
    kinematics_fatjet_branches = ['FatJet_pt', 'FatJet_eta', 'FatJet_phi', 'FatJet_mass', 'FatJet_tau1', 'FatJet_tau2', 'FatJet_tau3']

    # Declaration of a list of the "pixels-list"
    npixels = 1600
    listpixels = [[] for i in repeat(None, npixels)]
    branches = []
    for col in range(0,npixels):
        branches.append('img_'+ str(col))

    counter = 0
    for i_evt in range(n):
        print counter
        t.GetEntry(i_evt)
    
        # Collect Kinematics info from GenTop
        n_GenTop = t.nGenTop
        n_jets =  t.nFatjetCA15ungroomed
        if n_jets==0:
            continue
        for gt in np.arange(n_GenTop):
            decay_mode = t.GenTop_status[gt]
            if decay_mode==0:
                continue
            pt = t.GenTop_pt[gt]
            eta = t.GenTop_eta[gt]
            phi = t.GenTop_phi[gt]
            m = t.GenTop_mass[gt]
            #tau1 = t.GenTop_tau1[i_jet]
            #tau2 = t.GenTop_tau2[i_jet]
            #tau3 = t.GenTop_tau3[i_jet]
            #gentop_listkin = [pt,eta,phi,m,tau1,tau2,tau3]
            gentop_listkin = [pt,eta,phi,m]
            gentopkin = ROOT.TLorentzVector()
            gentopkin.SetPtEtaPhiM(pt,eta,phi,m)

            for i_jet in np.arange(n_jets):
                # Collect Kinematics info from FatJet
                pt_fatjet = t.FatjetCA15ungroomed_pt[i_jet]
                eta_fatjet = t.FatjetCA15ungroomed_eta[i_jet]
                phi_fatjet = t.FatjetCA15ungroomed_phi[i_jet]
                m_fatjet = t.FatjetCA15ungroomed_mass[i_jet]
                tau1_fatjet = t.FatjetCA15ungroomed_tau1[i_jet]
                tau2_fatjet = t.FatjetCA15ungroomed_tau2[i_jet]
                tau3_fatjet = t.FatjetCA15ungroomed_tau3[i_jet]
                fatjet_listkin = [pt_fatjet,eta_fatjet,phi_fatjet,m_fatjet,tau1_fatjet,tau2_fatjet,tau3_fatjet]
                fatjetkin = ROOT.TLorentzVector()
                fatjetkin.SetPtEtaPhiM(pt_fatjet,eta_fatjet,phi_fatjet,m_fatjet)
        
                # Calculate Delta_R
                Delta_R = gentopkin.DeltaR(fatjetkin)
                if Delta_R<1.0:
            
                    for var in range(0,kinematics_variables_mult):
                        list_fatjetkin[var].append(fatjet_listkin[var])
                    for var in range(0,kinematics_variables_mult-3):
                        list_gentopkin[var].append(gentop_listkin[var])
            
                    NEvents.append(counter)
                    counter = counter+1
                    for px in range(0,1600):
                        pixel = getattr(t,'FatjetCA15ungroomed_img_'+ str(px))[i_jet]
                        listpixels[px].append(pixel)

    # Check that all the columns have the same size
    print 'Checking the size of the columns...'
    size_NEvents = len(NEvents)
    size_pixels_columns = len(listpixels[500])
    size_kinematics_columsn = len(list_gentopkin[0])
    print size_NEvents, size_pixels_columns, len(branches), size_kinematics_columsn

    # Store the information into an .h5 file
    print 'Saving the columns into an .h5 file...'
    arrays = []
    arrays.append(NEvents)

    # Add a random column for "is_signal_new"
    is_signal_new = [1]*size_NEvents

    df = pandas.DataFrame(NEvents, columns=['entries'])
    for n in range(0,kinematics_variables_mult-3):
        df[kinematics_gentop_branches[n]] = list_gentopkin[n]
    for n in range(0,kinematics_variables_mult):
        df[kinematics_fatjet_branches[n]] = list_fatjetkin[n]
    df['is_signal_new'] = is_signal_new
    for n in range(0,len(branches)):
        df[branches[n]] = listpixels[n]

    outputname = 'toptable.h5'
    #outputname = rootfile.split('.root')
    #outputname = outputname[0] + '.h5'
    df.to_hdf(outputname,'table', append=True, clobber=True)

    # Call the imager
    #imager(outputname,1)

# --------------------------------------------------------------- #
# BKG
def process_bkg(rootfile):
    
    # Access to the Ttree and read it
    print 'Accessing to the Ttree and reading it...'; print ' '
    f = ROOT.TFile(rootfile)
    t = f.Get("tree")
    n = t.GetEntries()
    print n
    NEvents = []
    
    # Declaration of a list of the "kinematics-list"
    kinematics_variables_mult = 7
    list_fatjetkin = [[] for i in repeat(None, kinematics_variables_mult)]
    kinematics_fatjet_branches = ['FatJet_pt', 'FatJet_eta', 'FatJet_phi', 'FatJet_mass', 'FatJet_tau1', 'FatJet_tau2', 'FatJet_tau3']

    # Declaration of a list of the "pixels-list"
    npixels = 1600
    listpixels = [[] for i in repeat(None, npixels)]
    branches = []
    for col in range(0,npixels):
        branches.append('img_'+ str(col))

    counter = 0
    for i_evt in range(n):
        print counter
        t.GetEntry(i_evt)
    
        # Collect Kinematics info from GenTop
        n_jets =  t.nFatjetCA15ungroomed
        if n_jets==0:
            continue

        for i_jet in np.arange(n_jets):
            # Collect Kinematics info from FatJet
            pt_fatjet = t.FatjetCA15ungroomed_pt[i_jet]
            eta_fatjet = t.FatjetCA15ungroomed_eta[i_jet]
            phi_fatjet = t.FatjetCA15ungroomed_phi[i_jet]
            m_fatjet = t.FatjetCA15ungroomed_mass[i_jet]
            tau1 = t.FatjetCA15ungroomed_tau1[i_jet]
            tau2 = t.FatjetCA15ungroomed_tau2[i_jet]
            tau3 = t.FatjetCA15ungroomed_tau3[i_jet]
            fatjet_listkin = [pt_fatjet,eta_fatjet,phi_fatjet,m_fatjet,tau1,tau2,tau3]
        
            for var in range(0,kinematics_variables_mult):
                list_fatjetkin[var].append(fatjet_listkin[var])
            
            NEvents.append(counter)
            counter = counter+1
            for px in range(0,1600):
                pixel = getattr(t,'FatjetCA15ungroomed_img_'+ str(px))[i_jet]
                listpixels[px].append(pixel)

    # Check that all the columns have the same size
    print 'Checking the size of the columns...'
    size_NEvents = len(NEvents)
    size_pixels_columns = len(listpixels[500])
    size_kinematics_columsn = len(list_fatjetkin[0])
    print size_NEvents, size_pixels_columns, len(branches), size_kinematics_columsn

    # Store the information into an .h5 file
    print 'Saving the columns into an .h5 file...'

    # Add a bkg column for "is_signal_new"
    is_signal_new = [0]*size_NEvents

    df = pandas.DataFrame(NEvents, columns=['entries'])
    for n in range(0,kinematics_variables_mult):
        df[kinematics_fatjet_branches[n]] = list_fatjetkin[n]
    df['is_signal_new'] = is_signal_new
    for n in range(0,len(branches)):
        df[branches[n]] = listpixels[n]

    outputname = 'toptable.h5'
    #outputname = rootfile.split('.root')
    #outputname = outputname[0] + '.h5'
    df.to_hdf(outputname,'table', append=True, clobber=True)

    # Call the imager
    #imager(outputname,0)




