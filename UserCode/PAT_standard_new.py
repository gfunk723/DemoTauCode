########################################################################################################
import FWCore.ParameterSet.Config as cms
from PhysicsTools.PatAlgos.patTemplate_cfg import *
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
########################################################################################################


SampleName_='SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/AODSIM'
PhysicsProcess_='ggA0tautau[SUSY_120_8TeV]'
MASS_=120.0
isNonTopEmbeddedSample_ = False
isTopEmbeddedSample_ = False
runOnMC = True # true for MC, and all topTopBar and Ztautau embedded samples
branchingFraction_ = 999.99
crossSection_ = 999.99
numberEvents_ = 999

FilterEvents = True
DropSelectedPatObjects = True
KeepAll = False
PrintProductIDs = False

###################################################
# Store SampleName and PhysicsProcess
# eventually these should be command line
# options
###################################################

process.UserSpecifiedData = cms.EDProducer('TupleUserSpecifiedDataProducer',
                                            SampleName=cms.string(SampleName_),
                                            PhysicsProcess=cms.string(PhysicsProcess_),
                                            isNonTopEmbeddedSample=cms.bool(isNonTopEmbeddedSample_),
                                            isTopEmbeddedSample=cms.bool(isTopEmbeddedSample_),
                                            MASS=cms.double(MASS_),
                                            crossSection=cms.double(crossSection_),
                                            branchingFraction=cms.double(branchingFraction_),
                                            numberEvents=cms.int32(numberEvents_)
                                            )

###################################################
# need to get the correct version of the global
# tag and set JEC to match, also remove MC matching
# for data
###################################################
from PhysicsTools.PatAlgos.tools.coreTools import *


if runOnMC:
  process.GlobalTag.globaltag = 'START53_V23::All'
else:
  process.GlobalTag.globaltag = 'FT_53_V21_AN4::All'
  removeMCMatching(process, ['All'])
  runOnData(process)

if isNonTopEmbeddedSample_:
  process.GlobalTag.globaltag = 'FT_53_V21_AN4::All'
#  runOnData(process)



###################################################
# set the JEC level for MC or DATA
###################################################


jetEnCorr = ['L1FastJet', 'L2Relative', 'L3Absolute']

if not runOnMC:
  jetEnCorr.extend(['L2L3Residual'])

if isNonTopEmbeddedSample_:
  jetEnCorr.extend(['L2L3Residual'])

#####################################
# compute the tau spinner weights
#####################################

process.load("TauSpinnerInterface.TauSpinnerInterface.TauSpinner_cfi")


###################################################
# debug info including productId will be printed
###################################################

process.printEventContent = cms.EDAnalyzer("EventContentAnalyzer")







###################################################
# pu jet id requires PF jets as input
###################################################

from PhysicsTools.PatAlgos.tools.jetTools import *

###################################################
# must rerun b-tagging at PAT creation
# in order to get embedded sample b-tags correct
###################################################

process.patJets.addTagInfos = True
process.load('RecoBTag.Configuration.RecoBTag_cff')
process.load('RecoJets.JetAssociationProducers.ak5JTA_cff')

###################################################
# special case stuff for embedded samples
###################################################

if isNonTopEmbeddedSample_ or isTopEmbeddedSample_:
        print "EMBEDDED SETTING "
        process.ak5JetTracksAssociatorAtVertex.tracks = cms.InputTag("tmfTracks")
        process.ak5JetTracksAssociatorAtVertex.jets = cms.InputTag("ak5PFJets")


switchJetCollection(process,cms.InputTag('ak5PFJets'),
                 doJTA        = True,
                 doBTagging   = True,
                 jetCorrLabel = ('AK5PF', jetEnCorr),
                 doType1MET   = False,
                 genJetCollection=cms.InputTag("ak5GenJets"),
                 doJetID      = True
                 )

###################################################
# load the PU JetID sequence
###################################################

process.load("RecoJets.JetProducers.pujetidsequence_cff")

###################################################
# keep PU jet id
###################################################

process.out.outputCommands +=['keep *_selectedPatJets*_*_*']
process.out.outputCommands +=['keep *_puJetId*_*_*']
process.out.outputCommands +=['keep *_puJetMva*_*_*']


###################################################
# setup electron pfIsolation, without this the
# standard PAT access via chargedHadronIso etc.
# will return -1
###################################################
from PhysicsTools.PatAlgos.tools.pfTools import *

