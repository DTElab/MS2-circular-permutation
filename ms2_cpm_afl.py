# -*- coding: utf-8 -*-
"""MS2 CPM_AFL.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1KrC-KHGUxxrMZaXbwsZhabKQf_KOyTec

# SL heatmap generation for CPM library from sequence files

This AFL heatmap generation is designed to use the read counts from the alignment.

# Setup
*   Mount Google Drive to access input/output
*   Set working directory
*   Import packages
*   Define sequence-specific variables
"""

# import from Drive
from google.colab import drive
drive.mount('/content/drive')

import os
import re
import pandas as pd
from collections import Counter
from mpl_toolkits.mplot3d import Axes3D
from scipy import stats
import matplotlib as matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = '/content/drive/My Drive/MS2/Arial.ttf' # Replace with your actual path
font_name = fm.FontProperties(fname=font_path).get_name()
fm.fontManager.addfont(font_path)
plt.rc('font', family=font_name)

import numpy as np
import math
import matplotlib.patches as mpatches
import matplotlib.colors as colors

'''Define Sequence-Specific Variables'''
# assign the reference gene as CP-CP
ms2_CPCP_gene = ('GCGTCGAACTTTACGCAATTCGTGCTCGTAGACAACGGAGGGACAGGTGACGTA' +
            'ACTGTGGCCCCGAGTAACTTCGCGAATGGCGTCGCCGAGTGGATCTCCAGCAAT' +
            'TCTCGCAGCCAAGCTTATAAAGTTACCTGTAGTGTGCGGCAGAGCTCAGCGCAG' +
            'AACCGTAAATACACGATTAAAGTTGAAGTACCAAAAGTGGCAACCCAGACCGTG' +
            'GGCGGCGTCGAACTGCCGGTCGCAGCCTGGCGCAGCTATCTGAACATGGAATTA' +
            'ACCATTCCGATCTTTGCGACGAATTCCGATTGCGAGCTGATTGTTAAAGCTATG' +
            'CAGGGTTTGCTGAAGGATGGCAATCCCATTCCTTCGGCGATAGCCGCAAACTCA' +
            'GGTATCTACGCGTCGAACTTTACGCAATTCGTGCTCGTAGACAACGGAGGGACA' +
            'GGTGACGTAACTGTGGCCCCGAGTAACTTCGCGAATGGCGTCGCCGAGTGGATC' +
            'TCCAGCAATTCTCGCAGCCAAGCTTATAAAGTTACCTGTAGTGTGCGGCAGAGC' +
            'TCAGCGCAGAACCGTAAATACACGATTAAAGTTGAAGTACCAAAAGTGGCAACC' +
            'CAGACCGTGGGCGGCGTCGAACTGCCGGTCGCAGCCTGGCGCAGCTATCTGAAC' +
            'ATGGAATTAACCATTCCGATCTTTGCGACGAATTCCGATTGCGAGCTGATTGTT' +
            'AAAGCTATGCAGGGTTTGCTGAAGGATGGCAATCCCATTCCTTCGGCGATAGCC' +
            'GCAAACTCAGGTATCTAC')

ms2_CP = ('ASNFTQFVLVDNGGTGDVTVAPSNFANGVAEWISSNSRSQAYKVTC'+
               'SVRQSSAQNRKYTIKVEVPKVATQTVGGVELPVAAWRSYLNMELTIPIFATNSDCELIVKA'+
               'MQGLLKDGNPIPSAIAANSGIY')

ms2_CPCP_protein = ('ASNFTQFVLVDNGGTGDVTVAPSNFANGVAEWISSNSRSQAYKVTCS' +
                     'VRQSSAQNRKYTIKVEVPKVATQTVGGVELPVAAWRSYLNMELTIPI' +
                     'FATNSDCELIVKAMQGLLKDGNPIPSAIAANSGIYASNFTQFVLVDN' +
                     'GGTGDVTVAPSNFANGVAEWISSNSRSQAYKVTCSVRQSSAQNRKYT' +
                     'IKVEVPKVATQTVGGVELPVAAWRSYLNMELTIPIFATNSDCELIVK' +
                     'AMQGLLKDGNPIPSAIAANSGIY')

