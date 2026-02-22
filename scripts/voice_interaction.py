#!/usr/bin/env python3
import os
import sys
import subprocess

# Optional import for speech recognition
try:
    import speech_recognition as sr
    HAS_RECOGNITION = True
except ImportError:
    HAS_RECOGNITION = False

def speak(text):
    """Uses macOS 'say' command to speak text."""
    print(f"Lyra is speaking: {text}", file=sys.stderr)
    subprocess.run(["say", text])

def listen(timeout=5):
    """Listens for speech and returns text. Stops after 5 seconds of silence or 5 minutes of speech."""
    if not HAS_RECOGNITION:
        print("Error: 'speech_recognition' module not installed. Cannot listen.", file=sys.stderr)
        return None
    
    r = sr.Recognizer()
    # Adjust sensitivity
    r.energy_threshold = 300 # Much more sensitive to catch trailing speech
    r.dynamic_energy_threshold = False 
    r.pause_threshold = 5.0 
    r.non_speaking_duration = 1.0 # Buffer before speech starts
    with sr.Microphone() as source:
        print("Listening started (max 5 minutes, stops after 5s silence)...", file=sys.stderr)
        # Very brief adjustment
        r.adjust_for_ambient_noise(source, duration=0.2)
        if r.energy_threshold < 300:
            r.energy_threshold = 300
        print(f"Energy threshold locked to: {r.energy_threshold}", file=sys.stderr)
        try:
            # timeout: max seconds to wait for speech to START
            # phrase_time_limit: max seconds for the entire recording
            audio = r.listen(source, timeout=300, phrase_time_limit=300)
            
            print("Listening stopped. Processing audio immediately...", file=sys.stderr)
            text = r.recognize_google(audio)
            print(f"Speech recognized: {text}", file=sys.stderr)
            return text
        except sr.WaitTimeoutError:
            print("Stop: No speech started within 5 minutes.", file=sys.stderr)
            return None
        except sr.UnknownValueError:
            print("Stop: Audio captured but could not be understood.", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error during listening: {e}", file=sys.stderr)
            return None
        except sr.UnknownValueError:
            print("Could not understand audio.", file=sys.stderr)
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}", file=sys.stderr)
            return None

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: ./voice_interaction.py [listen|speak] [text]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "listen":
        result = listen()
        if result:
            # Print to stderr for immediate visual confirmation in the terminal
            print(f"\n[LYRA VOICE SYSTEM] Heard: \"{result}\"\n", file=sys.stderr)
            # Print to stdout to be used as the prompt, with a special prefix
            print(f"[VOICE_INPUT] I heard: {result}")
        else:
            sys.exit(1)
    elif command == "speak":
        if len(sys.argv) < 3:
            print("Error: No text provided for speak command.")
        else:
            speak(" ".join(sys.argv[2:]))
    else:
        print(f"Unknown command: {command}")