process.patElectrons.pfElectronSource = 'particleFlow'
process.patElectrons.embedTrack = True
process.eleIsoSequence = setupPFElectronIso(process, 'gsfElectrons', '')
process.muIsoSequence  = setupPFMuonIso(process, 'muons', '')
adaptPFIsoMuons(process, applyPostfix(process,"patMuons",""), '')
adaptPFIsoElectrons(process, applyPostfix(process,"patElectrons",""), '')



usePFIso(process)
#process.patElectrons.pfElectronSource = 'particleFlow'


##################################################
# MVA MET
###################################################
from RecoMET.METPUSubtraction.mvaPFMET_leptons_PAT_cfi import *
process.load('JetMETCorrections.Configuration.JetCorrectionProducers_cff')
process.load('RecoMET.METPUSubtraction.mvaPFMET_leptons_cff')




#process.pfMEtMVA = process.pfMEtMVA.clone(srcLeptons = cms.VInputTag("isomuons","isoelectrons","isotaus"))
#process.patPFMetByMVA = process.patMETs.clone(
#    metSource = cms.InputTag('pfMEtMVA'),
#    addMuonCorrections = cms.bool(True),
#    genMETSource = cms.InputTag('genMetTrue')
#                                                )

# match to LLR

process.pfMEtMVA = process.pfMEtMVA.clone(
    #srcLeptons = cms.VInputTag("isomuons","isoelectrons","isotaus"),
    useType1 = cms.bool(False))
process.patPFMetByMVA = process.patMETs.clone(
    metSource = cms.InputTag('pfMEtMVA'),
    addMuonCorrections = cms.bool(False),
    genMETSource = cms.InputTag('genMetTrue')
                                                )

process.load("JetMETCorrections.Type1MET.pfMETCorrectionType0_cfi")
process.load("PhysicsTools.PatUtils.patPFMETCorrections_cff")

process.mvametPF2PATsequence = cms.Sequence(
                process.pfMEtMVAsequence*
                # next 2 lines are from
                # https://twiki.cern.ch/twiki/bin/view/CMSPublic/SWGuidePATTools#METSysTools
                process.type0PFMEtCorrection*
                process.patPFMETtype0Corr
                                )


process.out.outputCommands +=['keep *_pfMEtMVA*_*_*']
process.out.outputCommands +=['keep *_patPFMetByMVA*_*_*']









###################################################
# needed for JEC
###################################################
process.out.outputCommands +=['keep double_kt6PFJets_rho_RECO']

###################################################
# Store the Vertex Collection
# filtering is possible at this
# stage (currently requiring at least one)
###################################################

from PhysicsTools.PatAlgos.tools.trackTools import *

process.VertexPresent = cms.EDFilter("VertexSelector",
                             src = cms.InputTag("offlinePrimaryVertices"),
                             cut = cms.string("!isFake && ndof > 4 && abs(z) < 24 && position.Rho < 2"),
                             filter = cms.bool(True)
                             )

process.out.outputCommands +=['keep *_offlinePrimaryVertices*_*_*']
process.out.outputCommands +=['keep *_offlinePrimaryVerticesWithBS*_*_*']
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
# need for PDF sys tool
###################################################
if runOnMC:
    process.out.outputCommands +=['keep GenEventInfoProduct_generator__SIM']

###################################################
# the new Tau ID
###################################################
process.load("RecoTauTag.Configuration.RecoPFTauTag_cff")

from PhysicsTools.PatAlgos.tools.tauTools import *
switchToPFTauHPS(process)

#########################
# embedded sample settings
#########################

if isNonTopEmbeddedSample_ or isTopEmbeddedSample_:
  print "EMBEDDED SETTING "
  process.hpsPFTauPrimaryVertexProducer.TrackCollectionTag = cms.InputTag("tmfTracks")

process.cleanPatTaus.preselection = 'pt>17 & abs(eta)<2.4'\
+ '& ( tauID("byLooseCombinedIsolationDeltaBetaCorr3Hits") > 0.5 | tauID("byVLooseIsolationMVA3oldDMwLT") > 0.5 )'\
+ ' & ( tauID("againstElectronLoose")>0.5 | tauID("againstElectronVLooseMVA5")>0.5 )'\
+ ' & ( tauID("againstMuonLoose3")>0.5 | tauID("againstMuonLooseMVA")>0.5 )'


###################################################
# the MVA electron ID
###################################################


process.load('EgammaAnalysis.ElectronTools.electronIdMVAProducer_cfi')
process.mvaID = cms.Sequence(  process.mvaTrigV0 + process.mvaTrigNoIPV0 + process.mvaNonTrigV0 )


