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
        self.sounds = {}  # Dictionary to store sounds and their volume bars
        self.current_volume_bars = {}  # Track volume bars for each sound

        self.root.title("Soundboard")
        self.create_buttons()

    def create_buttons(self):
        try:
            sound_files = [f for f in os.listdir(self.sound_folder) if f.endswith(('.wav', '.mp3', '.ogg'))]
            for sound_file in sound_files:
                self.add_button_with_volume(sound_file)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load sounds: {e}")

    def add_button_with_volume(self, sound_file):
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        button = tk.Button(frame, text=sound_file, command=lambda sf=sound_file: self.toggle_play_pause(sf))
        button.pack(side=tk.LEFT, padx=5)

        volume_bar = Scale(frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL, label="Volume")
        volume_bar.set(1.0)  # Default volume
        volume_bar.pack(side=tk.RIGHT, padx=5)

        self.buttons.append((button, volume_bar))

    def toggle_play_pause(self, sound_file):
        if sound_file in self.sounds:
            self.stop_sound(sound_file)
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

        self.sounds[sound_file].play(loops=-1)  # Play sound in a loop

        # Start updating the volume dynamically
        self.update_volume(sound_file)

    def update_volume(self, sound_file):
        if sound_file in self.sounds and sound_file in self.current_volume_bars:
            # Continuously update the volume based on the volume bar's value
            self.sounds[sound_file].set_volume(self.current_volume_bars[sound_file].get())
            self.root.after(100, lambda: self.update_volume(sound_file))  # Check again after 100ms

    def stop_sound(self, sound_file):
        if sound_file in self.sounds:
            self.sounds[sound_file].stop()
            del self.sounds[sound_file]
            del self.current_volume_bars[sound_file]

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