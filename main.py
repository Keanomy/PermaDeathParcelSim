from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import os
import signal
from time import sleep

import pygame
from pymem import Pymem
from pymem.exception import MemoryReadError, ProcessError, ProcessNotFound
from rich import print
from rich.console import Console

pygame.mixer.init(frequency=48000, buffer=2048)
base_address = 0x072F2088
offset = [0x1B8, 0x268, 0x378]


def main() -> None:
    Console().clear()
    print("Starting ...")
    check_fails()
    if input("Hit 'Enter' to Exit. Y to restart.").lower() == "y":
        main()


def check_fails() -> None:
    try:
        global game_mem, fail_count_address
        game_mem = Pymem("parcel-Win64-Shipping.exe")
        while game_mem:
            fail_count_address = game_mem.resolve_offsets(base_address, offset)
            fails = int(game_mem.read_int(fail_count_address))
            if fails > 0 and game_mem.process_id:
                print(f"[bold red]{fails} Fails detected![/bold red]")
                audio = pygame.mixer.Sound("Failed.mp3").play()
                while audio.get_busy():
                    sleep(0.1)
                sleep(1)
                savepath = os.path.join((os.getenv("LOCALAPPDATA")) or "", "\\parcel\\Saved\\SaveGames\\Save1.sav")
                os.kill(game_mem.process_id, signal.SIGTERM)
                os.remove(savepath)
                print("[bold red]Save file deleted.[/bold red]")
                break
            else:
                print("[bold green]No fails detected.[/bold green]", end="\r")
                sleep(1)
        sleep(1)
    except (ProcessNotFound, ProcessError):
        print("Parcel Simulator not running.")
    except FileNotFoundError:
        print("Save file not found.")
    except MemoryReadError:
        print("Failed to read memory.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting ...")
        pygame.mixer.quit()