process.patElectrons.electronIDSources = cms.PSet(
    mvaTrigV0 = cms.InputTag("mvaTrigV0"),
    mvaNonTrigV0 = cms.InputTag("mvaNonTrigV0"),
    mvaTrigNoIPV0 = cms.InputTag("mvaTrigNoIPV0"),
    )


process.patConversions = cms.EDProducer("PATConversionProducer",
                                        # input collection
                                        # this should be whatever the final analysis-level
                                        # electrons are
                                        electronSource = cms.InputTag("cleanPatElectrons")
                                        )


process.out.outputCommands +=['keep *_patConversions*_*_*']
process.out.outputCommands +=['keep *_conversions*_*_*']
#process.out.outputCommands +=['keep *_gsfElectrons*_*_*']




###################################################
# apply selection cuts on physics objects
# to keep that PATtuple to a reasonable size
###################################################

#from PhysicsTools.PatAlgos.cleaningLayer1.cleanPatCandidates_cff import *
from PhysicsTools.PatAlgos.selectionLayer1.tauSelector_cfi import *
process.countMyPatTaus = selectedPatTaus.clone(src = 'cleanPatTaus',
            cut = cms.string("pt>17 && abs(eta)<2.4"+
            " && ( tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') > 0.5 || tauID('byVLooseIsolationMVA3oldDMwLT') > 0.5 )"+
            " && ( tauID('againstElectronLoose')>0.5 || tauID('againstElectronVLooseMVA5')>0.5 )"+
            " && ( tauID('againstMuonLoose3')>0.5 || tauID('againstMuonLooseMVA')>0.5 )")
                                                )


from PhysicsTools.PatAlgos.selectionLayer1.muonSelector_cfi import *
process.myCleanPatMuons = selectedPatMuons.clone(src = 'cleanPatMuons',
cut = cms.string("pt > 10"+
                 " && abs(eta) < 2.4"
                +" && isPFMuon"
                +" && isTrackerMuon "
                +" && isGlobalMuon "
                +" && (pfIsolationR04.sumChargedParticlePt +"
                +"max(pfIsolationR04.sumNeutralHadronEt+pfIsolationR04.sumPhotonEt-0.5*pfIsolationR04.sumPUPt,0.0))/pt < 0.3"
                )
                                                  )

#########################################################################
# cleanPatElectron passing selection counter
#########################################################################
# we count those electrons in cleanPatElectrons that pass the following ID,
# but keep the entire collection as we need to veto diElectron
# events using looser cuts (could change this later)

from PhysicsTools.PatAlgos.selectionLayer1.electronSelector_cfi import *
process.countMyPatElectrons = selectedPatElectrons.clone(src = 'cleanPatElectrons',
      cut = cms.string("et > 20 * 0.9"+
                       " && gsfTrack.trackerExpectedHitsInner.numberOfLostHits == 0"+
                       " && abs(eta) < 2.1 * 1.1" +
                       " && electronID('mvaNonTrigV0') >= 0.85 " +
                       " && passConversionVeto " +
                       " && (chargedHadronIso + max(neutralHadronIso+photonIso-0.5*puChargedHadronIso,0.0))/pt < 0.2 "
                      )
                                                        )



###################################################
# require an eTau or MuTau pair in the event
###################################################


process.countGoodPairs = cms.EDFilter("PatMuonTauOrElectronTauFilter",
  electronSource = cms.InputTag("countMyPatElectrons"),
  muonSource     = cms.InputTag("myCleanPatMuons"),
  tauSource      = cms.InputTag("countMyPatTaus"),
  countElectronTaus = cms.bool(True),
  countMuonTaus     = cms.bool(True),
  filter = cms.bool(True)
)




###################################################
# keep selected and clean collections
###################################################

process.out.outputCommands +=['keep *_selectedPat*_*_*']
process.out.outputCommands +=['keep *_cleanPat*_*_*']

###################################################
# keeps for MET Unc. Tool
###################################################

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
process.out.outputCommands +=['keep *_*TauSpinnerReco*_*_*']
process.out.outputCommands +=['keep *_*_*_LHE']

if runOnMC:
    process.out.outputCommands +=['keep GenEventInfoProduct_generator__SIM']
  # the above is needed for the PDF sys. tool



##################################################
# stuff needed for the embedded samples
##################################################

process.load('RecoJets.JetAssociationProducers.ak5JTA_cff')

from PhysicsTools.PatAlgos.tools.trigTools import *
switchOnTrigger( process )


