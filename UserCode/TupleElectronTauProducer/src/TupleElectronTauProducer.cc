// -*- C++ -*-
//
// Package:    TupleElectronTauProducer
// Class:      TupleElectronTauProducer
//
/**\class TupleElectronTauProducer TupleElectronTauProducer.cc TEMP/TupleElectronTauProducer/src/TupleElectronTauProducer.cc

Description: [one line class summary]

Implementation:
[Notes on implementation]
*/
//
// Original Author:  shalhout shalhout
//         Created:  Fri Jun 27 04:29:18 CDT 2014
// $Id$
//
//


// system include files
#include <memory>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

// needed by ntuple tau producer
#include <vector>
#include <iostream>
#include "DataFormats/Math/interface/LorentzVector.h"
#include "UserCode/TupleObjects/interface/TupleTau.h"
#include "UserCode/TupleObjects/interface/TupleElectron.h"
#include "UserCode/TupleObjects/interface/TupleElectronTau.h"
#include "TauAnalysis/CandidateTools/interface/NSVfitStandaloneAlgorithm.h"
#include "TLorentzVector.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "Math/GenVector/VectorUtil.h"
#include "DataFormats/PatCandidates/interface/MET.h"
#include "DataFormats/METReco/interface/PFMET.h"
#include "DataFormats/METReco/interface/PFMETCollection.h"
#include "UserCode/RecoilCorrector/interface/RecoilCorrector.hh"
#include "UserCode/GenBosonDecayFinder/interface/GenBosonDecayFinder.hh"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/JetReco/interface/Jet.h"
#include "DataFormats/Math/interface/deltaPhi.h"
#include "UserCode/TupleHelpers/interface/TupleHelpers.hh"
#include "DataFormats/PatCandidates/interface/Jet.h"
#include "DataFormats/JetReco/interface/PileupJetIdentifier.h"


typedef math::XYZTLorentzVector LorentzVector;
using namespace std;
using namespace edm;



//
// class declaration
//

class TupleElectronTauProducer : public edm::EDProducer {
public:
  explicit TupleElectronTauProducer(const edm::ParameterSet&);
  ~TupleElectronTauProducer();

  static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);

private:
  virtual void beginJob() ;
  virtual void produce(edm::Event&, const edm::EventSetup&);
  virtual void endJob() ;

  virtual void beginRun(edm::Run&, edm::EventSetup const&);
  virtual void endRun(edm::Run&, edm::EventSetup const&);
  virtual void beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);
  virtual void endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&);

  // ----------member data ---------------------------

  edm::InputTag tauSrc_;
  edm::InputTag electronSrc_;
  edm::InputTag mvametSrc_;
  edm::InputTag genSrc_;
  edm::InputTag jetSrc_;
  double iFluc_;
  double iScale_;
  string NAME_;
  edm::InputTag puJetIdMVASrc_;
  edm::InputTag puJetIdFlagSrc_;
  bool doSVFit_;


};

//
// constants, enums and typedefs
//


//
// static data member definitions
//

//
// constructors and destructor
//
TupleElectronTauProducer::TupleElectronTauProducer(const edm::ParameterSet& iConfig):
tauSrc_(iConfig.getParameter<edm::InputTag>("tauSrc" )),
electronSrc_(iConfig.getParameter<edm::InputTag>("electronSrc" )),
mvametSrc_(iConfig.getParameter<edm::InputTag>("mvametSrc" )),
genSrc_(iConfig.getParameter<edm::InputTag>("genSrc" )),
jetSrc_(iConfig.getParameter<edm::InputTag>("jetSrc" )),
iFluc_(iConfig.getParameter<double>("iFluc" )),
iScale_(iConfig.getParameter<double>("iScale" )),
NAME_(iConfig.getParameter<string>("NAME" )),
puJetIdMVASrc_(iConfig.getParameter<edm::InputTag>("puJetIdMVASrc" )),
puJetIdFlagSrc_(iConfig.getParameter<edm::InputTag>("puJetIdFlagSrc" )),
doSVFit_(iConfig.getParameter<bool>("doSVFit" ))
{


  produces< vector<TupleElectronTau> >(NAME_).setBranchAlias(NAME_);


  //register your products
  /* Examples
  produces<ExampleData2>();

  //if do put with a label
  produces<ExampleData2>("label");

  //if you want to put into the Run
  produces<ExampleData2,InRun>();
  */
  //now do what ever other initialization is needed

}


