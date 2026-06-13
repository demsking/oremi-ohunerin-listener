# Copyright 2026 Sébastien Demanou. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Support for Oremi Ohunerin Listener sensors."""
from __future__ import annotations

import json
import logging
from typing import Any

from homeassistant.components import mqtt
from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import callback
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import OhunerinListenerConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# List of all known sounds that can be detected
SOUND_OPTIONS = [
  "a-capella",
  "accelerating-revving-vroom",
  "accordion",
  "acoustic-guitar",
  "afrobeat",
  "air-brake",
  "air-conditioning",
  "air-horn-truck-horn",
  "aircraft",
  "aircraft-engine",
  "alarm",
  "alarm-clock",
  "ambient-music",
  "ambulance-siren",
  "angry-music",
  "animal",
  "applause",
  "arrow",
  "artillery-fire",
  "babbling",
  "baby-cry-infant-cry",
  "baby-laughter",
  "background-music",
  "bagpipes",
  "bang",
  "banjo",
  "bark",
  "basketball-bounce",
  "bass-drum",
  "bass-guitar",
  "bathtub-filling-or-washing",
  "beatboxing",
  "bee-wasp-etc",
  "beep-bleep",
  "bell",
  "bellow",
  "belly-laugh",
  "bicycle",
  "bicycle-bell",
  "bird",
  "bird-flight-flapping-wings",
  "bird-vocalization-bird-call-bird-song",
  "biting",
  "bleat",
  "blender",
  "bluegrass",
  "blues",
  "boat-water-vehicle",
  "boiling",
  "boing",
  "boom",
  "bouncing",
  "bow-wow",
  "bowed-string-instrument",
  "brass-instrument",
  "breaking",
  "breathing",
  "burping-eructation",
  "burst-pop",
  "bus",
  "busy-signal",
  "buzz",
  "buzzer",
  "cacophony",
  "camera",
  "canidae-dogs-wolves",
  "cap-gun",
  "car",
  "car-alarm",
  "car-passing-by",
  "carnatic-music",
  "cash-register",
  "cat",
  "caterwaul",
  "cattle-bovinae",
  "caw",
  "cello",
  "chainsaw",
  "change-ringing-campanology",
  "chant",
  "chatter",
  "cheering",
  "chewing-mastication",
  "chicken-rooster",
  "child-singing",
  "child-speech-kid-speaking",
  "children-playing",
  "children-shouting",
  "chime",
  "chink-clink",
  "chirp-tone",
  "chirp-tweet",
  "choir",
  "chop",
  "chopping-food",
  "chorus-effect",
  "christian-music",
  "christmas-music",
  "chuckle-chortle",
  "church-bell",
  "civil-defense-siren",
  "clang",
  "clapping",
  "clarinet",
  "classical-music",
  "clatter",
  "clickety-clack",
  "clicking",
  "clip-clop",
  "clock",
  "cluck",
  "coin-dropping",
  "computer-keyboard",
  "conversation",
  "coo",
  "cough",
  "country",
  "cowbell",
  "crack",
  "crackle",
  "creak",
  "cricket",
  "croak",
  "crow",
  "crowd",
  "crowing-cock-a-doodle-doo",
  "crumpling-crinkling",
  "crunch",
  "crushing",
  "crying-sobbing",
  "cupboard-open-or-close",
  "cutlery-silverware",
  "cymbal",
  "dance-music",
  "dental-drill-dentists-drill",
  "dial-tone",
  "didgeridoo",
  "ding",
  "ding-dong",
  "disco",
  "dishes-pots-and-pans",
  "distortion",
  "dog",
  "domestic-animals-pets",
  "door",
  "doorbell",
  "double-bass",
  "drawer-open-or-close",
  "drill",
  "drip",
  "drum",
  "drum-and-bass",
  "drum-kit",
  "drum-machine",
  "drum-roll",
  "dubstep",
  "duck",
  "echo",
  "effects-unit",
  "electric-guitar",
  "electric-piano",
  "electric-shaver-electric-razor",
  "electric-toothbrush",
  "electronic-dance-music",
  "electronic-music",
  "electronic-organ",
  "electronic-tuner",
  "electronica",
  "emergency-vehicle",
  "engine",
  "engine-knocking",
  "engine-starting",
  "environmental-noise",
  "eruption",
  "exciting-music",
  "explosion",
  "fart",
  "field-recording",
  "filing-rasp",
  "fill-with-liquid",
  "finger-snapping",
  "fire",
  "fire-alarm",
  "fire-engine-fire-truck-siren",
  "firecracker",
  "fireworks",
  "fixed-wing-aircraft-airplane",
  "flamenco",
  "flap",
  "flute",
  "fly-housefly",
  "foghorn",
  "folk-music",
  "fowl",
  "french-horn",
  "frog",
  "frying-food",
  "funk",
  "fusillade",
  "gargling",
  "gasp",
  "gears",
  "giggle",
  "glass",
  "glockenspiel",
  "goat",
  "gobble",
  "gong",
  "goose",
  "gospel-music",
  "groan",
  "growling",
  "grunge",
  "grunt",
  "guitar",
  "gunshot-gunfire",
  "gurgling",
  "gush",
  "hair-dryer",
  "hammer",
  "hammond-organ",
  "hands",
  "happy-music",
  "harmonic",
  "harmonica",
  "harp",
  "harpsichord",
  "heart-murmur",
  "heart-sounds-heartbeat",
  "heavy-engine-low-frequency",
  "heavy-metal",
  "helicopter",
  "hi-hat",
  "hiccup",
  "hip-hop-music",
  "hiss",
  "honk",
  "hoot",
  "horse",
  "house-music",
  "howl",
  "hubbub-speech-noise-speech-babble",
  "hum",
  "humming",
  "ice-cream-truck-ice-cream-van",
  "idling",
  "independent-music",
  "insect",
  "inside-large-room-or-hall",
  "inside-public-space",
  "inside-small-room",
  "jackhammer",
  "jazz",
  "jet-engine",
  "jingle-bell",
  "jingle-music",
  "jingle-tinkle",
  "keyboard-musical",
  "keys-jangling",
  "knock",
  "laughter",
  "lawn-mower",
  "light-engine-high-frequency",
  "liquid",
  "livestock-farm-animals-working-animals",
  "lullaby",
  "machine-gun",
  "mains-hum",
  "mallet-percussion",
  "mandolin",
  "mantra",
  "maraca",
  "marimba-xylophone",
  "mechanical-fan",
  "mechanisms",
  "medium-engine-mid-frequency",
  "meow",
  "microwave-oven",
  "middle-eastern-music",
  "moo",
  "mosquito",
  "motor-vehicle-road",
  "motorboat-speedboat",
  "motorcycle",
  "mouse",
  "music",
  "music-for-children",
  "music-of-africa",
  "music-of-asia",
  "music-of-bollywood",
  "music-of-latin-america",
  "musical-instrument",
  "narration-monologue",
  "neigh-whinny",
  "new-age-music",
  "noise",
  "ocean",
  "oink",
  "opera",
  "orchestra",
  "organ",
  "outside-rural-or-natural",
  "outside-urban-or-manmade",
  "owl",
  "pant",
  "patter",
  "percussion",
  "piano",
  "pig",
  "pigeon-dove",
  "ping",
  "pink-noise",
  "pizzicato",
  "plop",
  "plucked-string-instrument",
  "police-car-siren",
  "pop-music",
  "pour",
  "power-tool",
  "power-windows-electric-windows",
  "printer",
  "progressive-rock",
  "propeller-airscrew",
  "psychedelic-rock",
  "pulleys",
  "pulse",
  "pump-liquid",
  "punk-rock",
  "purr",
  "quack",
  "race-car-auto-racing",
  "radio",
  "rail-transport",
  "railroad-car-train-wagon",
  "rain",
  "rain-on-surface",
  "raindrop",
  "rapping",
  "ratchet-pawl",
  "rattle",
  "rattle-instrument",
  "reggae",
  "reverberation",
  "reversing-beeps",
  "rhythm-and-blues",
  "rimshot",
  "ringtone",
  "roar",
  "roaring-cats-lions-tigers",
  "rock-and-roll",
  "rock-music",
  "rodents-rats-mice",
  "roll",
  "rowboat-canoe-kayak",
  "rub",
  "rumble",
  "run",
  "rustle",
  "rustling-leaves",
  "sad-music",
  "sailboat-sailing-ship",
  "salsa-music",
  "sampler",
  "sanding",
  "sawing",
  "saxophone",
  "scary-music",
  "scissors",
  "scrape",
  "scratch",
  "scratching-performance-technique",
  "screaming",
  "sewing-machine",
  "shatter",
  "sheep",
  "ship",
  "shofar",
  "shout",
  "shuffle",
  "shuffling-cards",
  "sidetone",
  "sigh",
  "silence",
  "sine-wave",
  "singing",
  "singing-bowl",
  "single-lens-reflex-camera",
  "sink-filling-or-washing",
  "siren",
  "sitar",
  "sizzle",
  "ska",
  "skateboard",
  "skidding",
  "slam",
  "slap-smack",
  "sliding-door",
  "slosh",
  "smash-crash",
  "smoke-detector-smoke-alarm",
  "snake",
  "snare-drum",
  "sneeze",
  "snicker",
  "sniff",
  "snoring",
  "snort",
  "sonar",
  "song",
  "soul-music",
  "sound-effect",
  "soundtrack-music",
  "speech",
  "speech-synthesizer",
  "splash-splatter",
  "splinter",
  "spray",
  "squawk",
  "squeak",
  "squeal",
  "squish",
  "static",
  "steam",
  "steam-whistle",
  "steel-guitar-slide-guitar",
  "steelpan",
  "stir",
  "stomach-rumble",
  "stream",
  "string-section",
  "strum",
  "subway-metro-underground",
  "swing-music",
  "synthesizer",
  "synthetic-singing",
  "tabla",
  "tambourine",
  "tap",
  "tapping-guitar-technique",
  "tearing",
  "techno",
  "telephone",
  "telephone-bell-ringing",
  "telephone-dialing-dtmf",
  "television",
  "tender-music",
  "theme-music",
  "theremin",
  "throat-clearing",
  "throbbing",
  "thump-thud",
  "thunder",
  "thunderstorm",
  "thunk",
  "tick",
  "tick-tock",
  "timpani",
  "tire-squeal",
  "toilet-flush",
  "tools",
  "toot",
  "toothbrush",
  "traditional-music",
  "traffic-noise-roadway-noise",
  "train",
  "train-horn",
  "train-wheels-squealing",
  "train-whistle",
  "trance-music",
  "trickle-dribble",
  "trombone",
  "truck",
  "trumpet",
  "tubular-bells",
  "tuning-fork",
  "turkey",
  "typewriter",
  "typing",
  "ukulele",
  "vacuum-cleaner",
  "vehicle",
  "vehicle-horn-car-horn-honking",
  "vibraphone",
  "vibration",
  "video-game-music",
  "violin-fiddle",
  "vocal-music",
  "wail-moan",
  "walk-footsteps",
  "water",
  "water-tap-faucet",
  "waterfall",
  "waves-surf",
  "wedding-music",
  "whack-thwack",
  "whale-vocalization",
  "wheeze",
  "whimper",
  "whimper-dog",
  "whip",
  "whir",
  "whispering",
  "whistle",
  "whistling",
  "white-noise",
  "whoop",
  "whoosh-swoosh-swish",
  "wild-animals",
  "wind",
  "wind-chime",
  "wind-instrument-woodwind-instrument",
  "wind-noise-microphone",
  "wood",
  "wood-block",
  "writing",
  "yell",
  "yip",
  "yodeling",
  "zing",
  "zipper-clothing",
  "zither",
  "💤",
]