if isNonTopEmbeddedSample_ or isTopEmbeddedSample_:
  print "EMBEDDED SETTING "
  process.patTriggerEvent.processName = 'HLT'



if runOnMC and not isNonTopEmbeddedSample_:
    process.load("RecoJets.Configuration.GenJetParticles_cff")
    process.load("RecoJets.Configuration.RecoGenJets_cff")
    process.genJetsNoNu = cms.Sequence(process.genParticlesForJetsNoNu* process.ak5GenJetsNoNu)
    process.patDefaultSequence.replace(process.patJetGenJetMatch, process.genJetsNoNu* process.patJetGenJetMatch)
    process.patJetGenJetMatch.matched = cms.InputTag("ak5GenJetsNoNu")


##################################################
# Let it run
###################################################
process.p = cms.Path(process.UserSpecifiedData)
process.p *= process.VertexPresent



process.p *= process.mvaID
process.p *= process.PFTau
process.p *= process.pfNoPileUpSequence
process.p *= process.pfAllMuons
process.p *= process.pfParticleSelectionSequence
process.p *= process.eleIsoSequence
process.p *= process.muIsoSequence
process.p *= process.recoTauClassicHPSSequence
process.p *= process.mvametPF2PATsequence

# always rerun b-tagging before the pat default seq.
process.p *= process.ak5JetTracksAssociatorAtVertex
process.p *= process.btagging

process.p *= process.patDefaultSequence
process.p *= process.patPFMetByMVA
process.p *= process.patConversions
process.p *= process.puJetIdSqeuence
process.p *= process.countMyPatTaus
process.p *= process.countMyPatElectrons
process.p *= process.myCleanPatMuons



if FilterEvents:
  process.p *= process.countGoodPairs

if runOnMC:
  process.p *= process.TauSpinnerReco

if DropSelectedPatObjects:
  process.out.outputCommands +=['drop *_selectedPatElectrons*_*_*']
  process.out.outputCommands +=['drop *_selectedPatMuons*_*_*']
  process.out.outputCommands +=['drop *_selectedPatTaus*_*_*']
  process.out.outputCommands +=['drop *_selectedPatJets*_*_*']
  process.out.outputCommands +=['keep *_cleanPatElectrons*_*_*']
  process.out.outputCommands +=['keep *_cleanPatMuons*_*_*']
  process.out.outputCommands +=['keep *_myCleanPatMuons*_*_*']
  process.out.outputCommands +=['keep *_cleanPatTaus*_*_*']
  process.out.outputCommands +=['keep *_cleanPatJets*_*_*']


# always keep the following, really needed for embedded
process.out.outputCommands +=['keep *_tmfTracks_*_*']
process.out.outputCommands +=['keep *_generator_minVisPtFilter_*']
process.out.outputCommands +=['keep *_generator_*_*']
process.out.outputCommands +=['keep *_particleFlow__*']
process.out.outputCommands +=['keep *_particleFlowDisplacedVertex_*_*']
process.out.outputCommands +=['keep recoMuons_muons__EmbeddedRECO']
process.out.outputCommands +=['keep recoPFJets_ak5PFJets__EmbeddedRECO']
process.out.outputCommands +=['keep recoGsfTracks_electronGsfTracks__EmbeddedRECO']


if PrintProductIDs:
  process.p *= process.printEventContent


###################################################
# require all paths to pass
###################################################

process.out.SelectEvents.SelectEvents = ['p']



###################################################
# add in Trigger Info, according to twiki it should
# be done after all modifications to the path
###################################################

# Trigger Object Matching

process.load( "PhysicsTools.PatAlgos.triggerLayer1.triggerProducer_cff" )

###################################################

process.eTrigMatchEle27 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatElectrons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
                                                       matchedCuts = cms.string( 'path( "HLT_Ele27*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################

process.eTrigMatchEle20 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatElectrons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_Ele20_CaloIdVT_CaloIsoRhoT_TrkIdT_TrkIsoT_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )


###################################################

process.eTrigMatchEle22 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatElectrons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_Ele22_eta2p1_WP90Rho_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################


process.muTrigMatchMu17 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatMuons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_IsoMu17_eta2p1_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################

process.muTrigMatchMu18 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatMuons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_IsoMu18_eta2p1_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################


process.muTrigMatchMu24 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatMuons' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_IsoMu24*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )


####################################################

###################################################

process.tauTrigMatchEle20 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_Ele20_CaloIdVT_CaloIsoRhoT_TrkIdT_TrkIsoT_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )


###################################################