TupleElectronTauProducer::~TupleElectronTauProducer()
{

  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
TupleElectronTauProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{



  // get tuple electron and tau and jet collections


  edm::Handle< TupleElectronCollection > electrons;
  iEvent.getByLabel(electronSrc_, electrons);

  edm::Handle< TupleTauCollection > taus;
  iEvent.getByLabel(tauSrc_, taus);

  edm::Handle<edm::View<pat::Jet> > jets;
  iEvent.getByLabel(jetSrc_,jets);

  std::size_t njet = jets->size();

  ///////////////////////////////////////
  // figure out how many of these jets
  // pass the loose WP - should be moved since used twice
  // here and in muTau producer



  edm::Handle<ValueMap<float> > puJetIdMVA;
  iEvent.getByLabel(puJetIdMVASrc_,puJetIdMVA);


  edm::Handle<ValueMap<int> > puJetIdFlag;
  iEvent.getByLabel(puJetIdFlagSrc_,puJetIdFlag);


  njet = 0;

  for ( unsigned int i=0; i<jets->size(); ++i )
  {
    const pat::Jet & patjet = jets->at(i);
    float mva   = (*puJetIdMVA)[jets->refAt(i)];
    int    idflag = (*puJetIdFlag)[jets->refAt(i)];
    if(PileupJetIdentifier::passJetId( idflag, PileupJetIdentifier::kLoose )) njet++;
  }


  ///////////////////////////////////


  // get the mva met

  edm::Handle<std::vector<reco::PFMET> > mvamet;
  iEvent.getByLabel(mvametSrc_, mvamet);

  // get the gen particles

  edm::Handle<std::vector<reco::GenParticle> > gen;
  iEvent.getByLabel(genSrc_, gen);

  // print the parameters passed by the config file

  cout<<" NAME_, iFluc_, iScale_ "<<NAME_<<" "<<iFluc_<<" "<<iScale_<<endl;

  ////////////

  auto_ptr<TupleElectronTauCollection> TupleElectronTaus (new TupleElectronTauCollection);

  const int TupleElectronTauSize = electrons->size();
  TupleElectronTaus->reserve( TupleElectronTauSize );
  const reco::PFMET mvaMETpf =  (*mvamet)[0];


  // declare & init to raw value before applying recoil corrections
  NSVfitStandalone::Vector NSVcorrectedMET = mvaMETpf.momentum();
  math::PtEtaPhiMLorentzVector correctedMET(mvaMETpf.pt(),0.0,mvaMETpf.phi(),0.0);

  ///////////////////
  // find max pt pair

  std::size_t max_i = 0;
  std::size_t max_j = 0;
  int max_pt = -999;

  for (std::size_t i = 0; i < electrons->size(); ++i)
  {

    const TupleElectron electron =   ((*electrons)[i]);

    for (std::size_t j = 0; j < taus->size(); ++j)
    {

      const TupleTau tau =   ((*taus)[j]);

      if(tau.passFullId_eTau() && electron.passFullId())
      { // temp

        if(tau.p4().pt()+electron.p4().pt() >= max_pt)
        {
          max_pt = (tau.p4().pt()+electron.p4().pt());
          max_i = i;
          max_j = j;
        }

      }
    }
  }

  for (std::size_t i = 0; i < electrons->size(); ++i)
  {

    const TupleElectron electron =   ((*electrons)[i]);

    for (std::size_t j = 0; j < taus->size(); ++j)
    {

      const TupleTau tau =   ((*taus)[j]);

      if(tau.passFullId_eTau() && electron.passFullId())
      { // temp


        cout<<" i,j = "<<i<<","<<j;
        cout<<" electron PDGID (pf) "<<electron.PFpdgId();
        cout<<" tau PDGID (pf) "<<tau.pdgId()<<endl;


        TupleElectronTau CurrentElectronTau;

        if(max_i == i && max_j == j) CurrentElectronTau.set_MAX(1);
        else CurrentElectronTau.set_MAX(2);


        CurrentElectronTau.set_p4(  electron.p4() + tau.p4() );
        CurrentElectronTau.set_electronIndex(i);
        CurrentElectronTau.set_tauIndex(j);
        std::cout<<" TAU ES corrections are not applied "<<std::endl;
        CurrentElectronTau.set_corrected_p4( electron.p4() + tau.p4()   );
        CurrentElectronTau.set_scalarSumPt(electron.p4() , tau.p4()  );
        CurrentElectronTau.set_DR(electron.p4() , tau.p4()  );
        CurrentElectronTau.set_mvaMETraw(mvaMETpf.pt());
        CurrentElectronTau.set_mvaMETphiRaw(mvaMETpf.phi());


        //      CurrentElectronTau.set_corrected_p4( electron.p4() + tau.corrected_p4()   );
        //      CurrentElectronTau.set_scalarSumPt(electron.p4() , tau.corrected_p4()  );
        //      CurrentElectronTau.set_DR(electron.p4() , tau.corrected_p4()  );
        CurrentElectronTau.set_sumCharge(electron.charge() , tau.charge()  );

        ////////////
        // apply Phil's recoil
        // corrections to the MET before
        // running SVFit to MC only

        if( !iEvent.isRealData() )
        {
          double met=mvaMETpf.pt();
          double metphi=mvaMETpf.phi();
          //        double leptonPt = ( electron.p4() + tau.corrected_p4()   ).pt();
          //        double leptonPhi  = ( electron.p4() + tau.corrected_p4()   ).phi();
          cout<<" Warning, may not be using correct pdgIds for Recoil correction \n turned off tau ES correction"<<endl;
          double leptonPt = ( electron.p4() + tau.p4()   ).pt();
          double leptonPhi  = ( electron.p4() + tau.p4()   ).phi();

          double GenZPt = 0.0;
          double GenZPhi = 0.0;
          double iU1 = 0.0;
          double iU2 = 0.0;

          ////////////////
          // There are specific corrections
          // for H->tau tau, W, Z, and Zmm.
          // As of Summer 2013, H,W, and Z use 53X_20pv
          // while Zmm uses 53X_2012 for the process.
          // For data Zmm and simulated Zmm, we use 53X_2012.
          // The function genDecayFinder can figure out the process
          // while whichRecoilCorrectionFiles will return the
          // correct set of files for the correction

          int BosonPdgId = 0;
          LorentzVector BosonP4(0,0,0,0);
          int DaughterOnePdgId = 0;
          LorentzVector DaughterOneP4(0,0,0,0);
          int DaughterTwoPdgId = 0;
          LorentzVector DaughterTwoP4(0,0,0,0);
          bool ApplyRecoilCorrection = 1;


          GenBosonDecayFinder genDecayFinder;
          genDecayFinder.findBosonAndDaugters(*gen,BosonPdgId,BosonP4,DaughterOnePdgId,
          DaughterOneP4,DaughterTwoPdgId,
          DaughterTwoP4,ApplyRecoilCorrection);

          cout<<BosonPdgId<<" = BosonPdgId "<<endl;
          cout<<DaughterOnePdgId<<" = DaughterOnePdgId "<<endl;
          cout<<DaughterTwoPdgId<<" = DaughterTwoPdgId "<<endl;
          cout<<ApplyRecoilCorrection<<" = ApplyRecoilCorrection "<<endl;


          if(ApplyRecoilCorrection)
          {

            GenZPt = (DaughterOneP4+DaughterTwoP4).pt();
            GenZPhi = (DaughterOneP4+DaughterTwoP4).phi();

            std::string DataFile;
            std::string MCFile;
            std::string ProcessFile;



            whichRecoilCorrectionFiles(BosonPdgId, DaughterOnePdgId,
            DaughterTwoPdgId, njet, ProcessFile, DataFile, MCFile);

            cout<<" files = "<<ProcessFile<<" "<<DataFile<<" "<<MCFile<<endl;

            // not sure what random seed we should be using?
            // do we really want it to be random?
            cout<<" applying recoil corrections with random seed : 0xDEADBEEF"<<endl;

            RecoilCorrector corrector(ProcessFile,0xDEADBEEF);
            corrector.addDataFile(DataFile);
            corrector.addMCFile(MCFile);

            //////////////////////
            // print out the uncorrected value
            cout<<" Before Correction : "<<met<<" "<<metphi<<endl;

            corrector.CorrectType1(  met,
            metphi,
            GenZPt,
            GenZPhi,
            leptonPt,
            leptonPhi,
            iU1,
            iU2,
            iFluc_,
            iScale_,
            njet);

            correctedMET.SetPt(met);
            correctedMET.SetEta(0.0);
            correctedMET.SetPhi(metphi);
            correctedMET.SetM(0.0);
            NSVcorrectedMET.SetXYZ(correctedMET.x(),correctedMET.y(),correctedMET.z());

            //////////////////////
            // print out the corrected value
            cout<<" Post Correction : "<<met<<" "<<metphi<<endl;
          }


        }


        ////////////////
        double Mt = TupleHelpers::GetTransverseMass(electron.p4(), NSVcorrectedMET);
        CurrentElectronTau.set_TransverseMass(Mt);

        cout<<" transverse mass  = "<<Mt<<endl;
        ////////////////

        TMatrixD covMET(2, 2); // PFMET significance matrix
        std::vector<NSVfitStandalone::MeasuredTauLepton> measuredTauLeptons;

        ///////
        // it seems the order matters
        // pass the higher pt lepton 1st

        if( electron.p4().pt() >=  tau.p4().pt()  )
        //      if( electron.p4().pt() >=  tau.corrected_p4().pt()  )
        {
          measuredTauLeptons.push_back(NSVfitStandalone::MeasuredTauLepton(NSVfitStandalone::kLepDecay,
          electron.p4()) );
          measuredTauLeptons.push_back(NSVfitStandalone::MeasuredTauLepton(NSVfitStandalone::kHadDecay,
          tau.p4()));
          //        tau.corrected_p4()));
        }

        else
        {
          measuredTauLeptons.push_back(NSVfitStandalone::MeasuredTauLepton(NSVfitStandalone::kHadDecay,
          tau.p4()));
          //        tau.corrected_p4()));
          measuredTauLeptons.push_back(NSVfitStandalone::MeasuredTauLepton(NSVfitStandalone::kLepDecay,
          electron.p4()) );


        }

        // store the met
        CurrentElectronTau.set_mvaMET(correctedMET.pt());
        CurrentElectronTau.set_mvaMETphi(correctedMET.phi());

        covMET = mvaMETpf.getSignificanceMatrix();


        if(doSVFit_)
        {
          // last argument is verbosity
          NSVfitStandaloneAlgorithm algo(measuredTauLeptons, NSVcorrectedMET, covMET, 0);
          algo.addLogM(false);
          algo.integrateMarkovChain();

          //algo.integrateVEGAS(); ////Use this instead for VEGAS integration

          CurrentElectronTau.set_correctedSVFitMass(algo.getMass());

          //cout<<" diTauMassErr "<<algo.getMassUncert();
          //cout<<" diTauPt "<<algo.getPt();
          //cout<<" diTauPtErr "<<algo.getPtUncert();
        }
        else CurrentElectronTau.set_correctedSVFitMass(0.0);
        measuredTauLeptons.clear();

        ////////////
        // store the ElectronTau

        TupleElectronTaus->push_back(CurrentElectronTau);

      } //temp

    }

  }

  iEvent.put( TupleElectronTaus, NAME_ );

  /* This is an event example
  //Read 'ExampleData' from the Event
  Handle<ExampleData> pIn;
  iEvent.getByLabel("example",pIn);

  //Use the ExampleData to create an ExampleData2 which
  // is put into the Event
  std::auto_ptr<ExampleData2> pOut(new ExampleData2(*pIn));
  iEvent.put(pOut);
  */

  /* this is an EventSetup example
  //Read SetupData from the SetupRecord in the EventSetup
  ESHandle<SetupData> pSetup;
  iSetup.get<SetupRecord>().get(pSetup);
  */

}

// ------------ method called once each job just before starting event loop  ------------
void
TupleElectronTauProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
TupleElectronTauProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void
TupleElectronTauProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
TupleElectronTauProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
TupleElectronTauProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
TupleElectronTauProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
TupleElectronTauProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(TupleElectronTauProducer);