async def async_setup_entry(
  hass: HomeAssistant,
  config_entry: OhunerinListenerConfigEntry,
  async_add_entities: AddEntitiesCallback,
) -> None:
  """Set up Oremi Ohunerin Listener sensors from a config entry."""
  topic_prefix = config_entry.runtime_data.topic_prefix

  async_add_entities(
    [
      OhunerinListenerWakewordSensor(hass, topic_prefix, config_entry.entry_id),
      OhunerinListenerSoundSensor(hass, topic_prefix, config_entry.entry_id),
    ]
  )


class OhunerinListenerBaseSensor(SensorEntity):
  """Base sensor for Oremi Ohunerin Listener."""

  _attr_has_entity_name = True
  _attr_icon = "mdi:waveform"
  _attr_device_class = SensorDeviceClass.ENUM

  def __init__(self, hass: HomeAssistant, topic_prefix: str, entry_id: str) -> None:
    """Initialize the base sensor."""
    self.hass = hass
    self._topic_prefix = topic_prefix
    self._entry_id = entry_id
    self._attr_available = False
    self._state: str | None = "💤"
    self._attributes: dict[str, Any] = {}
    self._sub_state = None
    self._sub_availability = None

    self._attr_device_info = DeviceInfo(
      identifiers={(DOMAIN, entry_id)},
      name="Oremi Ohunerin Listener",
      manufacturer="Sébastien Demanou",
      model="Oremi Ohunerin Listener",
      sw_version="2.0.1",
      configuration_url="https://gitlab.com/demsking/oremi-ohunerin-listener",
    )

  @property
  def native_value(self) -> str | None:
    """Return the state of the sensor."""
    return self._state

  @property
  def extra_state_attributes(self) -> dict[str, Any]:
    """Return the state attributes."""
    return self._attributes

  async def async_added_to_hass(self) -> None:
    """Subscribe to MQTT topics."""
    await super().async_added_to_hass()

    @callback
    def message_received(msg: mqtt.ReceiveMessage) -> None:
      """Handle new MQTT messages."""
      try:
        payload = json.loads(msg.payload)
        sound = payload.get("sound")
        if sound == "...":
          self._state = "💤"
          self._attributes = {}
        else:
          self._state = self._process_sound_value(sound)
          self._attributes = {
            "type": payload.get("type"),
            "sound": sound,
            "score": payload.get("score"),
            "date": payload.get("date"),
          }
        self.async_write_ha_state()
      except (json.JSONDecodeError, KeyError) as err:
        _LOGGER.error("Error parsing payload on topic %s: %s", msg.topic, err)

    @callback
    def availability_message_received(msg: mqtt.ReceiveMessage) -> None:
      """Handle availability MQTT messages."""
      self._attr_available = (msg.payload == "online")
      self.async_write_ha_state()

    self._sub_state = await mqtt.async_subscribe(
      self.hass, f"{self._topic_prefix}/{self._topic_type}", message_received
    )
    self._sub_availability = await mqtt.async_subscribe(
      self.hass, f"{self._topic_prefix}/available", availability_message_received
    )

  async def async_will_remove_from_hass(self) -> None:
    """Unsubscribe from MQTT topics."""
    if self._sub_state:
      self._sub_state()
    if self._sub_availability:
      self._sub_availability()
    await super().async_will_remove_from_hass()

  def _process_sound_value(self, sound: str) -> str:
    """Process sound value to fit sensor requirements."""
    raise NotImplementedError


