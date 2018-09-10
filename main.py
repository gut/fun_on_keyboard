#!/usr/bin/env python3
# SPDX short identifier: GPL-3.0

import argparse
import glob
import random
import sys
import time

import pygame


SOUND_FILENAMES = glob.glob('sounds/*.ogg')

USAGE = """
On keypress: slightly change the color of the screen and play a sound.
When no action is taking place, fade out colors.

All of this done in an animated manner.

Quits on (ALT or CTRL) + (Q or F4)
"""

ARGS = None
LABEL = None
LABEL_POSITION = None


def get_cur_color(surface):
  return tuple(surface.get_at((0, 0)))


def fill_frame(surface, color):
  surface.fill(color)
  surface.blit(LABEL, LABEL_POSITION)
  pygame.display.update()


def main_loop(surface, sounds):
  # Initialize which channel will be used for playing sounds
  cur_channel = 0

  while True:
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
      break
    elif event.type == pygame.KEYDOWN:
      if ARGS.print_key:
        # Curious about what is being pressed?
        print(pygame.key.name(event.key), end=" ")
        sys.stdout.flush()

      # Control quitting
      mods = pygame.key.get_mods()
      quit_key = event.key in (pygame.K_q, pygame.K_F4)
      alt_or_ctrl = mods & (pygame.KMOD_ALT | pygame.KMOD_CTRL)
      if quit_key and alt_or_ctrl:
        print("Quitting...")
        break

      # Main actions!
      # Fill screen with a solid color
      def get_byte():
        """
        Returns a random int from [0,255]
        """
        return int(random.random() * 256)

      target_color = (get_byte(), get_byte(), get_byte())

      def int_easing(current, target):
        """
        Eases @current to @target in a exponential matter
        """
        return current + (target - current) / 10

      next_color = map(int_easing, get_cur_color(surface), target_color)
      fill_color = pygame.Color(*map(int, next_color))
      fill_frame(surface, fill_color)

      # Play a random sound and try to keep playing previous sound as long as
      # possible (use all the channels available)
      sound_index = int(random.random() * len(sounds))
      sound = sounds[sound_index]
      ch = pygame.mixer.Channel(cur_channel)
      cur_channel = (cur_channel + 1) % pygame.mixer.get_num_channels()
      ch.play(sound)

    elif event.type == pygame.NOEVENT:
      # Dim color to black
      def dim_color(tup):
        """
        Returns a darker @tup color until its black
        """
        def keep_within_boundaries_add(a, b):
          """
          Restrict a + b to [0,255]
          """
          result = a + b
          if result < 0:
            return 0
          if result > 255:
            return 255
          return result

        return map(keep_within_boundaries_add, tup, (-1, -1, -1, 0))

      new_color = pygame.Color(*dim_color(get_cur_color(surface)))
      fill_frame(surface, new_color)

      # Wait something like a frame for performance concerns
      time.sleep(1.0 / 60)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description=USAGE,
      formatter_class=argparse.RawTextHelpFormatter)
  parser.add_argument('--window', dest='window', action='store_true',
      default=False, help='run on window mode instead of fullscreen')
  parser.add_argument('--hide-key', dest='print_key', action='store_false',
      default=True, help='print which keys are being pressed')
  ARGS = parser.parse_args()
  mode = pygame.FULLSCREEN if not ARGS.window else 0
  resolution = (0, 0) if not ARGS.window else (800, 600)

  # Pygame initialization
  pygame.init()
  pygame.mixer.init()
  pygame.mouse.set_visible(False)
  font = pygame.font.SysFont(pygame.font.get_default_font(), 24)

  # render text and cache it
  LABEL = font.render("Press Alt+F4 or Ctrl+Q to quit.", 1, (255, 255, 255))

  # Sound caching
  sounds = [pygame.mixer.Sound(i) for i in SOUND_FILENAMES]

  surface = pygame.display.set_mode(resolution, mode)
  info = pygame.display.Info()

  # Centralize text on screen and cache it
  label_rect = LABEL.get_rect()
  LABEL_POSITION = (info.current_w / 2 - label_rect.width / 2,
                    info.current_h / 2 - label_rect.height / 2,)
  main_loop(surface, sounds)

  pygame.quit()
