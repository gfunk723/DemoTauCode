// -*- C++ -*-
//
// Package:    SinglePatLeptonProducer
// Class:      SinglePatLeptonProducer
//
/**\class SinglePatLeptonProducer SinglePatLeptonProducer.cc TEMP/SinglePatLeptonProducer/src/SinglePatLeptonProducer.cc

Description: [one line class summary]

Implementation:
[Notes on implementation]
*/
//
// Original Author:  shalhout shalhout
//         Created:  Mon Jul 14 12:35:16 CDT 2014
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

// needed by ntuple electron producer
#include <vector>
#include <iostream>
#include "DataFormats/PatCandidates/interface/Electron.h"
#include "RecoEgamma/EgammaTools/interface/ConversionTools.h"
#include "EgammaAnalysis/ElectronTools/interface/EGammaCutBasedEleId.h"
#include "DataFormats/PatCandidates/interface/Conversion.h"
#include "DataFormats/PatCandidates/interface/Lepton.h"
#include "UserCode/TupleObjects/interface/TupleElectron.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "TLorentzVector.h"
#include "DataFormats/Math/interface/Vector3D.h"
#include "DataFormats/Math/interface/LorentzVector.h"
#include "Math/GenVector/VectorUtil.h"
#include "DataFormats/PatCandidates/interface/PFParticle.h"
#include "UserCode/TupleHelpers/interface/TupleHelpers.hh"
#include "PhysicsTools/PatUtils/interface/TriggerHelper.h"
#include "DataFormats/PatCandidates/interface/TriggerEvent.h"


typedef math::XYZTLorentzVector LorentzVector;
using namespace std;
using namespace edm;
using namespace pat;



//
// class declaration
//

class SinglePatLeptonProducer : public edm::EDProducer {
public:
  explicit SinglePatLeptonProducer(const edm::ParameterSet&);
  ~SinglePatLeptonProducer();

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

  // ----------member data ---------------------------

  edm::InputTag electronSrc_;
  int INDEX_;
  string NAME_;

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
SinglePatLeptonProducer::SinglePatLeptonProducer(const edm::ParameterSet& iConfig):
electronSrc_(iConfig.getParameter<edm::InputTag>("electronSrc" )),
INDEX_(iConfig.getParameter<string>("INDEX" )),
NAME_(iConfig.getParameter<int>("NAME" ))
{


  produces<vector<pat::Electron>>(NAME_).setBranchAlias(NAME_);




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


SinglePatLeptonProducer::~SinglePatLeptonProducer()
{

  // do anything here that needs to be done at desctruction time
  // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called to produce the data  ------------
void
SinglePatLeptonProducer::produce(edm::Event& iEvent, const edm::EventSetup& iSetup)
{



  // get electron collection
  edm::Handle<edm::View<pat::Electron> > electrons;
  iEvent.getByLabel(electronSrc_,electrons);


  std::vector<pat::Electron> * storedElectrons = new std::vector<pat::Electron>();
  const pat::Electron & electronToStore = electrons->at(INDEX_);
  storedElectrons->push_back(electronToStore);

  // add the electrons to the event output
  std::auto_ptr<std::vector<pat::Electron> > eptr(storedElectrons);
  iEvent.put(eptr);


}

// ------------ method called once each job just before starting event loop  ------------
void
SinglePatLeptonProducer::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void
SinglePatLeptonProducer::endJob() {
}

// ------------ method called when starting to processes a run  ------------
void
SinglePatLeptonProducer::beginRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void
SinglePatLeptonProducer::endRun(edm::Run&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void
SinglePatLeptonProducer::beginLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void
SinglePatLeptonProducer::endLuminosityBlock(edm::LuminosityBlock&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
SinglePatLeptonProducer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(SinglePatLeptonProducer);