num_AAs = len(ms2_CP)

# define dictionary of codons to amino acids in order of AAs keys
codons_to_AAs = {'GCT': 'A', 'GCG': 'A', 'GCA': 'A', 'GCC': 'A',
                 'TCT': 'S', 'TCG': 'S', 'TCA': 'S', 'TCC': 'S',
                 'AGT': 'S', 'AGC': 'S', 'ACT': 'T', 'ACG': 'T',
                 'ACA': 'T', 'ACC': 'T', 'GTT': 'V', 'GTG': 'V',
                 'GTA': 'V', 'GTC': 'V', 'TGT': 'C', 'TGC': 'C',
                 'GAG': 'E', 'GAA': 'E', 'GAT': 'D', 'GAC': 'D',
                 'AAG': 'K', 'AAA': 'K', 'CGT': 'R', 'CGG': 'R',
                 'CGA': 'R', 'CGC': 'R', 'AGG': 'R', 'AGA': 'R',
                 'CAG': 'Q', 'CAA': 'Q', 'AAT': 'N', 'AAC': 'N',
                 'ATG': 'M', 'ATT': 'I', 'ATA': 'I', 'ATC': 'I',
                 'TTG': 'L', 'TTA': 'L', 'CTT': 'L', 'CTG': 'L',
                 'CTA': 'L', 'CTC': 'L', 'CAT': 'H', 'CAC': 'H',
                 'TTT': 'F', 'TTC': 'F', 'TAT': 'Y', 'TAC': 'Y',
                 'TGG': 'W', 'GGT': 'G', 'GGG': 'G', 'GGA': 'G',
                 'GGC': 'G', 'CCT': 'P', 'CCG': 'P', 'CCA': 'P',
                 'CCC': 'P', 'TAG': '*', 'TAA': '*', 'TGA': '*'}

"""# Filter sequences and populate heatmap arrays with read counts for each sequencing library

After importing packages and defining project-specific variables, processing can begin. The first step is to pull the DNA sequences from the alignment output. The "parse_from_txt" function keeps only sequences that start with "ATG" and end with "TAA" at the appropriate position. Please note that here I choose not to keep the start codon or stop codon because my reference MS2 CP gene does not include them.

---

Sequencing libraries:

1.   asl01.txt - CPM #1: VLPs, post size selection, replicate 1
2.   asl02.txt - CPM #2: VLPs, post size selection, replicate 2
3.   asl03.txt - CPM #3: VLPs, post size selection, replicate 3
4.   asl04.txt - CPM #4: Plasmids (combined), replicate 1
5.   asl05.txt - CPM #5: Plasmids (combined), replicate 2
6.   asl06.txt - CPM #6: Plasmids (combined), replicate 3

---

Indexes of columns in a SAM file output (indexes are added according to the indexes in a pandas dataframe):
0. QNAME: Query name of the read or the read pair
1. FLAG: Bitwise flag (pairing, strand, mate strand, etc.)
2. RNAME: Reference sequence name
3. POS: 1-Based leftmost position of clipped alignment
4. MAPQ: Mapping quality (Phred-scaled)
5. CIGAR: Extended CIGAR string (operations: MIDNSHP)
6. MRNM: Mate reference name (‘=’ if same as RNAME)
7. MPOS: 1-based leftmost mate position
8. ISIZE: Inferred insert size
9. SEQQuery: Sequence on the same strand as the reference
10. QUAL: Query quality (ASCII-33=Phred base quality)
11. (11+): optional fields
"""

