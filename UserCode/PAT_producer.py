########################################################################################################
import FWCore.ParameterSet.Config as cms
########################################################################################################

#process = cms.Process("DemoTauAna")

###################################################
# Import skeleton
###################################################
from PhysicsTools.PatAlgos.patTemplate_cfg import *

process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')

RunMETUnc = False
KeepAll = False
SampleName_='GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/Summer12_DR53X-PU_S10_START53_V7A-v1/AODSIM'
PhysicsProcess_='gg->H->tautau[SM_125_8TeV]'


###################################################
# Store SampleName and PhysicsProcess
# eventually these should be command line
# options
###################################################

process.UserSpecifiedData = cms.EDProducer('TupleUserSpecifiedDataProducer' ,
                                            SampleName=cms.string(SampleName_),
                                            PhysicsProcess=cms.string(PhysicsProcess_)
                                            )



###################################################
# need to get the correct version of the global
# tag and set JEC to match
###################################################

runOnMC = True
if runOnMC:
  process.GlobalTag.globaltag = 'START53_V23::All'
else:
  process.GlobalTag.globaltag = 'FT_53_V21_AN4::All'



########################################################################################################
# Setup PF2PAT (for now we will not run both PAT and PF2PAT, everything will be PF2PAT)
########################################################################################################

###################################################
# setup PF2PAT, empty postfix means
# only PF2PAT and not both PAT + PF2PAT
###################################################
from PhysicsTools.PatAlgos.tools.pfTools import *

###################################################
# use PF isolation
###################################################

usePFIso(process)

# if the sample does not contain value map of PF candidate "particleFlow:electrons", use following line.
# this appears to be the case for our test sample
process.patElectrons.pfElectronSource = 'particleFlow'


postfix = ""
jetAlgo = "AK5"
usePF2PAT(process,runPF2PAT=True, jetAlgo=jetAlgo, runOnMC=runOnMC, postfix=postfix)
switchToPFJets(process)

###############
# change some tau defaults
process.patTaus = process.patTaus.clone(embedIsolationPFCands = True,
                                        embedIsolationPFChargedHadrCands = True,
                                        embedIsolationPFGammaCands = True,
                                        embedIsolationPFNeutralHadrCands = True,
                                        embedLeadPFCand = True,
                                        embedLeadPFChargedHadrCand = True,
                                        embedLeadPFNeutralCand = True,
                                        embedSignalPFCands = True,
                                        embedSignalPFChargedHadrCands = True,
                                        embedSignalPFGammaCands = True,
                                        embedSignalPFNeutralHadrCands = True
                                                        )


#############################
# add in some gen level jet collections
# needed for the jet smear in MET unc.
##############################

from RecoJets.Configuration.GenJetParticles_cff import *
from RecoJets.Configuration.RecoGenJets_cff import *


process.genForPF2PATSequence = cms.Sequence(
    genParticlesForJetsNoNu +
    iterativeCone5GenJetsNoNu +
    ak5GenJetsNoNu +
    ak7GenJetsNoNu
    )




# needed for MVA met, but need to be here
from RecoMET.METPUSubtraction.mvaPFMET_leptons_PAT_cfi import *
process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
process.load('RecoMET.METPUSubtraction.mvaPFMET_leptons_cff')




##################################################
# specify settings for met mva
# https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet
# recoil corrections should be applied at Ntuple stage
# in later stages isomuons, isoelectrons are a resonable
# preselection for MET corrections
###################################################
process.pfMEtMVA = process.pfMEtMVA.clone(srcLeptons = cms.VInputTag("isomuons","isoelectrons","isotaus"),
                                          )






###################################################
# rm MC matching if DATA
###################################################

if not runOnMC:
  removeMCMatchingPF2PAT( process, 'All' )


###################################################
# load the PU JetID sequence
###################################################
from PhysicsTools.PatAlgos.tools.jetTools import *

switchJetCollection(process,cms.InputTag('ak5PFJets'),
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', cms.vstring(['L1FastJet', 'L2Relative', 'L3Absolute'])),
                 doType1MET   = True,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True
                 )



process.load("RecoJets.JetProducers.pujetidsequence_cff")

process.out.outputCommands +=['keep *_selectedPatJets*_*_*']
process.out.outputCommands +=['keep *_puJetId*_*_*']
process.out.outputCommands +=['keep *_puJetMva*_*_*']


###################################################
# needed for JEC
###################################################
process.out.outputCommands +=['keep double_kt6PFJets_rho_RECO']
###################################################
# Store the Vertex Collection
# filtering is possible at this
# stage (currently requiring at least one)
###################################################

from PhysicsTools.PatAlgos.tools.coreTools import *
from PhysicsTools.PatAlgos.tools.trackTools import *

