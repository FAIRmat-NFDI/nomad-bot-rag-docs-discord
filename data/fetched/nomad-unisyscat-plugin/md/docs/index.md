# Welcome to the `nomad-unisyscat` documentation

![Combined logos for NOMAD Oasis and UniSysCat](images/Logos.png)

Welcome to the NOMAD Oasis demonstration! This documentation provides an overview of the example dataset, supported entry types, and details about the data and publications used in this demonstration. Our goal is to help UniSysCat users effectively manage and explore research data using NOMAD.

This demonstration highlights [NOMAD Oasis](https://nomad-lab.eu/nomad-lab/nomad-oasis.html), a data management and sharing platform developed as part of the [FAIRmat](https://www.fairmat-nfdi.eu/fairmat/) project within the National Research Data Infrastructure ([NFDI](https://www.nfdi.de/)). NOMAD facilitates the collection, storage, analysis, and dissemination of research data, adhering to the principles of FAIR (Findable, Accessible, Interoperable, and Reusable) data management.


## Introduction

This example demonstrates how NOMAD effectively manages diverse research data, particularly in computational and experimental research. It encompasses various entry types, showcasing NOMAD's flexibility and robust data integration features.

The dataset used in this demonstration originates from a paper by C. Lorent *et al.*
[(Angew. Chem. Int. Ed. 2021, 60, 15854–15862)](doi.org/10.1002/anie.202100451).

The paper introduces an innovative experimental setup for spectroscopic analyses of gas-converting metalloenzymes. It allows for adjustments in gas composition and temperature, enabling the preparation of specific redox states for characterization using complementary spectroscopic tools such as **IR**, **EPR**, or **NRVS**.

![Alt text](images/TOC%20figure%20from%20paper.png)


This NOMAD Oasis demonstration illustrates the Research Data Management (RDM) of experiments focusing on the regulatory [NiFe]-hydrogenase from Ralstonia eutropha (ReRH). The experiments involve preparing the catalytic intermediate (Ni<sub>a</sub>-C) using highly concentrated lyophilized samples of ReRH treated either in H<sub>2</sub> or D<sub>2</sub>, followed by characterizing the sample via IR, Electron paramagnetic resonance (EPR), and Nuclear Resonance Vibrational Spectroscopy (NRVS). Additionally, it includes the calculation of vibrational frequencies.

The demonstration covers creating entries for different parts of the experiment, uploading raw data files from measurements and calculations, visualizing them in NOMAD, launching analysis tools like Jupyter notebooks with the files in NOMAD, and demonstrating how different project members can collaborate.


### **Supported Entry Types**
In this demonstration, NOMAD supports multiple entry types, including:

#### **Experimental Data:**

- Tabular data files with the `.dat` file format.
- Binary data files with the `.DSC` file format.
- Electronic Lab Notebook (ELN) entries for samples, instruments, and processes, based on NOMAD basic sections.

#### **Computational data:**
   
- Output files from Density Functional Theory (DFT) calculations based on the ``Gaussian 09`` package.

### **Research Data**

The data used in this NOMAD Oasis demonstration come from various sources, ensuring a comprehensive representation of the types of entries NOMAD can handle. The primary sources include:

- **In-situ Infrared (IR) spectroscopy** for <code>ReRH_Ni<sub>a</sub>-C_H</code>.
- <sup>57</sup>Fe **nuclear resonance vibrational spectroscopy (NRVS)**, both measured and simulated, for <code>ReRH_Ni<sub>a</sub>-C_H</code> and <code>ReRH_Ni<sub>a</sub>-C_D</code>.
- **Electron paramagnetic spectroscopy (EPR)** for <code>ReRH_Ni<sub>a</sub>-C_H</code>.
- **Density functional theory (DFT)** calculations using the **Gaussian** package for <code>ReRH_Ni<sub>a</sub>-C_H</code> and <code>ReRH_Ni<sub>a</sub>-C_D</code>.

By exploring this demonstration, users will gain a clearer understanding of how NOMAD can streamline research data management processes, enhance and organize the data, and foster collaboration across UniSysCat.


<div markdown="block" class="home-grid">
<div markdown="block">

### How-to guides

How-to guides provide step-by-step instructions for a wide range of tasks, with the overarching topics:

- [Install this plugin](how_to/install_this_plugin.md)
- [Use this plugin](how_to/use_this_plugin.md)

</div>

<div markdown="block">


### Reference

The reference [section](reference/references.md) includes a list fo the measurements supported by this plugin.

</div>
</div>
