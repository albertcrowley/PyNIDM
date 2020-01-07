from nidm.experiment import Query
from nidm.core import Constants
import json
import re
from urllib import parse
import pprint
import os
from tempfile import gettempdir

class RestParser:

    def projects(self):
        result = []
        self.restLog("Returning all projects", 2, self.verbosity_level)
        projects = Query.GetProjectsUUID(self.nidm_files)
        for uuid in projects:
            result.append(str(uuid).replace(Constants.NIIRI, ""))
        return result

    def projectSummary(self):
        result = []
        self.restLog("Returing metadata ", 2, self.verbosity_level)
        match = re.match(r"^/?projects/([^/]+)$", self.command)
        id = parse.unquote(str(match.group(1)))
        self.restLog("computing metadata", 5, self.verbosity_level)
        projects = Query.GetProjectsComputedMetadata(self.nidm_files)
        for pid in projects['projects'].keys():
            self.restLog("comparng " + str(pid) + " with " + str(id), 5, self.verbosity_level)
            self.restLog("comparng " + str(pid) + " with " + Constants.NIIRI + id, 5, self.verbosity_level)
            self.restLog("comparng " + str(pid) + " with niiri:" + id, 5, self.verbosity_level)
            if pid == id or pid == Constants.NIIRI + id or pid == "niiri:" + id:
                result = projects['projects'][pid]
        return result

    def subjectsList(self):
        match = re.match(r"^/?projects/([^/]+)/subjects/?$", self.command)
        project = match.group((1))
        self.restLog("Returning all agents matching filter '{}' for project {}".format(self.filter, project), 2,
                     self.verbosity_level)
        return Query.GetParticipantUUIDsForProject(self.nidm_files, project, self.filter, None)

    def subjectSummary(self):
        match = re.match(r"^/?projects/([^/]+)/subjects/([^/]+)/?$", self.command)
        self.restLog("Returning info about subject {}".format(match.group(2)), 2, self.verbosity_level)
        return Query.GetParticipantDetails(self.nidm_files, match.group(1), match.group(2))

    def instrumentsList(self):
        result = []
        match = re.match(r"^/?projects/([^/]+)/subjects/([^/]+)", self.command)
        self.restLog("Returning instruments in subject {}".format(match.group(2)), 2, self.verbosity_level)
        instruments = Query.GetParticipantInstrumentData(self.nidm_files, match.group(1), match.group(2))
        for i in instruments:
            result.append(i)
        return result

    def instrumentSummary(self):
        match = re.match(r"^/?projects/([^/]+)/subjects/([^/]+)/instruments/([^/]+)", self.command)
        self.restLog("Returning instrument {} in subject {}".format(match.group(3), match.group(2)), 2, self.verbosity_level)
        instruments = Query.GetParticipantInstrumentData(self.nidm_files, match.group(1), match.group(2))
        return instruments[match.group(3)]

    def derivativesList(self):
        result = []
        match = re.match(r"^/?projects/([^/]+)/subjects/([^/]+)", self.command)
        self.restLog("Returning derivatives in subject {}".format(match.group(2)), 2, self.verbosity_level)
        derivatives = Query.GetDerivativesDataForSubject(self.nidm_files, match.group(1), match.group(2))
        for s in derivatives:
            result.append(s)
        return result

    def derivativeSummary(self):
        match = re.match(r"^/?projects/([^/]+)/subjects/([^/]+)/derivatives/([^/]+)", self.command)
        self.restLog("Returning stat {} in subject {}".format(match.group(3), match.group(2)), 2, self.verbosity_level)
        derivatives = Query.GetDerivativesDataForSubject(self.nidm_files, match.group(1), match.group(2))
        return derivatives[match.group(3)]

    def run (self, nidm_files, command, verbosity_level = 0):
        self.nidm_files = nidm_files
        self.command = command
        self.verbosity_level = verbosity_level

        self.restLog("parsing command "+ command, 1, verbosity_level)
        self.restLog("Files to read:" + str(nidm_files), 1, verbosity_level)
        self.restLog("Using {} as the graph cache directory".format( gettempdir() ), 1, verbosity_level)

        self.filter = ""
        if str(command).find('?') != -1:
            (command, query) = str(command).split('?')
            for q in query.split('&'):
                if len(q.split('=')) == 2:
                    left, right = q.split('=')[0], q.split('=')[1]
                    if left == 'filter':
                        self.filter = right

        if re.match(r"^/?projects/?$", command): return self.projects()

        if re.match(r"^/?projects/[^/]+$", command): return self.projectSummary()

        if re.match(r"^/?projects/[^/]+/subjects/?$", command): return self.subjectsList()

        if re.match(r"^/?projects/[^/]+/subjects/[^/]+/?$", command): return self.subjectSummary()

        if re.match(r"^/?projects/[^/]+/subjects/[^/]+/instruments/?$", command): return self.instrumentsList()

        if re.match(r"^/?projects/[^/]+/subjects/[^/]+/instruments/[^/]+/?$", command): return self.instrumentSummary()

        if re.match(r"^/?projects/[^/]+/subjects/[^/]+/derivatives/?$", command): return self.derivativesList()

        if re.match(r"^/?projects/[^/]+/subjects/[^/]+/derivatives/[^/]+/?$", command): return self.derivativeSummary()

        self.restLog("NO MATCH!",2, verbosity_level)

        return []


    def restLog (self, message, verbosity_of_message, verbosity_level):
        if verbosity_of_message <= verbosity_level:
            print (message)
    
    def formatResults (self, result, format, stream):
        pp = pprint.PrettyPrinter(stream=stream)
        if format == 'text':
            if isinstance(result, list):
                print(*result, sep='\n', file=stream)
            else:
                pp.pprint(result)
        else:
            print(json.dumps(result, indent=2, separators=(',', ';')), file=stream)
