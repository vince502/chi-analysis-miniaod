input_filename = 'file:step3_6.root'
#input_filename = 'file:/afs/cern.ch/work/s/soohwan/private/MCSIM/ChiC_PbPb/CMSSW_13_2_8/src/step3.root'
ouput_filename = 'rootuple.root'

import FWCore.ParameterSet.Config as cms
process = cms.Process("Rootuple")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
# load the Geometry and Magnetic Field
process.load('Configuration.StandardSequences.Reconstruction_cff')
process.load('Configuration.StandardSequences.Services_cff')
process.load('Configuration.Geometry.GeometryDB_cff')
process.load('Configuration.StandardSequences.MagneticField_38T_cff')

# Global Tag:
process.load('Configuration.StandardSequences.FrontierConditions_GlobalTag_cff')
from Configuration.AlCa.GlobalTag import GlobalTag
process.GlobalTag = GlobalTag(process.GlobalTag, '132X_dataRun3_Prompt_v4', '')

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 2000

process.maxEvents = cms.untracked.PSet(input = cms.untracked.int32(-1))
process.source = cms.Source("PoolSource",fileNames = cms.untracked.vstring(input_filename))
process.TFileService = cms.Service("TFileService",fileName = cms.string(ouput_filename))
process.options   = cms.untracked.PSet( wantSummary = cms.untracked.bool(True))

process.load("Ponia.OniaPhoton.slimmedMuonsTriggerMatcher2017_cfi")

# In MiniAOD, the PATMuons are already present. We just need to run Onia2MuMu, with a selection of muons.
process.oniaSelectedMuons = cms.EDFilter('PATMuonSelector',
   src = cms.InputTag('slimmedMuonsWithTrigger'),
   cut = cms.string('muonID(\"AllGlobalMuons\")'
                    ' && abs(innerTrack.dxy) < 0.3'
                    ' && abs(innerTrack.dz)  < 20.'
                    ' && innerTrack.hitPattern.trackerLayersWithMeasurement > 5'
                    ' && innerTrack.hitPattern.pixelLayersWithMeasurement > 0'
                    ' && innerTrack.quality(\"highPurity\")'
                    ' && (abs(eta) <= 2.4 && pt > 1.)'
   ),
   filter = cms.bool(True)
)

process.load("HeavyFlavorAnalysis.Onia2MuMu.onia2MuMuPAT_cfi")
process.onia2MuMuPAT.muons=cms.InputTag('oniaSelectedMuons')
process.onia2MuMuPAT.primaryVertexTag=cms.InputTag('offlineSlimmedPrimaryVertices')
process.onia2MuMuPAT.beamSpotTag=cms.InputTag('offlineBeamSpot')
process.onia2MuMuPAT.higherPuritySelection=cms.string("")
process.onia2MuMuPAT.lowerPuritySelection=cms.string("")
process.onia2MuMuPAT.dimuonSelection=cms.string("2.7 < mass && mass < 3.5")
process.onia2MuMuPAT.addMCTruth = cms.bool(True)

process.triggerSelection = cms.EDFilter("TriggerResultsFilter",
                                        triggerConditions = cms.vstring("HLT_HIL*SingleMu*_v*", "HLT_HIL*DoubleMu*_v*", "HLT_HIMinimumBiasHF1AND*_v*"
                                                                       ),
                                        hltResults = cms.InputTag( "TriggerResults", "", "HLT" ),
                                        l1tResults = cms.InputTag( "" ),
                                        throw = cms.bool(False)
                                        )

process.Onia2MuMuFiltered = cms.EDProducer('DiMuonFilter',
      OniaTag             = cms.InputTag("onia2MuMuPAT"),
      singlemuonSelection = cms.string(""),             
      dimuonSelection     = cms.string("2.7 < mass && mass < 3.5 && pt > 2. && abs(y) < 2.4 && charge==0 && userFloat('vProb') > 0.01"),
      do_trigger_match    = cms.bool(False),
      HLTFilters          = cms.vstring(
                                       ),
)

process.DiMuonCounter = cms.EDFilter('CandViewCountFilter',
    src       = cms.InputTag("Onia2MuMuFiltered"),
    minNumber = cms.uint32(1),
)

process.chiProducer = cms.EDProducer('OniaPhotonProducer',
    conversions     = cms.InputTag("oniaPhotonCandidates","conversions"),
    dimuons         = cms.InputTag("Onia2MuMuFiltered"),
    pi0OnlineSwitch = cms.bool(False),
    deltaMass       = cms.vdouble(0.0,2.0),
    dzmax           = cms.double(0.5),
    triggerMatch    = cms.bool(False)  # trigger match is performed in Onia2MuMuFiltered
)

process.chiFitter1S = cms.EDProducer('OniaPhotonKinematicFit',
                          chi_cand = cms.InputTag("chiProducer"),
                          upsilon_mass = cms.double(3.0969), # GeV   1S = 9.46030   2S = 10.02326    3S = 10.35520  J/psi=3.0969
                          product_name = cms.string("y1S")
                         )

process.chiSequence = cms.Sequence(
                                   process.triggerSelection *
				   process.slimmedMuonsWithTriggerSequence *
				   process.oniaSelectedMuons *
				   process.onia2MuMuPAT *
				   process.Onia2MuMuFiltered *
		                   process.DiMuonCounter *
				   process.chiProducer *
				   process.chiFitter1S
				   )

process.rootuple = cms.EDAnalyzer('chicRootupler',
                          chi_cand = cms.InputTag("chiProducer"),
			  ups_cand = cms.InputTag("Onia2MuMuFiltered"),
                          refit1S  = cms.InputTag("chiFitter1S","y1S"),
                          primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
                          TriggerResults  = cms.InputTag("TriggerResults", "", "HLT"),
                          isMC = cms.bool(True),
                          FilterNames = cms.vstring(
                                                   )
                         )

process.p = cms.Path(process.chiSequence*process.rootuple)
