BEST Analysis
=============

This repository contains programs used to train and test a neural network that catagorizes different types of jets.

Instructions
============

This program has been tested with CMSSW_8_0_12. 

Installation
------------

To use this program, obtain this CMSSW release and move into the source directory.

    cmsrel CMSSW_8_0_12
    cd CMSSW_8_0_12/src
    cmsenv

Then, clone this git repository and compile CMSSW.

    git clone https://github.com/bregnery/BESTAnalysis.git
    scram b
    cmsenv 

Run BEST Producer
-----------------

The BEST producer can be run using the following:

    cd BESTAnalysis/BESTProducer/test
    cmsRun run_TT.py

TT can be replaced with any run_*.py program.

### Run on CRAB

First, source the .bash_profile in bregnery/Settings/lxplus. Then, set up the CRAB environment and obtain a proxy. Please note that this does require a GRID account.

    cmsenv
    CRAB
    vprox

Now, check that the CRAB environment is working properly.

    crab --version

Then, submit the crab*.py files to CRAB.

    crab submit -c crab*.py

Finally, check the status of the job in CRAB.

    crab status -d ./crab_projects/*/

The files produced here can train the NN. Some of the most recentfiles are on the LPC at:

    /eos/uscms/store/user/pilot/BESTFiles/Aug8/

Preparing Files for Training
----------------------------

Before training, some processing needs to be done.

### Flatten the Et Spectrum

The Et spectrum needs to be flattened to prevent the NN from biasing high Pt events.

    cd BESTAnalysis/BESTProducer/test
    root -l
    [0] .L flatten.C
    [1] flatten(TString infile, TString outWeightFile, float etMin = 500, float etMax = 4000)

it will spit out a weight file that you use with runTree.C.

### Compute Additoinal Variables and Targets

The next step is to compute additional variables and add the targets.  The script is runTree.C, which can also be used to evaluate new NNs on existing samples on-the-fly:

    cd BESTAnalysis/BESTProducer/test
    root -l
    [0] .L runTree.C
    [1] runTree(string inFile, string outFile, string histName, float targX, float targY, float targ3, float targ4, float targ5, bool reduce = 1)

The options are as follows:

* inFile → the inputFile to run over
* outFile → the outputFile name
* histName → the weight file used to flatten the pT distribution (see "Flatten the Et Spectrum")
* targets → the values of the desired outputs for each node
* reduce → reduce the total number of events to a desired number for training/testing

run_all.C can be used to run these commands sequentially for all samples.

Train the Neural Network
------------------------

After creating and processing the training files, the neural net can be trained. 

    cd BESTAnalysis/BESTProducer/TMVATraining
    root -l TMVARegression.C

This program takes a long time to run. This program can be tested by reducing the number of training events and input variables in order to create a small NN. The network is defined by an xml file in TMVATraining/weights/. This xml file needs to be used with runTree.C to evaluate the NN performance

Test the Neural Network
-----------------------

Once the NN xml file has been created, runTree.C can be re-run to look at the output distributions in a nice way. Make sure the correct xml file is in runTree.C:

See https://github.com/bregnery/BESTAnalysis/blob/master/BESTProducer/test/runTree.C#L139

The variables must defined in the same order as done in TMVARegression.C for the TMVA::Reader class. Make sure BookMVA() has the new file name of the xml file from training.

Program Details
===============

BESTProducer.cc
---------------

The BEST Producer computes the event shape quantities in the boosted frame, adds them as EDM products to the event, and produces a flat TTree with the quantities for NN training. Several files are available (run_TT.py, run_WW.py, etc.) and can be configured according to the sample of interest with the following options:

    process.run = cms.EDProducer('BESTProducer',
        pdgIDforMatch = cms.int32(6),  # the particle used for jet matching
        NNtargetX = cms.int32(1),  # not used
        NNtargetY = cms.int32(1),  # not used anymore
        isMC = cms.int32(1),   # if the input is MC (to use data eventually)
        doMatch = cms.int32(0) # if the matching requirement with pdgID is actually applied
    )

TMVARegression.C
----------------

Some important pieces of this file:

    factory->AddVariable( "h1_top", "h1_top", "", 'F' );   // Adding the variables for training -- they must match the branch names in the trees

    factory->AddTarget( "targetX" ); // The regression "targets" (output nodes) and desired outputs -- must have all 5 and the names must match the branch names again

    TChain *input = new TChain("jetTree"); // The input tree and file names (everything is added to one chain)

    factory->SetWeightExpression( "flatten", "Regression" );  // Apply the weights to flatten et

    TCut mycut = "et > 500 && et < 3000" // A cut to apply in creating testing/training samples

    factory->PrepareTrainingAndTestTree( mycut, "nTrain_Regression=100000:nTest_Regression=100000:SplitMode=Random:NormMode=NumEvents:!V" ); // Define training/testing sizes

Plotting Scripts
----------------

Some plotting scripts that are useful:

* draw.C → compares W/Z/t/H/j samples for individual variables (DoDraw.C for batch plot creation)
* draw2D.C → makes the cool 2D plot and lego plots for the individual samples