def parse_from_txt(file):
    '''This takes the aligned, merged file from terminal analysis. We first get rid of any genes that do not
    start with ATG and end with TAA. Then we append the resulting genes to a list.'''
    gene = ""
    file_path = os.path.join('/content/drive/My Drive/MS2/Input .txt Files/SL CPM Library/', file+'.txt') #open and read the text file containing aligned library reads
    txt_columns = ['QNAME','FLAG','RNAME','POS','MAPQ','CIGAR','MRNM','MPOS',
                   'ISIZE','SEQQuery','QUAL','1','2','3','4','5','6']
    reads_df = pd.read_table(file_path, header=None, names=txt_columns, on_bad_lines='skip')
    seq_ID = reads_df['QNAME'] #this is a list of query IDs
    aligned_p = reads_df['RNAME'] #this is a list of aligned positions on the reference library
    seq_POS = reads_df['POS'] #this is a list of positions on the reference library
    seqs = reads_df['SEQQuery'] #this is a list of genes that will be counted later
    record_seq = []
    record_pos = []
    num_reads = len(seqs)
    for x in range(num_reads): #separate out each read to be analyzed individually
        '''The start codon follow a tab, and the stop codon should preceed a tab'''
        if seq_POS[x] != 1:
            #if seq_ID[x] in set(seq_ID[:x]) or seq_ID[x] in set(seq_ID[x+1:]):
            continue
        for i in range(30): #scan the first 30 letters for the start and stop codons
            if seqs[x][i:i+5] == "TCATG": # find the start codon: "TCATG" is only specific to the start codon region
                gene = seqs[x][i+5:] #only take records that agree with both of these conditions and that correspond to CP genes
                record_seq.append(gene) #append to a list for further analysis
                record_pos.append(aligned_p[x])
                break
    print(file + ' total seqs: '+str(len(record_seq)))
    return record_pos, record_seq

def dna_translate(dna_lst):
    '''This function is to translate DNA reads from NGS into amino acid reads.'''

    aa_lst = []

    for dna_seq in dna_lst:
        aa_seq = str()
        for codon_number in range(num_AAs):
          dna_base_num = codon_number * 3 #dna_base_num is dna base pair number
          codon = dna_seq[dna_base_num:dna_base_num+3].replace('N', 'G') # if there is an 'N' in the codon, replace it with 'G'
          aa_seq += codons_to_AAs[codon]
        aa_lst.append(aa_seq)

    return aa_lst

def seq_correction(po_lst, dna_lst):
    '''This function is to correct the list of CPM positions.
    CPM positions will be omitted if there is a misalignment to the reference sequences.'''
    corrected_po_lst = []
    initial_len = len(dna_lst)

    for x in range(initial_len):
        dna_seq = dna_lst[x]
        aligned_po = 3 * (po_lst[x] - 1) # the starting base number on MS2 DNA sequence
        ref = ms2_CPCP_gene[aligned_po:aligned_po + 8]
        # rescue the sequence if there is only point mutations caused by reading error
        # compare the starting 8-bp sequence in the read to that of the reference sequence
        truncated_dna_seq = dna_seq[:8]
        if truncated_dna_seq in ref:
            corrected_po_lst.append(po_lst[x])
        elif truncated_dna_seq in ms2_CPCP_gene:
            nt_num = ms2_CPCP_gene.find(truncated_dna_seq)
            if nt_num % 3 == 0:
                aa_num = int(nt_num / 3)
                corrected_po_lst.append(aa_num+1)

    print('total seqs after correction: ' + str(len(corrected_po_lst)))
    print('number of tossed seqs: ' + str(initial_len - len(corrected_po_lst)))

    return corrected_po_lst

