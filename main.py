import os
import io
import glob
import time
import random
import re
import tkinter as tk
from tkinter import messagebox
import pygame
from PIL import Image, ImageTk
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

CORRECT_EMOJI = "😀"
INCORRECT_EMOJI = "😭"
BIRD_EMOJI = "🐦‍⬛"

def bird_name_from_filename(mp3_filename):
    bird_name = (re.search(r'/([^/0-9]+)\s*\d', mp3_filename))
    return bird_name.group(1).strip()

class BirdList():

    def __init__(self):
        self.original_bird_list = sorted(glob.glob(os.path.join("sounds", '*.mp3')))
        self.bird_list = self.original_bird_list.copy()
        self.current_bird = None


    def print_bird_list(self):
        print(f"Soundfiles:\n  {"\n  ".join(self.bird_list)}\n{len(self.bird_list)} birds in total.")


    def reset_bird_list(self):
        self.bird_list = self.original_bird_list.copy()


    def select_random_bird(self):
        self.current_bird = random.choice(self.bird_list)


    def remove_bird(self, bird):
        self.bird_list.remove(bird)


class QuizScreen(tk.Tk):

    def __init__(self, bird_list):
        super().__init__()
        pygame.init()
        self.n_items = 0
        self.n_correct = 0
        self.evaluation = False
        self.current_bird = ""
        self.title("Birdsong Quiz")
        self.focus_force()
        # images
        self.image_width = 0
        self.image_height = 0
        self.image_shown = True
        self.bird_list = bird_list
        blank_img = Image.new('RGBA', (600, 600), (0, 0, 0, 0))  # Transparent image
        self.blank_tk_img = ImageTk.PhotoImage(blank_img)
        self.tk_img = ImageTk.PhotoImage(blank_img)
        percentage_score_img = Image.new('RGBA', (100, 10), (112, 198, 135))
        self.percentage_score_tk_img = ImageTk.PhotoImage(percentage_score_img)
        self.percentage_score_image = tk.Label(self)
        self.percentage_score_image.configure(image = self.percentage_score_tk_img)
        self.percentage_score_image.grid(row = 7, column = 0, columnspan = 3, sticky = "w")
        # labels
        self.label_0 = tk.Label(text = "0%")
        self.label_0.grid(row = 6, column = 0, sticky = "w")
        self.label_100 = tk.Label(text = "100%")
        self.label_100.grid(row = 6, column = 2, sticky = "e")
        self.label_image = tk.Label(self)
        self.label_image.configure(image = self.blank_tk_img)
        self.label_image.grid(row=1, column=0, columnspan=3)
        self.label_common_name = tk.Label(text ="", font = ("Helvetica", 22, "bold"))
        self.label_common_name.grid(row = 2, column = 0, columnspan = 3, pady = (10, 0))
        self.label_latin_name = tk.Label(text = "", font = ("Helvetica", 15, "normal"))
        self.label_latin_name.grid(row = 3, column = 0, columnspan = 3, pady = (0, 12))
        self.label_credits = tk.Label(font = ("Helvetica", 10, "normal"), text = "\n")
        self.label_credits.grid(row = 4, column = 0, columnspan = 3, pady = (0, 5))
        self.label_birds_remaining = tk.Label(font = ("Helvetica", 12, "normal"))
        self.label_birds_remaining.grid(row = 8, column = 1, pady = 10)
       # buttons
        self.next_button = tk.Button(text = "Skip", command = self.next_bird)
        self.next_button.grid(row = 5, column = 2)
        self.reveal_button = tk.Button(text = "Reveal image", width = 8, command = self.show_image)
        self.reveal_button.grid(row = 5, column = 1)
        self.repeat_button = tk.Button(text = "Repeat", command = self.play_birdsong)
        self.repeat_button.grid(row = 5, column = 0, pady = 10)
        self.correct_button = tk.Button(text = CORRECT_EMOJI, command = self.correct)
        self.incorrect_button = tk.Button(text = INCORRECT_EMOJI, command = self.incorrect)


    def load_image(self):
        audio = ID3(self.current_bird)
        picture = None
        for tag in audio.getall("APIC"):
            picture = tag
            break
        if picture:
            image_data = io.BytesIO(picture.data)
            img = Image.open(image_data)
            self.tk_img = ImageTk.PhotoImage(img)
        else:
            tk.messagebox.showinfo(message = "No image available for this recording")
        audiofile = MP3(self.current_bird)
        metadata = audiofile.tags.get("COMM::ENG")[0]
        metadata_list = [item.strip() for item in metadata.split(";")]
        self.latin_name = metadata_list[0]
        self.recording_place = metadata_list[1]
        self.recording_artist = metadata_list[2]
        self.recording_id = metadata_list[3]


    def show_image(self):
        self.label_image.configure(image = self.tk_img)
        self.label_image.grid(row = 1, column = 0, columnspan = 3)
        self.label_image.update()
        self.reveal_button.configure(text = "Reveal Info", command = self.show_info)
        self.show_response_buttons()

    def show_info(self):
        self.label_common_name.configure(text = bird_name_from_filename(self.current_bird))
        self.label_latin_name.configure(text = self.latin_name)
        self.label_credits.config(text = f"Recorded in {self.recording_place} by {self.recording_artist}\nMacaulay Library, {self.recording_id}")
        self.reveal_button.configure(text = "(evaluate)", fg = "gray", command = None)


    def hide_image(self):
        self.label_image.configure(image = self.blank_tk_img)
        self.label_common_name.configure(text = "")
        self.label_latin_name.configure(text = "")
        self.label_credits.configure(text = "\n")
        self.hide_response_buttons()


    def play_birdsong(self):
        pygame.mixer.stop()
        pygame.mixer.init()
        music = pygame.mixer.Sound(self.current_bird)
        music.play()


    def correct(self):
        self.n_items += 1
        self.n_correct += 1
        self.evaluation = True
        self.bird_list.bird_list.remove(self.current_bird)
        self.next_bird()


    def incorrect(self):
        self.n_items += 1
        self.evaluation = False
        self.next_bird()


    def update_percentage_score(self):
        self.percentage_score_image.grid_remove()
        if self.n_items > 0:
            length = int((self.n_correct / self.n_items) * 600)
        else:
            length = 1
        percentage_score_img = Image.new('RGBA', (length, 10), (112, 198, 135))
        self.percentage_score_tk_img = ImageTk.PhotoImage(percentage_score_img)
        self.percentage_score_image = tk.Label(self)
        self.percentage_score_image.configure(image=self.percentage_score_tk_img)
        self.percentage_score_image.grid(row=7, column=0, columnspan=3, sticky = "w")
        self.label_birds_remaining.configure(text = f"{BIRD_EMOJI} {len(self.bird_list.bird_list)}")


    def show_response_buttons(self):
        self.correct_button.grid(row = 5, column = 1, sticky = "e")
        self.incorrect_button.grid(row = 5, column = 1, sticky = "w")


    def hide_response_buttons(self):
        self.correct_button.grid_remove()
        self.incorrect_button.grid_remove()


    def next_bird(self):
        self.update_percentage_score()
        self.reveal_button.configure(text = "Reveal image", fg = "black", command = self.show_image)
        if len(self.bird_list.bird_list) > 0:
            self.bird_list.select_random_bird()
            self.current_bird = self.bird_list.current_bird
            self.hide_image()
            self.load_image()
            self.play_birdsong()
        else:
            reset_score = tk.messagebox.askyesno(message = f"No birds left!\nRepopulating list.\n{round(100 * (self.n_correct / self.n_items))}% correct\nReset score?")
            if reset_score:
                self.n_items = 0
                self.n_correct = 0
            print(reset_score)
            self.bird_list.reset_bird_list()
            self.next_bird()


if __name__ == "__main__":
    birdList = BirdList()
    birdList.print_bird_list()
    birdList.select_random_bird()

    quizScreen = QuizScreen(birdList)
    quizScreen.next_bird()

    quizScreen.mainloop()
