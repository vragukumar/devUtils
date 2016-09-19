import re
import json

class JsonGenerator:
    def __init__(self, outFile, eventList):
        self.outFile = outFile
        self.eventList = eventList
        self.fltTmplt = {
            "EventID" : 15,
            "EventName": "TemperatureHighWarn",
            "Description" : "Asic temperature low warning",
            "SrcObjName" : "AsicGlobalPM",
            "EventEnable" : True,
            "IsFault" : True,
            "Fault" : {
                    "RaiseFault" : True,
                    "ClearingEventId" : 16,
                    "ClearingDaemonId" : 1,
                    "AlarmSeverity" : "Major"
            }
        }
        self.clrTmplt = {
            "EventID" : 16,
            "EventName": "TemperatureHighWarnClear",
            "Description" : "Asic temperature low warning cleared",
            "SrcObjName" : "AsicGlobalPM",
            "EventEnable" : True,
            "IsFault" : False
        }

    def isFault(self, evtName):
        if evtName.find('Clear') == -1:
            return True 
        else:
            return False 

    def getDesc(self, event):
        s = event[len('EthIf'):]
	s = re.sub('(.)([A-Z][a-z]+)', r'\1 \2', s)
	return "Ethernet interface " + re.sub('([a-z0-9])([A-Z])', r'\1 \2', s)

    def getAlarmSev(self, event):
        if event.find('Alarm') == -1:
            return 'Major'
        else:
            return 'Critical'

    def Generate(self):
        with open(self.outFile, 'w+') as fp:
            eventId = 17
            for event in self.eventList:
                if self.isFault(event):
                    obj = self.fltTmplt
                    obj['EventID'] = eventId
                    obj['EventName'] = event
                    obj['Description'] = self.getDesc(event)
                    obj['Fault']['ClearingEventId'] = eventId + 1
                    obj['Fault']['AlarmSeverity'] = self.getAlarmSev(event) 
                else:
                    obj = self.clrTmplt
                    obj['EventID'] = eventId
                    obj['EventName'] = event
                    obj['Description'] = self.getDesc(event)
                json.dump(obj, fp, sort_keys=1, indent=4)
                fp.write(',\n')
                eventId += 1

if __name__ == '__main__':
    events = [
	'EthIfUnderSizePktsHighAlarm',
	'EthIfUnderSizePktsHighAlarmClear',
	'EthIfUnderSizePktsHighWarn',
	'EthIfUnderSizePktsHighWarnClear',
    ]
    outputFile = './gen_evt.json' 
    gen = JsonGenerator(outputFile, events)
    gen.Generate()