def count_heatmap(CPM_lst):
    '''This function takes the output of list_seqs and counts codons. Several conditions are in place:
    First, we determine how many mutations there are per gene. We discard wildtype reads (or those with zero
    mutations. Anything with one mutation is counted. For reads with two or more mutations, any 1-bp mutations
    are discarded, while 2+ bp mutations are counted'''

    intensities = np.zeros(num_AAs)
    err_num = 0

    for CPM_num in CPM_lst: #dna_read counts where you are in sequencing reads
        intensities[CPM_num-1] += 1 # CPM count increases by 1

    print ("unknown CPM counts: " + str(err_num))

    return intensities

def heatmap(file):
    '''Combines all analyses into one function that outputs the counted array'''
    array_po, array_dna = parse_from_txt(file)
    array_po_corrected = seq_correction(array_po, array_dna)
    array_counts = count_heatmap(array_po_corrected)
    return array_counts

# generate a csv of heatmaps from triplicates
rep1 = heatmap('asl01')
rep2 = heatmap('asl02')
rep3 = heatmap('asl03')
rep4 = heatmap('asl04')
rep5 = heatmap('asl05')
rep6 = heatmap('asl06')

counts_df = pd.DataFrame({'screened lib1': rep1, 'screened lib2': rep2, 'screened lib3': rep3,
                          'unscreened lib1': rep4, 'unscreened lib2': rep5, 'unscreened lib3': rep6})
counts_df.to_csv('CPM_counts.csv')

"""# AFL Calculations (Figure 3A)

A function to calculate relative abundance between final VLP after selection and starting plasmid library for each replicate
"""

def heatmap_diff(array1, array2):
    '''Compares two heatmaps. Array 1 / Array 2, with zeros in array2 masked with np.nans'''
    diff = np.zeros(num_AAs)
    total1 = np.sum(array1)
    total2 = np.sum(array2)
    for codon in range(num_AAs):
        if array2[codon] == 0: #if there's a zero in array2, the position becomes nan
            diff[codon] = np.nan
        else:
            diff[codon] = (array1[codon] * total2) / (array2[codon] * total1) #else, divide, add to diff
    return diff

"""A function that averages the three biological replicates"""

def heatmap_avgs(array1, array2, array3):
    '''Takes average of three heatmaps'''
    log = np.zeros(num_AAs)
    m = np.array([array1, array2, array3]) #this array of arrays means we can use axis=0 to get the mean
    mean = np.nanmean(m, axis=0) #nanmean masks ignores nan values
    for i in range(num_AAs):
        mean[i] = max(mean[i], .0001) #if the mean is zero, replace with .0001 so the resulting log value is -4
        log[i] = np.log10(mean[i]) #take the log of the mean value
    return log #this is the finalized heatmap with apparent fitness scores

"""Define a function to calculate AFL from individual libraries, calculate the mean and standard deviation of individual AFLs and plot them."""

def AFL_mean_std(array1, array2, array3):
    '''Takes average of three heatmaps'''
    AFL = np.zeros((3, num_AAs)) #nanmean masks ignores nan values
    for i in range(num_AAs):
        mean1 = max(array1[i], .0001) #if the mean is zero, replace with .0001 so the resulting log value is -4
        mean2 = max(array2[i], .0001)
        mean3 = max(array3[i], .0001)
        AFL[0,i] = np.log10(mean1) #take the log of the mean value
        AFL[1,i] = np.log10(mean2)
        AFL[2,i] = np.log10(mean3)

    mean_AFL = np.nanmean(AFL, axis=0)
    mean_AFL = np.round(mean_AFL, 3)
    plt.scatter(range(num_AAs), mean_AFL)
    std_AFL = np.nanstd(AFL, axis=0)
    std_AFL = np.round(std_AFL, 3)
    plt.errorbar(range(num_AAs), mean_AFL, yerr=std_AFL, fmt='o')
    plt.title("CPM AFS", fontweight='bold')
    plt.xlabel("Residue Number")
    plt.ylabel("AFS")
    plt.savefig("CPM AFS", dpi=1000, format='pdf')
    plt.show()
    return mean_AFL, std_AFL #this is the finalized heatmap with apparent fitness scores

