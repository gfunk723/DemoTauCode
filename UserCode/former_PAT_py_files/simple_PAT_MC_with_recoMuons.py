## import skeleton process
from PhysicsTools.PatAlgos.patTemplate_cfg import *
from PhysicsTools.PatAlgos.tools.tauTools import *


# based on (https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#5_3_12_and_higher)
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")



# load the standard PAT config
#process.load("PhysicsTools.PatAlgos.patSequences_cff")

# load the coreTools of PAT
#from PhysicsTools.PatAlgos.tools.pfTools import *
#usePF2PAT(process)

# based on https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#5_3_12_and_higher
# not sure this next line is really needed 
switchToPFTauHPS(process)


## let it run
process.p = cms.Path(process.recoTauClassicHPSSequence+process.PFTau+process.patDefaultSequence)


## ------------------------------------------------------
#  In addition you usually want to change the following
#  parameters:
## ------------------------------------------------------
#
process.GlobalTag.globaltag = 'START53_V7G::All' ##  (according to https://twiki.cern.ch/twiki/bin/view/CMS/SWGuideFrontierConditions)
#process.source.fileNames = ['file:/afs/cern.ch/cms/Tutorials/TWIKI_DATA/CMSDataAnaSch_RelValZMM536.root']
process.source.fileNames = ['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/00E903E2-9FE9-E111-8B1E-003048FF86CA.root']
process.maxEvents.input = 3         ##  ( -1 to run on all events)
#process.out.fileName = 'MC.root'            ##  (e.g. 'myTuple.root')


from PhysicsTools.PatAlgos.patEventContent_cff import patEventContent
process.out = cms.OutputModule("PoolOutputModule",
                               fileName = cms.untracked.string('smallPatTuple.root'),
                               # save only events passing the full path
                               SelectEvents   = cms.untracked.PSet( SelectEvents = cms.vstring('p') ),
                               # save PAT Layer 1 output; you need a '*' to
                               # unpack the list of commands 'patEventContent'
                               outputCommands = cms.untracked.vstring(
                             #      'keep *',
'keep patVertexAssociationedmValueMap_patTrackVertexInfo__PAT',
'keep CaloTowers_selectedPatJets_caloTowers_PAT',
'keep patElectrons_cleanPatElectrons__PAT',
'keep patGenericParticles_cleanPatTrackCands__PAT',
'keep patGenericParticles_selectedPatTrackCands__PAT',
'keep patJets_cleanPatJets__PAT',
'keep patMETs_patMETs__PAT',
'keep patMuons_cleanPatMuons__PAT',
'keep patPhotons_cleanPatPhotons__PAT',
'keep patTaus_cleanPatTaus__PAT',
'keep recoGenJets_selectedPatJets_genJets_PAT',
                                   'keep recoMuons_muons__RECO')
                               )

process.outpath = cms.EndPath(process.out)
