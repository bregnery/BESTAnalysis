import FWCore.ParameterSet.Config as cms

process = cms.Process("run")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.options = cms.untracked.PSet(SkipEvent = cms.untracked.vstring('ProductNotFound') )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring('file:Radion_hh_wwww_M3500_MiniAOD.root')
)
process.MessageLogger.cerr.FwkReport.reportEvery = 50

process.BESTProducer = cms.EDProducer('BESTProducer',
	pdgIDforMatch = cms.int32(6),
	NNtargetX = cms.int32(1),
	NNtargetY = cms.int32(1),
	isMC = cms.int32(1),
	doMatch = cms.int32(0)

)

process.BESTAnalyzer = cms.EDProducer('BESTAnalyzer')

process.TFileService = cms.Service("TFileService", fileName = cms.string("histo_HHwwww.root") )

process.out = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string("ana_out.root"),
                               SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
                               outputCommands = cms.untracked.vstring('keep *',
                                                                      #'keep *_*run*_*_*'
                                                                      #, 'keep *_goodPatJetsCATopTagPF_*_*'
                                                                      #, 'keep recoPFJets_*_*_*'
                                                                      ) 
                               )
process.outpath = cms.EndPath(process.out)

process.p = cms.Path(process.BESTProducer*process.BESTAnalyzer)