"""Define a function to actually plot the heatmap"""

def plot_heatmap(heatmap_np, name):

    heatmap_T = heatmap_np.T

    xtix = []
    for i in range(1,13):
        i = i * 10
        xtix.append(i)

    data = heatmap_T.reshape(1, -1)
    data = np.ma.masked_invalid(data)

    fig, ax = plt.subplots(figsize = (60,5),layout='constrained')
    ax.patch.set(hatch='', color="#7B9569")
    im = ax.pcolor(data, cmap='RdBu', vmax = 2, vmin = -2, edgecolor='black', linestyle=':', lw=4)
    cbar = plt.colorbar(im, aspect=70, orientation='horizontal', location='bottom', shrink=0.6)
    plt.title(name, fontsize=36, fontweight='bold')
    plt.xlabel("Starting Residue Number", fontsize=30, fontweight='bold')
    plt.ylabel("", fontsize=24, fontweight='bold')
    plt.xticks(fontsize=24, fontweight='bold')

    # Shift ticks to be at 0.5, 1.5, etc
    ax.xaxis.set(ticks=np.arange(9.5, 128.5, 10), ticklabels=xtix)
    ax.yaxis.set_visible(False)
    plt.tick_params(axis='x',
                      width=3)

    cbar.ax.tick_params(labelsize=24, width=3)
    cbar.outline.set_linewidth(2.5)

    ax.spines['top'].set_linewidth(3)
    ax.spines['bottom'].set_linewidth(3)
    ax.spines['left'].set_linewidth(3)
    ax.spines['right'].set_linewidth(3)

    plt.savefig(name, dpi=1000, format='pdf')
    plt.show()

    return

"""Finally, pull all of the calculations functions together in one and output final averaged amino acid heatmap array"""

'''Figure 3a: The Apparent Fitness Landscape'''

def heatmap_diff_bioreps(file):
    '''All analysis to generate a heatmap plot'''
    libs = ['screened lib1', 'screened lib2', 'screened lib3',
            'unscreened lib1', 'unscreened lib2', 'unscreened lib3']
    df = pd.read_csv(file, header = 0, names=libs)
    a = df['screened lib1']
    b = df['screened lib2']
    c = df['screened lib3']
    d = df['unscreened lib1']
    e = df['unscreened lib2']
    f = df['unscreened lib3']

    a_d = heatmap_diff(a, d)
    b_e = heatmap_diff(b, e)
    c_f = heatmap_diff(c, f)

    # final = heatmap_avgs(a_d, b_e, c_f)
    AFL, std = AFL_mean_std(a_d, b_e, c_f) # calculate the AFL with the new method
    AFL_df = pd.DataFrame({'CPM_AFL': AFL, 'stdev': std}, index=range(1,130))
    AFL_df.to_csv('CPM_AFL.csv')

    return AFL

#calculate circular permutation AFL and plot the heatmap
htmp_avg = heatmap_diff_bioreps('CPM_counts.csv')
plot_heatmap(htmp_avg, 'MS2 Circular Permutation Apparent Fitness Landscape')

"""# AFL Subsets and Validation (Figure 3B)

"""

