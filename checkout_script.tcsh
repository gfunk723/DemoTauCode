#!/bin/tcsh


echo "checking out improved Tau ID : "
################################################
git cms-merge-topic -u cms-tau-pog:CMSSW_5_3_X_boostedTaus_2013Dec17
#git cms-merge-topic -u cms-tau-pog:CMSSW_5_3_X_tauID2014
################################################

echo "soft link to UserCode "
################################################
ln -s ../../UserCode UserCode
################################################


echo "checking out SVFit code : "

################################################
wget --no-check-certificate https://github.com/cms-analysis/TauAnalysis-CandidateTools/archive/TauAnalysis-CandidateTools-V00-02-03s.tar.gz .
tar -xzvf TauAnalysis-CandidateTools-V00-02-03s
mkdir TauAnalysis
rm -rf TauAnalysis/CandidateTools
mv TauAnalysis-CandidateTools-TauAnalysis-CandidateTools-V00-02-03s TauAnalysis/CandidateTools
rm -rf TauAnalysis-CandidateTools-V00-02-03s
################################################


echo "copying MVA PF MET code from Phil Harris : "
################################################
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/RecoMET .
################################################


echo "checking out MET Recoil Correction Code : "

################################################
wget http://web.mit.edu/~pcharris/www/RecoilCorrector_v7.tgz RecoilCorrector_v7.tgz
tar -xzvf RecoilCorrector_v7.tgz
rm -rf UserCode/RecoilCorrector/recoilfits
mv RecoilCorrector_v7/recoilfits UserCode/RecoilCorrector/recoilfits
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/LLR_recoilfits/*RR*.root UserCode/RecoilCorrector/recoilfits/.
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/53_Dec2012/*root ./RecoMET/METPUSubtraction/data/.
rm -rf RecoilCorrector_v7
rm -rf RecoilCorrector_v7.tgz
################################################

echo "checking out Electron MVA Code : "
################################################
git cms-addpkg EgammaAnalysis/ElectronTools
cd EgammaAnalysis/ElectronTools/data/
cat download.url | xargs wget
cd -
################################################



echo "soft link MVA MET leptons PAT config :"
################################################
cd RecoMET/METPUSubtraction/python/
ln -s ../../../UserCode/mvaPFMET_leptons_PAT_cfi.py mvaPFMET_leptons_PAT_cfi.py
cd -
################################################

echo " copy pile up jet ID configs "
################################################
rm -rf RecoJets
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/RecoJets .
rm -rf DataFormats/JetReco
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/JetReco_v2 DataFormats/JetReco
rm -rf DataFormats/METReco
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/METReco_v2 DataFormats/METReco
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/SelectorUtils PhysicsTools/.
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/PhysicsTools_Utilities PhysicsTools/Utilities
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/TauSpinnerInterface TauSpinnerInterface
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/mvaPFMEt_53_Dec2012.db RecoMET/METPUSubtraction/data/.
cp -r /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/HiggsPtReweightFiles UserCode/.
################################################

echo "getting pile-up correction root files "
####################################################

mkdir UserCode/PileUpReWeightFiles
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/MC_Summer12_PU_S10-600bins.root UserCode/PileUpReWeightFiles/.
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/Data_Pileup_2012_ReRecoPixel-600bins.root UserCode/PileUpReWeightFiles/.
####################################################

echo "setting up JEC and uncertainty "
################################################
git cms-addpkg JetMETCorrections/Modules
cp JetMETCorrections/Modules/test/JetCorrectionDBReader_cfg.py RecoJets/JetAnalyzers/test/.
sed -i 's/string(\x27AK5PF\x27)/string(\x27AK5PFchs\x27)/g' RecoJets/JetAnalyzers/test/JetCorrectionDBReader_cfg.py
cd RecoJets/JetAnalyzers/test/

echo "running JEC DB file pull for MC under START53_V23 : "
sed -i 's/GR_R_42_V19/START53_V23/g' JetCorrectionDBReader_cfg.py
cmsRun JetCorrectionDBReader_cfg.py

echo "running JEC DB file pull for DATA under START53_V23 : "
sed -i 's/START53_V23/FT_53_V21_AN4/g' JetCorrectionDBReader_cfg.py
cmsRun JetCorrectionDBReader_cfg.py
cd -
################################################

mkdir RunTimeDataInput
mkdir RunTimeDataInput/data
cp UserCode/TupleMuonProducer/BuildFile.xml RunTimeDataInput/.
cp -r UserCode/HiggsPtReweightFiles RunTimeDataInput/data/.
cp -r UserCode/PileUpReWeightFiles RunTimeDataInput/data/.
cp -r UserCode/RecoilCorrector/recoilfits RunTimeDataInput/data/.
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/CustomVersions/PFMETProducerMVA.h ./RecoMET/METPUSubtraction/plugins/PFMETProducerMVA.h
cp /afs/cern.ch/user/s/sshalhou/public/INSTALL_PUBLIC_FILES/CustomVersions/PFMETProducerMVA.cc ./RecoMET/METPUSubtraction/plugins/PFMETProducerMVA.cc


