import azure.cognitiveservices.speech as speechsdk #pylint: disable=import-error
import time
import wikipedia
import click
import sys
import re
import pprint

class RecogEventHandler:
    _speech_recognizer = None
    _last_output_recognizing = False
    full_page_output_mode = False
    years_found = []

    def __init__(self, speech_recognizer):
        self._speech_recognizer = speech_recognizer
        self._cancel_event_signal = speech_recognizer.canceled
        self._recognized_event_signal = speech_recognizer.recognized
        self._recognizing_event_signal = speech_recognizer.recognizing
        self._session_started_event_signal = speech_recognizer.session_started
        self._session_stopped_event_signal = speech_recognizer.session_stopped
        self._speech_start_event_signal = speech_recognizer.speech_start_detected
        self._speech_stop_event_signal = speech_recognizer.speech_end_detected
        self._cancel_event_signal.connect(self.cancel_event_signal_handler)
        self._recognized_event_signal.connect(self.recognized_event_signal_handler)
        self._recognizing_event_signal.connect(self.recognizing_event_signal_handler)
        self._session_started_event_signal.connect(self.session_started_event_signal_handler)
        self._session_stopped_event_signal.connect(self.session_stopped_event_signal_handler)
        self._speech_start_event_signal.connect(self.speech_start_event_signal_handler)
        self._speech_stop_event_signal.connect(self.speech_stop_event_signal_handler)

    def cancel_event_signal_handler(self, input, evt_args=0):
        print('\n[CANCEL_EVENT] ' + str(input.cancellation_details))
        self._last_output_recognizing = False

    def session_started_event_signal_handler(self, input, evt_args=0):
        print('\n[SESSION_START] ' + str(input.session_id))
        self._last_output_recognizing = False

    def session_stopped_event_signal_handler(self, input, evt_args=0):
        print('\n[SESSION_STOP] ' + str(input.session_id))
        self._last_output_recognizing = False

    # --- Speech Events ---

    def recognized_event_signal_handler(self, input, evt_args=0):
        print('\n[RECOGNIZED] ' + str(input.result.text))
        self._last_output_recognizing = False
        # --- check for commands ---
        if str(input.result.text) == "Rory stop.":
            self._speech_recognizer.stop_continuous_recognition()
            print("Rory has stopped listening.")
        if str(input.result.text) == "Rory full page output true.":
            self.full_page_output_mode = True
            print("Rory will output all page contents.")
        if str(input.result.text) == "Rory full page output false.":
            self.full_page_output_mode = False
            print("Rory will NOT output all page contents.")
        # --- find years ---
        regex = r"[1][0-9]{3}"
        matches = re.finditer(regex, str(input.result.text), re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            print ("[YEAR] {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
            self.years_found.append(match.group())
            self.display_year_info(str(match.group()))

    def recognizing_event_signal_handler(self, input, evt_args=0):
        if self._last_output_recognizing: 
            # sys.stdout.flush()
            # sys.stdout.write('\r[RECOGNIZING] ' + str(input.result.text), sep='', end='', flush=True)
            print('\r[RECOGNIZING] ' + str(input.result.text), sep='', end='', flush=True)
        else: 
            print("[RECOGNIZING] " + str(input.result.text), sep='', end='', flush=True)
            self._last_output_recognizing = True

    def speech_start_event_signal_handler(self, input, evt_args=0):
        print('\n[SPEECH_START] ' + str(input.offset))
        self._last_output_recognizing = False

    def speech_stop_event_signal_handler(self, input, evt_args=0):
        print('\n[SPEECH_STOP] ' + str(input.offset))
        self._last_output_recognizing = False

    # wiki tasks

    def display_year_info(self, inputyr):
        page = wikipedia.page(inputyr).content
        regex = r"(?<==\sEvents\s==\n\n\n)([\w\W\s\S\d\D\n\r\t\0\v\n]*?)(?<=\n\n==\s)"
        matches = re.finditer(regex, page, re.MULTILINE)
        for matchNum, match in enumerate(matches, start=1):
            # print ("Match {matchNum} was found at {start}-{end}: {match}".format(matchNum = matchNum, start = match.start(), end = match.end(), match = match.group()))
            if self.full_page_output_mode:
                print(str(match.group()))
            else:
                self.print_summary(str(match.group()))

    def print_summary(self, page_content):
        for line in page_content.split("\n"):
            if "United States" in line:
                pprint.pprint(line)

    @property
    def cancel_event_signal(self):
        """getter for CancelEvent signaller""" 
        return self._cancel_event_signal

    @property
    def recognized_event_signal(self):
        """getter for RecognizedEvent signaller""" 
        return self._recognized_event_signal

    @property
    def recognizing_event_signal(self):
        """getter for RecognizingEvent signaller""" 
        return self._recognizing_event_signal

    @property
    def session_started_event_signal(self):
        """getter for SessionStartEvent signaller""" 
        return self._session_started_event_signal

    @property
    def session_stopped_event_signal(self):
        """getter for SessionStopEvent signaller""" 
        return self._session_stopped_event_signal

    @property
    def speech_start_event_signal(self):
        """getter for SpeechStartEvent signaller""" 
        return self._speech_start_event_signal

    @property
    def speech_stop_event_signal(self):
        """getter for SpeechStopEvent signaller""" 
        return self._speech_stop_event_signal

# TODO: 
# [] Store keys in an ini file or something 
# [] a function for ranking the importance of a topic via the size of its page + references 
# [] Implement eventlistener for some key to cancel while running with some basic terminal GUI via click
#   [] Basic terminal GUI via Click (display topics)
#   [x] Live updating on recognizing event
# [] Implement some microphone processing to isolate speaking voices 
# [] Implement NLP to extract dates and basic propositional sentences for lookup 
# [] Implement a wikipedia scraper which hooks into NLP results 
# [] Implement basic readout of scraped information 


speech_key, service_region = "", ""
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
recog_event_handler = RecogEventHandler(speech_recognizer)

print("START SPEAKING")
speech_recognizer.start_continuous_recognition()
time.sleep(30)
speech_recognizer.stop_continuous_recognition()
print("END")




# if process == 'not finished':
#     print("done...")
#     speech_recognizer.stop_continuous_recognition_async()
#     # Checks result.
#     if result.reason == speechsdk.ResultReason.RecognizedSpeech:
#         print("Recognized: {}".format(result.text))
#     elif result.reason == speechsdk.ResultReason.NoMatch:
#         print("No speech could be recognized: {}".format(result.no_match_details))
#     elif result.reason == speechsdk.ResultReason.Canceled:
#         cancellation_details = result.cancellation_details
#         print("Speech Recognition canceled: {}".format(cancellation_details.reason))
#         if cancellation_details.reason == speechsdk.CancellationReason.Error:
#             print("Error details: {}".format(cancellation_details.error_details))
# else:
#     print("HELLO")
#     print(process)
#     print(result)