'''Plot Figure 3b'''
def plot_assembly_assay():
    selected_CPMs = ['2', '20', '29', '53', '56', '57',
                     '62', '69', '86', '90', '96', '113', '129']

    AFS = [0.223, -1.49, -0.556, 0.967, 1.216, 0.762,
           -1.465, -1.443, -1.496, -1.403, -1.213, -1.49, -0.806]
    AFS_std = [0.109, 0.044, 0.047, 0.299, 0.076, 0.101,
               0.083, 0.13, 0.132, 0.22, 0.081, 0.052, 0.099]
    AUC = [189.657, 151.366, 194.708, 1037.619, 732.298, 1385.299,
           107.411, 93.158, 254.809, 235.057, 241.771, 145.836, 111.822]
    AUC_std = [59.002, 3.949, 8.599, 96.939, 190.497, 75.273,
               15.589, 29.227, 15.319, 68.112, 56.387, 65.156, 41.662]

    fig, ax = plt.subplots(layout='constrained')
    ax.scatter(AFS, AUC, color='#6D0220')
    ax.errorbar(AFS, AUC, yerr=AUC_std, xerr=AFS_std, linestyle='None', color='#6D0220', capsize=4, linewidth=2)

    #plot the data of functional CPMs
    fun_AFS = [0.967, 1.216, 0.762]
    fun_AFS_std = [0.299, 0.076, 0.101]
    fun_AUC = [1037.619, 732.298, 1385.299]
    fun_AUC_std = [96.939, 190.497, 75.273]

    ax.scatter(fun_AFS, fun_AUC, color='#053061')
    ax.errorbar(fun_AFS, fun_AUC, yerr=fun_AUC_std, xerr=fun_AFS_std, linestyle='None', color='#053061', capsize=4, elinewidth=2)

    #plot the data of intermediate CPMs
    inter_AFS = [0.223]
    inter_AFS_std = [0.109]
    inter_AUC = [189.657]
    inter_AUC_std = [59.002]

    ax.scatter(inter_AFS, inter_AUC, color='#696969')
    ax.errorbar(inter_AFS, inter_AUC, yerr=inter_AUC_std, xerr=inter_AFS_std, linestyle='None', color='#696969', capsize=4, elinewidth=2)

    plt.ylabel('VLP Peak Area (A.U.)', fontsize='18')
    plt.xlabel('Apparent Fitness Score', fontsize='18')
    plt.tick_params(axis='both',
                    width=2, labelsize=16)

    ax.spines['top'].set_linewidth(2)
    ax.spines['right'].set_linewidth(2)
    ax.spines['bottom'].set_linewidth(2)
    ax.spines['left'].set_linewidth(2)

    plt.savefig('CPM_Assembly_assay', dpi=1000, format='pdf')

    return

#plot the assessment of the individual assembly assay
plot_assembly_assay()

"""# Comparison between circular permutation capbility and mutability (Supplementary Figure 6)
Comparing the mutatbility index from Hartman's MI to AFS in the circular permutation AFL.
"""

file_paths = ['CPM_AFL.csv',
              './Individual Working Notebooks/Shiqi Liang/20240426 Shiqi MS2 - CPM lib/MS2 MI.csv']

def MI_and_AFS():
    AFS_df = pd.read_csv(file_paths[0], header = 0)
    AFS = AFS_df['CPM_AFL'].to_numpy()
    MI_df = pd.read_csv(file_paths[1], header = 0)
    MI = MI_df['Mutability Index'].to_numpy()
    return AFS, MI

'''Supplemental Figure 6a'''
def plot_MI(AFS, MI):
    cm = 1/2.54
    fig, ax1 = plt.subplots(figsize = (18*cm, 4*cm))

    ax1.scatter(range(1, num_AAs+1), AFS, color='crimson', s=3.5)
    ax1.plot(range(1, num_AAs+1), AFS, color='crimson', linewidth=1)
    ax1.set_xlabel('Residue Number', fontsize=6.5)
    ax1.set_ylabel('Circular Permutation AFS', color='crimson', fontsize=6.5)
    ax1.tick_params('y', colors='crimson', labelsize=6, width=0.5, length=1)
    ax1.tick_params('x', labelsize=6, width=0.5, length=1)

    ax2 = ax1.twinx()
    ax2.scatter(range(1, num_AAs+1), MI, color='royalblue', s=3.5)
    ax2.plot(range(1, num_AAs+1), MI, color='royalblue', linewidth=1)
    ax2.set_ylabel('Mutability Index', color='royalblue', fontsize=6.5)
    ax2.tick_params('y', colors='royalblue', labelsize=6, width=0.5, length=1)

    ax1.spines['top'].set_linewidth(0.6)
    ax1.spines['right'].set_linewidth(0.6)
    ax1.spines['bottom'].set_linewidth(0.6)
    ax1.spines['left'].set_linewidth(0.6)

    plt.tight_layout()

    plt.savefig('AFSvsMI', dpi=1000, format='pdf')
    return

