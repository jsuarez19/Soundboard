import os
import tkinter as tk
from tkinter import messagebox
import pygame
from tkinter import Scale

# Initialize pygame mixer
pygame.mixer.init()

class SoundboardApp:
    def __init__(self, root, sound_folder):
        self.root = root
        self.sound_folder = sound_folder
        self.buttons = []
        self.sounds = {}  # Dictionary to store sounds
        self.channels = {}  # Dictionary to store channels for each sound
        self.current_volume_bars = {}  # Track volume bars for each sound
        self.paused_sounds = set()  # Track which sounds are paused

        self.root.title("Soundboard")
        self.create_buttons()

    def create_buttons(self):
        try:
            sound_files = [f for f in os.listdir(self.sound_folder) if f.endswith(('.wav', '.mp3', '.ogg'))]

            # Create a frame for non-"sfx" sounds
            non_sfx_frame = tk.LabelFrame(self.root, text="Regular Sounds", padx=10, pady=10)
            non_sfx_frame.pack(pady=10, fill="x")

            # Create a frame for "sfx" sounds
            sfx_frame = tk.LabelFrame(self.root, text="SFX Sounds", padx=10, pady=10)
            sfx_frame.pack(pady=10, fill="x")

            for sound_file in sound_files:
                if sound_file.lower().startswith("sfx"):
                    self.add_button_with_volume(sound_file, sfx_frame)
                else:
                    self.add_button_with_volume(sound_file, non_sfx_frame)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sounds: {e}")

    def add_button_with_volume(self, sound_file, parent_frame):
        frame = tk.Frame(parent_frame)
        frame.pack(pady=5)

        button = tk.Button(frame, text=sound_file, command=lambda sf=sound_file: self.toggle_play_pause(sf))
        button.pack(side=tk.LEFT, padx=5)

        volume_bar = Scale(frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Volume")
        volume_bar.set(1.0)  # Default volume
        volume_bar.pack(side=tk.RIGHT, padx=5)

        self.buttons.append((button, volume_bar))

    def toggle_play_pause(self, sound_file):
        if sound_file in self.channels:
            channel = self.channels[sound_file]
            if sound_file in self.paused_sounds:  # Sound is paused
                channel.unpause()
                self.paused_sounds.remove(sound_file)
            else:  # Sound is playing
                channel.pause()
                self.paused_sounds.add(sound_file)
        else:
            self.play_sound(sound_file)

    def play_sound(self, sound_file):
        sound_path = os.path.join(self.sound_folder, sound_file)
        if sound_file not in self.sounds:
            sound = pygame.mixer.Sound(sound_path)
            self.sounds[sound_file] = sound

        # Set initial volume from the corresponding volume bar
        for button, volume_bar in self.buttons:
            if button.cget("text") == sound_file:
                self.sounds[sound_file].set_volume(volume_bar.get())
                self.current_volume_bars[sound_file] = volume_bar  # Track the volume bar for this sound

        # Play the sound on a dedicated channel
        if sound_file not in self.channels:
            channel = pygame.mixer.find_channel()
            if channel:
                self.channels[sound_file] = channel
        else:
            channel = self.channels[sound_file]

        if channel:
            if not sound_file.lower().startswith("sfx"):
                channel.play(self.sounds[sound_file], loops=-1)  # Loop indefinitely
            else:
                channel.play(self.sounds[sound_file], loops=0)  # Play once

            # Start updating the volume dynamically
            self.update_volume(sound_file)

    def update_volume(self, sound_file):
        if sound_file in self.sounds and sound_file in self.current_volume_bars and sound_file in self.channels:
            # Continuously update the volume based on the volume bar's value
            volume = self.current_volume_bars[sound_file].get()
            channel = self.channels[sound_file]
            channel.set_volume(volume)  # Update the channel's volume
            self.root.after(100, lambda: self.update_volume(sound_file))  # Check again after 100ms

    def stop_sound(self, sound_file):
        if sound_file in self.channels:
            self.channels[sound_file].stop()
            del self.channels[sound_file]
        if sound_file in self.sounds:
            del self.sounds[sound_file]
        if sound_file in self.current_volume_bars:
            del self.current_volume_bars[sound_file]
        if sound_file in self.paused_sounds:
            self.paused_sounds.remove(sound_file)

    def stop_all_sounds(self):
        for sound_file in list(self.sounds.keys()):
            self.stop_sound(sound_file)

    def on_close(self):
        self.stop_all_sounds()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    sound_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SFX")  # Use SFX directory for sound files
    root = tk.Tk()
    app = SoundboardApp(root, sound_folder)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()