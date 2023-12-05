from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

myname='rootuple-POnia'
mydata='/Charmonium/Run2017B-PromptReco-v1/MINIAOD'
myjson='Cert_Collisions2023HI_374288_375823_Muon.json'

config.General.requestName = myname
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'run-chic-miniaod.py'
config.JobType.outputFiles = ['rootuple.root']

config.Data.inputDataset = mydata
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 5
config.Data.lumiMask = myjson

config.Data.outLFNDirBase = '/store/user/%s/' % (getUsernameFromSiteDB())
config.Data.publication = False
config.Data.publishDBS  = 'https://cmsweb.cern.ch/dbs/prod/phys03/DBSWriter/'
config.Data.inputDBS = 'https://cmsweb.cern.ch/dbs/prod/global/DBSReader/'
config.Data.outputDatasetTag  = myname
config.Data.outLFNDirBase = '/store/user/soohwan/Analysis/PbpMinimumBias/%s' % (config.General.requestName)
config.Site.storageSite = 'T3_KR_KNU'
