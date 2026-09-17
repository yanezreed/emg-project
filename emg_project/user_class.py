from presidio_anonymizer import AnonymizerEngine
from presidio_analyzer import AnalyzerEngine

from datastore import update_login_time
from datetime import datetime

class USER_CLASS:
    def __init__(self, username):
        self.username = username
        self.workflow = None
        self.active_session = False
        self.conversations = []
        self.selected_customer = None

    def initialize_session(self, selected_workflow):
        self.workflow = selected_workflow
        self.active_session = True

        last_login = datetime.now().isoformat()
        # format ie. 2026-06-13T20:34:27.654123

        update_login_time(last_login, self.username)

    def sanitise_text(self, text):
        if text == "":
            return text

        analyzer = AnalyzerEngine()
        anonymizer = AnonymizerEngine()

        analyzed_text = analyzer.analyze(text = text, language = "en")

        anonymized_result = anonymizer.anonymize(text = text, analyzer_results = analyzed_text)
        # for natural language processing to work here, spacy installation is required...

        return anonymized_result.text

    def spell_check(self, text):
        if text == "":
            return text
        # Need to implement this