process.VertexPresent = cms.EDFilter("VertexSelector",
                             src = cms.InputTag("offlinePrimaryVertices"),
                             cut = cms.string("!isFake && ndof > 4 && abs(z) < 24 && position.Rho < 2"),
                             filter = cms.bool(True)
                             )

process.out.outputCommands +=['keep *_offlinePrimaryVertices*_*_*']
process.out.outputCommands +=['drop *_offlinePrimaryVerticesWithBS*_*_*']
process.out.outputCommands +=['keep *_generalTracks_*_*']
process.out.outputCommands +=['keep TupleUserSpecifiedDatas_UserSpecifiedData_TupleUserSpecifiedData_PAT']


###################################################
# add info needed for pile-up reweight
####################################################
process.out.outputCommands +=['keep *_addPileupInfo*_*_*']
###################################################

###################################################
# keep beamspot (may be needed for electron ID)
###################################################

process.out.outputCommands +=['keep *_offlineBeamSpot*_*_*']



###################################################
# Store the Muons
###################################################

# https://twiki.cern.ch/twiki/bin/view/Main/SingleTopHiggsBBEventSel
# setting to 9999 eliminates the default filtering w.r.t the 1st vertex in
# the vertex src list; there is no gaurantee that the 1st vertex is the
# one that we will end up selecting

process.pfMuonsFromVertex.d0Cut = 9999.
process.pfMuonsFromVertex.d0SigCut = 9999.
process.pfMuonsFromVertex.dzCut = 9999.
process.pfMuonsFromVertex.dzSigCut = 9999.

process.out.outputCommands +=['keep *_selectedPatMuons*_*_*']






###################################################
# store electrons and MVA ID
###################################################


process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
process.mvaIDelec = cms.Sequence(  process.mvaTrigV0 + process.mvaNonTrigV0 + process.mvaTrigNoIPV0 )
process.patElectrons.electronIDSources.mvaTrigV0    = cms.InputTag("mvaTrigV0")
process.patElectrons.electronIDSources.mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0")
process.patElectrons.electronIDSources.mvaTrigNoIPV0 = cms.InputTag("mvaTrigNoIPV0")

process.patPF2PATSequence.replace( process.patElectrons, process.mvaIDelec * process.patElectrons )

process.out.outputCommands +=['keep *_selectedPatElectrons*_*_*']


###################################################
# keep conversion info and gsf electrons just in
# case they are needed
###################################################

process.patConversions = cms.EDProducer("PATConversionProducer",
                                        electronSource = cms.InputTag("gsfElectrons")
                                        )
#process.out.outputCommands +=['keep *_patConversions*_*_*']
#process.out.outputCommands +=['keep *_conversions*_*_*']
#process.out.outputCommands +=['keep *_gsfElectrons*_*_*']


###################################################
# MVA MET (this must be before muon and electron sequences, don't
# understand why at this point)
###################################################



process.patPFMetByMVA = process.patMETs.clone(
    metSource = cms.InputTag('pfMEtMVA'),
    addMuonCorrections = cms.bool(True),
    genMETSource = cms.InputTag('genMetTrue')
)

process.load("JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi")
process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")


###################################################
# add in hadronic taus
# based on
# https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePFTauID#5_3_12_and_higher
###################################################
###################################################
# tau discriminators must be re-run
###################################################

process.load("Configuration.Geometry.GeometryPilot2_cff")
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

#process.load("CommonTools.ParticleFlow.pfTaus_cff")

from PhysicsTools.PatAlgos.tools.tauTools import *
switchToPFTauHPS(process)

process.out.outputCommands += ['keep *_selectedPatTaus*_*_*']
########################################################


process.mvametPF2PATsequence = cms.Sequence(
                process.PFTau*
                process.pfMEtMVAsequence*
                # next 2 lines are from
                # https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#METSysTools
                process.type0PFMEtCorrection*
                process.patPFMETtype0Corr*
                getattr(process,"patPF2PATSequence"+postfix)*
                process.patPFMetByMVA
                                )


process.out.outputCommands +=['keep *_pfMEtMVA*_*_*']
process.out.outputCommands +=['keep *_patPFMetByMVA*_*_*']

# keep CSV info
process.out.outputCommands +=['keep *_combinedSecondaryVertexBJetTagsAOD_*_*']

###################################################
# apply selection cuts on physics objects
# to keep that PATtuple to a reasonable kB/event
###################################################


from PhysicsTools.PatAlgos.selectionLayer1.jetSelector_cfi import *
process.selectedPatJets = selectedPatJets.clone(src = 'patJets', cut = 'correctedP4(0).pt > 10. && abs(eta)<4.7')

from PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi import *
process.selectedPatTaus = selectedPatTaus.clone(src = 'patTaus', cut = 'pt >18. && decayMode>-1')