process.tauTrigMatchEle22 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_Ele22_eta2p1_WP90Rho_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################


process.tauTrigMatchMu17 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_IsoMu17_eta2p1_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################

process.tauTrigMatchMu18 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_IsoMu18_eta2p1_LooseIsoPFTau20_v*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################


process.tauTrigMatchJet320 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
            matchedCuts = cms.string( 'path( "HLT_PFJet320*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )


###################################################


process.tauTrigMatchEle27 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
                                                       matchedCuts = cms.string( 'path( "HLT_Ele27*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )

###################################################


process.tauTrigMatchMu24 = cms.EDProducer( "PATTriggerMatcherDRLessByR",
                                                       src = cms.InputTag( 'cleanPatTaus' ),
                                                       matched = cms.InputTag( 'patTrigger' ),
                                                       andOr          = cms.bool( False ),
                                                       matchedCuts = cms.string( 'path( "HLT_IsoMu24*" )' ),
                                                       maxDeltaR = cms.double( 0.5 ),
                                                       resolveAmbiguities = cms.bool( True ),
                                                       resolveByMatchQuality = cms.bool( True )
                                                       )


triggerMatchers = cms.vstring()
triggerMatchers.extend(['eTrigMatchEle20'])
triggerMatchers.extend(['eTrigMatchEle22'])
triggerMatchers.extend(['eTrigMatchEle27'])
triggerMatchers.extend(['muTrigMatchMu17'])
triggerMatchers.extend(['muTrigMatchMu18'])
triggerMatchers.extend(['muTrigMatchMu24'])
triggerMatchers.extend(['tauTrigMatchEle20'])
triggerMatchers.extend(['tauTrigMatchEle22'])
triggerMatchers.extend(['tauTrigMatchEle27'])
triggerMatchers.extend(['tauTrigMatchMu17'])
triggerMatchers.extend(['tauTrigMatchMu18'])
triggerMatchers.extend(['tauTrigMatchMu24'])
triggerMatchers.extend(['tauTrigMatchJet320'])



switchOnTriggerMatching( process, triggerMatchers )
process.out.outputCommands +=['keep *_*patTrigger*_*_*']
process.out.outputCommands +=['keep *_*TriggerResults*_*_*']
process.out.outputCommands +=['keep *_*patTriggerEvent*_*_*']
process.out.outputCommands +=['keep *_*TriggerMatch*_*_*']




########################################################################################################
if KeepAll:
  process.out.outputCommands +=['keep *_*_*_*']
########################################################################################################
process.out.fileName = '/uscms/home/shalhout/no_backup/patTuple_testing.root'

########################################################################################################
myfilelist = cms.untracked.vstring()


myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/02BCF7EF-82E9-E111-9ADC-E41F131815F0.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/04FDED26-AEE9-E111-988D-00215E229636.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/06036C63-AFE9-E111-ABE9-00215E21DD14.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/101C2B09-B4E9-E111-B23B-00215E221170.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/12FFB05B-B5E9-E111-9D2C-00215E21D906.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/18215775-AFE9-E111-9292-00215E2599A6.root'])
myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/SUSYGluGluToHToTauTau_M-120_8TeV-pythia6-tauola/AODSIM/PU_S10_START53_V7A-v1/0000/1AA634AD-A9E9-E111-9189-001A645C208C.root'])


#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/DY1JetsToLL_M-50_TuneZ2Star_8TeV-madgraph/AODSIM/PU_S10_START53_V7A-v1/0000/001318CD-C5F4-E111-AAD9-001E67398D72.root'])
#myfilelist.extend(['file:/uscms/home/shalhout/no_backup/5000.root'])
#myfilelist.extend(['file:/uscms/home/shalhout/1stSteps/Git2/DemoTauCode/CMSSW_5_3_14/src/MyOutputFile.root'])
#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/00E903E2-9FE9-E111-8B1E-003048FF86CA.root'])
#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/085027A0-63E9-E111-BA2C-0018F3D09670.root'])
#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/0E3688C3-98E9-E111-8FC6-003048FFCBB0.root'])
#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/1289637A-69E9-E111-B26D-003048678F84.root'])
#myfilelist.extend(['root://cmsxrootd-site.fnal.gov//store/mc/Summer12_DR53X/GluGluToHToTauTau_M-125_8TeV-powheg-pythia6/AODSIM/PU_S10_START53_V7A-v1/0000/12A21961-B3E9-E111-AA11-00261894394D.root'])

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


process.maxEvents.input = -1
########################################################################################################
