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
        self.looping_sound = None
        self.currently_playing = None
        self.paused = False
        self.current_volume_bar = None

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
        volume_bar.set(0.5)  # Default volume
        volume_bar.pack(side=tk.RIGHT, padx=5)

        self.buttons.append((button, volume_bar))

    def toggle_play_pause(self, sound_file):
        if self.currently_playing == sound_file and not self.paused:
            self.pause_sound()
        elif self.currently_playing == sound_file and self.paused:
            self.resume_sound()
        else:
            self.play_sound(sound_file)

    def play_sound(self, sound_file):
        self.stop_looping_sound()
        sound_path = os.path.join(self.sound_folder, sound_file)
        sound = pygame.mixer.Sound(sound_path)
        self.currently_playing = sound_file
        self.paused = False

        # Set initial volume from the corresponding volume bar
        for button, volume_bar in self.buttons:
            if button.cget("text") == sound_file:
                sound.set_volume(volume_bar.get())
                self.current_volume_bar = volume_bar  # Track the volume bar for the current sound

        sound.play()
        self.looping_sound = sound

        # Start updating the volume dynamically
        self.update_volume()

    def update_volume(self):
        if self.looping_sound and self.current_volume_bar:
            # Continuously update the volume based on the volume bar's value
            self.looping_sound.set_volume(self.current_volume_bar.get())
            self.root.after(100, self.update_volume)  # Check again after 100ms

    def pause_sound(self):
        if self.looping_sound:
            pygame.mixer.pause()
            self.paused = True

    def resume_sound(self):
        if self.looping_sound:
            pygame.mixer.unpause()
            self.paused = False

    def stop_looping_sound(self):
        if self.looping_sound:
            self.looping_sound.stop()
            self.looping_sound = None
            self.currently_playing = None
            self.paused = False

    def on_close(self):
        self.stop_looping_sound()
        pygame.mixer.quit()
        self.root.destroy()

if __name__ == "__main__":
    sound_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "SFX")  # Use SFX directory for sound files
    root = tk.Tk()
    app = SoundboardApp(root, sound_folder)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()