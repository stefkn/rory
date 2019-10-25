import azure.cognitiveservices.speech as speechsdk #pylint: disable=import-error
import time
import wikipedia #pylint: disable=import-error
import sys
import re
import pprint 
import flask #pylint: disable=import-error
import flask_socketio #pylint: disable=import-error
import threading
import os
import json

config = json.load(open('config.json'))

# try:
#     conf = open('keys.yaml')
#     print(conf)
# except Exception as e:
#     print(e)
# config.update_from_yaml_file(os.getcwd() + '/keys.yaml')

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = config['FLASK_SECRET_KEY']
app.config['DEBUG'] = True
socketio = flask_socketio.SocketIO(app)

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
        socketio.emit('newevent', json.dumps({'text': 'Rory is now listening.'}), namespace='/siotest')
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
                output = []
                keyword_list = ["United States", "Great Britain", "United Kingdom", "Prime Minister", "President"]
                for line in str(match.group()).split("\n"):
                    for word in keyword_list:
                        if word in line:
                            output.append(line)
                output_json = json.dumps({
                    "text": inputyr,
                    "longtext": output
                })
                socketio.emit('newevent', output_json, namespace='/siotest')

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


class SpeechRecogThread(threading.Thread):
    def __init__(self, speech_recognizer):
        super(SpeechRecogThread, self).__init__()
        recog_event_handler = RecogEventHandler(speech_recognizer)

    def startRecog(self):
        print("START SPEAKING")
        speech_recognizer.start_continuous_recognition()
        time.sleep(30)
        speech_recognizer.stop_continuous_recognition()
        print("END")

    def run(self):
        self.startRecog()


class WebInterface():
    global socketio

    def __init__(self, speech_recognizer):
        @app.route('/')
        def index():
            return flask.render_template('index.html')

        @socketio.on('connect', namespace='/siotest')
        def test_connection():
            print('Client has connected.')
            socketio.emit('newevent', json.dumps({'text': 'Connection Successful, starting up speech service.'}), namespace='/siotest')
            thread = SpeechRecogThread(speech_recognizer)
            thread.start()

        @socketio.on('disconnect', namespace='/siotest')
        def test_disconnection():
            print('Client has disconnected.')
            # Kill rory process here?

        # if __name__ == '__main__':
        socketio.run(app) 


speech_key, service_region = config['AZURE_SPEECH_KEY'], config['AZURE_SERVICE_REGION']
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
web_interface = WebInterface(speech_recognizer)


# class SpeechRecogThread(threading.Thread):
#     def __init__(self, speech_recognizer, web_interface):
#         super(SpeechRecogThread, self).__init__()
#         recog_event_handler = RecogEventHandler(speech_recognizer, web_interface)

#     def startRecog(self):
#         print("START SPEAKING")
#         speech_recognizer.start_continuous_recognition()
#         time.sleep(30)
#         speech_recognizer.stop_continuous_recognition()
#         print("END")

#     def run(self):
#         self.startRecog()


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