'''Supplemental Figure 6c'''
def plot_AFS_vs_MI(AFS, MI):

    cm = 1/2.54

    AFS_screened = []
    MI_screened = []
    for i in range(num_AAs):
        if AFS[i] > -0.6:
            AFS_screened.append(AFS[i])
            MI_screened.append(MI[i])

    #linear regression of AFS to MI above AFS=-0.6
    slope, intercept, r_value, p_value, std_err = stats.linregress(AFS_screened, MI_screened)
    pred = []
    for i in range(len(AFS_screened)):
        prediction = slope * AFS_screened[i] + intercept
        pred.append(prediction)

    fig, axs = plt.subplots(1, 2, figsize=(17.5*cm, 7*cm))

    axs[0].scatter(AFS, MI, color='thistle', s=4)
    axs[0].scatter(AFS_screened, MI_screened, color='darkviolet', s=4)
    axs[0].set_xlabel('Circular Permutation AFS', fontsize=6.5)
    axs[0].set_ylabel('Mutability Index', fontsize=6.5)
    axs[0].tick_params(labelsize=6, width=0.5, length=1)

    axs[1].scatter(AFS_screened, MI_screened, color='darkviolet', s=4)
    axs[1].plot(AFS_screened, pred, color='black', linewidth=1)
    r_squared = r'$r =$' + str(round(r_value,2))
    axs[1].text(0.6, -0.5, s=r_squared, fontsize=7)
    axs[1].set_xlabel('Circular Permutation AFS (AFS > -0.60)', fontsize=6.5)
    axs[1].set_ylabel('Mutability Index', fontsize=6.5)
    axs[1].tick_params(labelsize=6, width=0.5, length=1)

    fig.tight_layout()

    plt.savefig('AFSvsMI_scatter', dpi=1000, format='pdf')
    return

'''Supplemental Figure 6b'''

def plot_subset_AFS_vs_MI(AFS, MI):

    cm = 1/2.54

    AFS = AFS[51:58]
    MI = MI[51:58]
    residues = range(52,59)

    fig, ax1 = plt.subplots(figsize = (10.5*cm, 3.5*cm))

    ax1.scatter(residues, AFS, color='crimson', s=4)
    ax1.plot(residues, AFS, color='crimson', linewidth=1)
    ax1.set_xlabel('Residue Number', fontsize=6.5)
    ax1.set_ylabel('Circular Permutation AFS', color='crimson', fontsize=6.5)
    ax1.tick_params('y', colors='crimson', labelsize=6, width=0.5, length=1)
    ax1.tick_params('x', labelsize=6, width=0.5, length=1)

    ax2 = ax1.twinx()
    ax2.scatter(residues, MI, color='royalblue', s=4)
    ax2.plot(residues, MI, color='royalblue', linewidth=1)
    ax2.set_ylabel('Mutability Index', color='royalblue', fontsize=6.5)
    ax2.tick_params('y', colors='royalblue', labelsize=6, width=0.5, length=1)

    ax1.spines['top'].set_linewidth(0.6)
    ax1.spines['right'].set_linewidth(0.6)
    ax1.spines['bottom'].set_linewidth(0.6)
    ax1.spines['left'].set_linewidth(0.6)
    fig.tight_layout()

    plt.savefig('AFSvsMI_subset', dpi=1000, format='pdf')
    return

#compare circular permutation AFS to mutability index
AFS, MI = MI_and_AFS()
plot_MI(AFS, MI)
plot_AFS_vs_MI(AFS, MI)
plot_subset_AFS_vs_MI(AFS, MI)