from PhysicsTools.PatAlgos.selectionLayer1.muonSelector_cfi import *
process.selectedPatMuons = selectedPatMuons.clone(src = 'patMuons', cut = 'pt >3.')


from PhysicsTools.PatAlgos.selectionLayer1.electronSelector_cfi import *
process.selectedPatElectrons = selectedPatElectrons.clone(src = 'patElectrons', cut = 'et >8.')






###################################################
# drop some large unused collections
###################################################

process.out.outputCommands +=['drop patPFParticles_selectedPatPFParticles__PAT']
process.out.outputCommands +=['drop recoPFCandidates_selectedPatJets_pfCandidates_PAT']

###################################################
# require at least two lepton candidates
# in the event
###################################################


# module to filter on the number of Electrons
process.countSelectedLeptons = cms.EDFilter("PATLeptonCountFilter",
  electronSource = cms.InputTag("selectedPatElectrons"),
  muonSource     = cms.InputTag("selectedPatMuons"),
  tauSource      = cms.InputTag("selectedPatTaus"),
  countElectrons = cms.bool(True),
  countMuons     = cms.bool(True),
  countTaus      = cms.bool(True),
  minNumber = cms.uint32(2),
  maxNumber = cms.uint32(999999),
  filter = cms.bool(True)
)


##################################################
# run the MET systematic tool
##################################################

# apply type I/type I + II PFMEt corrections to pat::MET object
# and estimate systematic uncertainties on MET
from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
runMEtUncertainties(process,
      electronCollection  = cms.InputTag('selectedPatElectrons'),
      muonCollection  = cms.InputTag('selectedPatMuons'),
      tauCollection  = cms.InputTag('selectedPatTaus'),
      jetCollection  = cms.InputTag('selectedPatJets'),
      makePFMEtByMVA = True,
      doSmearJets = False
                    )








##################################################
# Let it run
###################################################
process.p = cms.Path(
                             process.UserSpecifiedData+
                             process.VertexPresent+
                             process.mvametPF2PATsequence+
                             process.recoTauClassicHPSSequence+
                             process.puJetIdSqeuence+
                             process.countSelectedLeptons
                                  )



if RunMETUnc:
  process.p += process.metUncertaintySequence

else:
  process.out.outputCommands +=['drop recoPFCandidates_*_*_*']
  process.out.outputCommands +=['keep recoPFCandidates_particleFlow__RECO']
  process.out.outputCommands +=['keep recoPFJets_calibratedAK5PFJetsForPFMEtMVA__PAT']
  process.out.outputCommands +=['keep recoPFJets_ak5PFJets__RECO']
  process.out.outputCommands +=['keep recoPFMETs_pfMet__RECO']
  process.out.outputCommands +=['keep recoGenMETs_genMetTrue__SIM']
  process.out.outputCommands +=['keep recoPFCandidates_selectedPatJets_pfCandidates_PAT']
  process.out.outputCommands +=['keep recoMuons_muons__RECO']
  process.out.outputCommands +=['keep recoGsfTracks_electronGsfTracks__RECO']
  process.out.outputCommands +=['keep *_ak5GenJetsNoNu_*_PAT']
  process.out.outputCommands +=['keep *_*genParticlesForJetsNoNu*_*_PAT']
  process.out.outputCommands +=['keep *_*iterativeCone5GenJetsNoNu*_*_PAT']
  process.out.outputCommands +=['keep recoGenParticles*_*_*_*']

if runOnMC:
    process.p += process.genForPF2PATSequence
    process.out.outputCommands +=['keep GenEventInfoProduct_generator__SIM']
    # the above is needed for the PDF sys. tool


###################################################
# require all paths to pass
###################################################

process.out.SelectEvents.SelectEvents = ['p']



########################################################################################################
if KeepAll:
  process.out.outputCommands +=['keep *_*_*_*']
########################################################################################################
process.out.fileName = '/uscms/home/shalhout/no_backup/patTuple_testing.root'

########################################################################################################
myfilelist = cms.untracked.vstring()
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/00E903E2-9FE9-E111-8B1E-003048FF86CA.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/085027A0-63E9-E111-BA2C-0018F3D09670.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/0E3688C3-98E9-E111-8FC6-003048FFCBB0.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/1289637A-69E9-E111-B26D-003048678F84.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/12A21961-B3E9-E111-AA11-00261894394D.root'])

process.source = cms.Source ("PoolSource",
                      fileNames=myfilelist,
                        dropDescendantsOfDroppedBranches = cms.untracked.bool(False),
                        inputCommands = cms.untracked.vstring(
                        'keep *',
                        'drop recoPFTaus_*_*_*'
                        ),
		                  skipEvents=cms.untracked.uint32(0)
			                       )
########################################################################################################


process.maxEvents.input = 10
########################################################################################################
