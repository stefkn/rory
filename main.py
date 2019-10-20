import azure.cognitiveservices.speech as speechsdk #pylint: disable=import-error
import time

class RecogEventHandler:
    def __init__(self, speech_recognizer):
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
        print("[CANCEL_EVENT] " + str(input.cancellation_details))
    
    def recognized_event_signal_handler(self, input, evt_args=0):
        print("[RECOGNIZED] UTTERANCE: " + str(input.result.text))

    def recognizing_event_signal_handler(self, input, evt_args=0):
        print("[RECOGNIZING] " + str(input.result.text))

    def session_started_event_signal_handler(self, input, evt_args=0):
        print("[SESSION_START] " + str(input.session_id))

    def session_stopped_event_signal_handler(self, input, evt_args=0):
        print("[SESSION_STOP] " + str(input.session_id))

    def speech_start_event_signal_handler(self, input, evt_args=0):
        print("[SPEECH_START] " + str(input.offset))

    def speech_stop_event_signal_handler(self, input, evt_args=0):
        print("[SPEECH_STOP] " + str(input.offset))

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
# [] Implement smart recycling of the speech recognizer in between sentences after certain length of time elapsed ?
# [] Implement eventlistener for some key to cancel while running with some basic terminal GUI 
# [] Implement some microphone processing to isolate speaking voices 
# [] Implement NLP to extract dates and basic propositional sentences for lookup 
# [] Implement a wikipedia scraper which hooks into NLP results 
# [] Implement basic readout of scraped information 


speech_key, service_region = "", ""
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)
recog_event_handler = RecogEventHandler(speech_recognizer)

print("START SPEAKING 20s")
test = speech_recognizer.start_continuous_recognition()
time.sleep(20)
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