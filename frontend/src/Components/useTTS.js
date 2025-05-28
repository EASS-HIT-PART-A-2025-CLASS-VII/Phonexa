import { useState } from "react";

export function useTTS() {
  const [audio, setAudio] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [phonemeAudio, setPhonemeAudio] = useState(null);
  const [isPhonemeAudioPlaying, setIsPhonemeAudioPlaying] = useState(false);

  const playTextToSpeech = async (text) => {
    if (isPlaying && audio) {
      audio.pause();
      audio.currentTime = 0;
      setIsPlaying(false);
      return;
    }

    try {
      const response = await fetch("http://localhost:8000/tts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sentence: text }),
      });

      if (!response.ok) throw new Error("Failed to fetch TTS audio.");

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      const newAudio = new Audio(audioUrl);
      newAudio.play();
      setAudio(newAudio);
      setIsPlaying(true);

      newAudio.onended = () => setIsPlaying(false);
    } catch (error) {
      console.error("Error playing TTS audio:", error);
    }
  };

  const playPhonemeToSpeech = async (phoneticWord) => {
    // Stop if already playing
    if (isPhonemeAudioPlaying && phonemeAudio) {
      phonemeAudio.pause();
      phonemeAudio.currentTime = 0;
      setIsPhonemeAudioPlaying(false);
      return;
    }
    
    try {
      const response = await fetch("http://localhost:5000/generate-phoneme-audio", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ phonetic_word: phoneticWord }),
      });

      if (!response.ok) throw new Error("Failed to fetch phoneme audio.");

      const blob = await response.blob();
      const audioUrl = URL.createObjectURL(blob);

      const newAudio = new Audio(audioUrl);
      newAudio.play();
      setPhonemeAudio(newAudio);
      setIsPhonemeAudioPlaying(true);

      newAudio.onended = () => setIsPhonemeAudioPlaying(false);
    } catch (error) {
      console.error("Error playing phoneme audio:", error);
    }
  };

  return { playTextToSpeech, isPlaying, playPhonemeToSpeech, isPhonemeAudioPlaying };
}