class OhunerinListenerWakewordSensor(OhunerinListenerBaseSensor):
  """Wake word sensor for Oremi Ohunerin Listener."""

  _topic_type = "wakeword"

  def __init__(self, hass: HomeAssistant, topic_prefix: str, entry_id: str) -> None:
    """Initialize the wake word sensor."""
    super().__init__(hass, topic_prefix, entry_id)
    self._attr_name = "Wakeword"
    self._attr_unique_id = f"{entry_id}_wakeword"
    self._attr_options = ["detected", "💤"]

  def _process_sound_value(self, sound: str) -> str:
    """Process sound value for wake word sensor."""
    return "detected"


class OhunerinListenerSoundSensor(OhunerinListenerBaseSensor):
  """Sound detector sensor for Oremi Ohunerin Listener."""

  _topic_type = "sound"

  def __init__(self, hass: HomeAssistant, topic_prefix: str, entry_id: str) -> None:
    """Initialize the sound detector sensor."""
    super().__init__(hass, topic_prefix, entry_id)
    self._attr_name = "Sound Detector"
    self._attr_unique_id = f"{entry_id}_sound"
    self._attr_options = SOUND_OPTIONS

  def _process_sound_value(self, sound: str) -> str:
    """Process sound value for sound detector sensor."""
    if sound in SOUND_OPTIONS:
      return sound
    return sound
