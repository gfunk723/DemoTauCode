import FWCore.ParameterSet.Config as cms
process = cms.Process("Ntuple")

#####################
# config parameters
#####################

runOnMC = True
MAX_ELECTRONS = 20 # max number of leptons to consider in the cleanPat collections
MAX_MUONS = 20
MAX_TAUS = 20

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(15) )

######################
# set the global tag
#######################
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
if runOnMC:
  process.GlobalTag.globaltag = 'START53_V23::All'
else:
  process.GlobalTag.globaltag = 'FT_53_V21_AN4::All'
process.load('JetMETCorrections.Configuration.DefaultJEC_cff')



myfilelist = cms.untracked.vstring()
myfilelist.extend(['file:/uscms/home/shalhout/no_backup/patTuple_testing.root'])

process.source = cms.Source ("PoolSource",
                      fileNames=myfilelist,
                      skipEvents=cms.untracked.uint32(0)
                             )




process.myProducerLabel = cms.EDProducer('Ntuple')
#################################


##########################
# diMuon & diElectron Vetoes
##########################

process.isDiMuonEvent = cms.EDFilter("DiMuonFilter",
  muonSource     = cms.InputTag("cleanPatMuons"),
  vertexSource      = cms.InputTag("offlinePrimaryVertices"),
  filter = cms.bool(True)
)


process.isDiElectronEvent = cms.EDFilter("DiElectronFilter",
  electronSource     = cms.InputTag("cleanPatElectrons"),
  vertexSource      = cms.InputTag("offlinePrimaryVertices"),
  filter = cms.bool(True)
)


####################################
# setup the MVA MET calculation
#####################################

process.load("JetMETCorrections.Configuration.JetCorrectionServicesAllAlgos_cff")
if runOnMC:
  process.prefer("ak5PFL1FastL2L3")
else:
  process.prefer("ak5PFL1FastL2L3Residual")

process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
#from RecoMET.METPUSubtraction.mvaPFMET_leptons_cff import pfMEtMVA
from RecoMET.METPUSubtraction.mvaPFMET_cff import calibratedAK5PFJetsForPFMEtMVA
process.load("RecoMET.METPUSubtraction.mvaPFMET_cff")
process.calibratedAK5PFJetsForPFMEtMVA = calibratedAK5PFJetsForPFMEtMVA.clone()

if runOnMC:
  process.calibratedAK5PFJetsForPFMEtMVA.correctors = cms.vstring("ak5PFL1FastL2L3")
else:
  process.calibratedAK5PFJetsForPFMEtMVA.correctors = cms.vstring("ak5PFL1FastL2L3Residual")

##############################

##############################
# produce the single electron,
# muon, and tau collections
# that will be used for pair-wise
# mvaMet calculation

singlePatLeptons = cms.Sequence()

for eINDEX in range(MAX_ELECTRONS):
        eModuleName = "cleanPatElectrons%i" % (eINDEX)
        eModule = cms.EDProducer('SinglePatElectronProducer' ,
                electronSrc =cms.InputTag('cleanPatElectrons'),
                INDEX = cms.uint32(eINDEX),
                NAME=cms.string(eModuleName))
        setattr(process, eModuleName, eModule)
        singlePatLeptons += eModule

for mINDEX in range(MAX_MUONS):
        mModuleName = "cleanPatMuons%i" % (mINDEX)
        mModule = cms.EDProducer('SinglePatMuonProducer' ,
                muonSrc =cms.InputTag('cleanPatMuons'),
                INDEX = cms.uint32(mINDEX),
                NAME=cms.string(mModuleName))
        setattr(process, mModuleName, mModule)
        singlePatLeptons += mModule

for tINDEX in range(MAX_TAUS):
        tModuleName = "cleanPatTaus%i" % (tINDEX)
        tModule = cms.EDProducer('SinglePatMuonProducer' ,
                tauSrc =cms.InputTag('cleanPatTaus'),
                INDEX = cms.uint32(tINDEX),
                NAME=cms.string(tModuleName))
        setattr(process, tModuleName, tModule)
        singlePatLeptons += tModule



#################################
process.out = cms.OutputModule("PoolOutputModule",
fileName = cms.untracked.string('NtupleFile.root'),
outputCommands = cms.untracked.vstring('drop *')
#SelectEvents = cms.untracked.PSet(SelectEvents = cms.vstring('p')
)



#################################
# keep everything produced by Tuepl-Ntuple
#################################
process.out.outputCommands +=['keep Tuple*_*_*_Ntuple']


#################################
# keep UserSpecifiedData
#################################
process.out.outputCommands +=['keep TupleUserSpecifiedDatas_UserSpecifiedData_TupleUserSpecifiedData_PAT']



process.p = cms.Path(
      process.myProducerLabel*
      process.isDiMuonEvent*
      process.isDiElectronEvent*
      process.singlePatLeptons
      #process.pfMEtMVANominal+
#      process.TupleElectronsNominal*
#      process.TupleMuonsNominal*
#      process.TupleTausNominal*
#      process.TupleMuonTausNominal*
#      process.TupleElectronTausNominal
      #+process.metUncertaintySequence+
      #process.TupleTausTauEnDown*process.TupleMuonTausTauEnDown
      #+process.TupleMuonTausRecoilUp
      #+process.TupleMuonTausRecoilDown
      #+process.TupleMuonTausRecoilResUp
      #+process.TupleMuonTausRecoilResDown
                     )

process.e = cms.EndPath(process.out)
